"""
Gemma4 Tool-Call Shim Proxy v3

Sits between OpenCode (or any OpenAI-compatible client) and Ollama.
Intercepts gemma4's thinking field where it plans tool calls,
extracts the intent, and converts to proper tool_calls format.

Handles both streaming and non-streaming requests.
For streaming: collects full response, extracts tool calls, then re-streams.

v3 additions:
  - Training data capture (JSONL) with thread safety
  - /health endpoint
  - Better error handling for malformed responses
  - Multi-turn conversation support (tool results)
  - threading.Lock for JSONL writer
"""

import json
import re
import uuid
import logging
import os
import time
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

# Config
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
SHIM_PORT = int(os.environ.get("SHIM_PORT", "11435"))
LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
TRAINING_DATA_DIR = os.environ.get(
    "TRAINING_DATA_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_data")
)
CAPTURES_FILE = os.path.join(TRAINING_DATA_DIR, "captures.jsonl")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("gemma4-shim")

# Thread-safe training data writer
_capture_lock = threading.Lock()
_stats = {"requests": 0, "shims": 0, "captures": 0, "errors": 0}
_stats_lock = threading.Lock()


def _ensure_training_dir():
    os.makedirs(TRAINING_DATA_DIR, exist_ok=True)


def _record_stats(key: str, delta: int = 1):
    with _stats_lock:
        _stats[key] = _stats.get(key, 0) + delta


def save_training_capture(request_data: dict, corrected_message: dict, source: str):
    """
    Save a training capture to the JSONL file.
    Thread-safe via _capture_lock.

    Format: each line is a JSON object with:
      - timestamp
      - source: "thinking" | "content" | "native"
      - messages: the conversation so far
      - tools: the tool schemas
      - response: corrected assistant message with proper tool_calls
    """
    _ensure_training_dir()
    capture = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "messages": request_data.get("messages", []),
        "tools": request_data.get("tools", []),
        "response": corrected_message,
    }
    line = json.dumps(capture, ensure_ascii=False) + "\n"
    with _capture_lock:
        try:
            with open(CAPTURES_FILE, "a", encoding="utf-8") as f:
                f.write(line)
            _record_stats("captures")
            log.debug(f"Captured training example to {CAPTURES_FILE}")
        except OSError as e:
            log.error(f"Failed to write training capture: {e}")


# ---------------------------------------------------------------------------
# Tool name helpers
# ---------------------------------------------------------------------------

def _normalize_name(name: str) -> str:
    """Normalize tool name for fuzzy matching (collapse - and _ and lower)."""
    return re.sub(r'[-_\s]+', '_', name).lower()


def _build_tool_map(available_tools: list) -> tuple:
    """
    Build exact and normalized tool maps.
    Returns (exact_map, norm_to_exact) where:
      exact_map[exact_name] = parameters_schema
      norm_to_exact[normalized_name] = exact_name
    """
    exact_map = {}
    norm_to_exact = {}
    for tool in available_tools:
        if not isinstance(tool, dict):
            continue
        func = tool.get("function", {})
        name = func.get("name", "")
        if name:
            exact_map[name] = func.get("parameters", {})
            norm_to_exact[_normalize_name(name)] = name
    return exact_map, norm_to_exact


def _resolve_tool_name(mentioned: str, norm_to_exact: dict) -> str | None:
    """Resolve a tool name mentioned in thinking to an exact tool name."""
    if not mentioned:
        return None
    # Exact match
    if mentioned in norm_to_exact.values():
        return mentioned
    # Normalized match
    normed = _normalize_name(mentioned)
    if normed in norm_to_exact:
        return norm_to_exact[normed]
    # Partial match (e.g. 'write_file' matches 'tehuti-core_write_file')
    for norm, exact in norm_to_exact.items():
        if normed in norm or norm.endswith(normed):
            return exact
    return None


# ---------------------------------------------------------------------------
# Tool call extraction
# ---------------------------------------------------------------------------

def extract_tool_calls_from_thinking(thinking: str, available_tools: list) -> list:
    """
    Parse gemma4's thinking to extract intended tool calls.
    Returns a list of tool_call dicts.
    """
    if not thinking or not available_tools:
        return []

    tool_map, norm_to_exact = _build_tool_map(available_tools)
    if not tool_map:
        return []

    tool_calls = []

    # Strategy 0: Find ANY tool name mentions (exact or fuzzy) in thinking
    mentioned_tools = []
    candidates = re.findall(r'`([\w.:-]+)`', thinking)
    candidates += re.findall(
        r'(?:use|call|invoke|tool)\s+(?:the\s+)?[`"\']?([\w.:-]+)',
        thinking, re.IGNORECASE
    )
    for cand in candidates:
        resolved = _resolve_tool_name(cand, norm_to_exact)
        if resolved and resolved not in mentioned_tools:
            mentioned_tools.append(resolved)

    if not mentioned_tools:
        mentioned_tools = list(tool_map.keys())

    log.info(f"Mentioned tools in thinking: {mentioned_tools}")

    # Strategy 1: Explicit function call pattern
    for tool_name in mentioned_tools:
        if tool_name not in tool_map:
            continue
        pattern = rf'{re.escape(tool_name)}\s*\(\s*(.*?)\s*\)'
        matches = re.finditer(pattern, thinking, re.DOTALL)
        for match in matches:
            args = _parse_function_args(match.group(1), tool_map[tool_name])
            if args:
                tool_calls.append(_make_tool_call(tool_name, args))

    if tool_calls:
        return tool_calls

    # Strategy 2: JSON structures near tool name
    for tool_name in mentioned_tools:
        if tool_name not in tool_map:
            continue
        if tool_name in thinking:
            json_pattern = r'\{[^{}]*"(?:path|content|command|file_path)"[^{}]*\}'
            for jm in re.finditer(json_pattern, thinking, re.DOTALL):
                try:
                    args = json.loads(jm.group())
                    props = tool_map[tool_name].get("properties", {})
                    if any(k in props for k in args):
                        tool_calls.append(_make_tool_call(tool_name, args))
                        break
                except (json.JSONDecodeError, ValueError):
                    continue

    if tool_calls:
        return tool_calls

    # Strategy 3: Natural language parameter extraction
    for tool_name in mentioned_tools:
        if tool_name not in tool_map:
            continue
        props = tool_map[tool_name].get("properties", {})
        args = {}

        for prop_name in props:
            patterns = [
                rf'{re.escape(prop_name)}\s*=\s*"((?:[^"\\]|\\.)*)"',
                rf'{re.escape(prop_name)}\s*=\s*\'((?:[^\'\\]|\\.)*?)\'',
                rf'{re.escape(prop_name)}\s*:\s*"((?:[^"\\]|\\.)*)"',
                rf'"{re.escape(prop_name)}"\s*:\s*"((?:[^"\\]|\\.)*)"',
            ]
            for p in patterns:
                m = re.search(p, thinking, re.DOTALL)
                if m:
                    args[prop_name] = m.group(1)
                    break

        required = tool_map[tool_name].get("required", [])
        if required and all(r in args for r in required):
            tool_calls.append(_make_tool_call(tool_name, args))

    if tool_calls:
        return tool_calls

    # Strategy 4: Code blocks as tool content
    for tool_name in mentioned_tools:
        if tool_name not in tool_map:
            continue
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', thinking, re.DOTALL)
        if code_blocks and "content" in tool_map[tool_name].get("properties", {}):
            path_match = re.search(
                r'(?:path|file|filename)\s*[=:]\s*["\']?(\S+\.(?:py|js|ts|sh|md|txt|json|yaml|yml))',
                thinking
            )
            if path_match:
                tool_calls.append(_make_tool_call(tool_name, {
                    "path": path_match.group(1).strip("\"'"),
                    "content": code_blocks[0]
                }))

    if tool_calls:
        return tool_calls

    # Strategy 5: Natural language plan with file paths + inline content
    for tool_name in mentioned_tools:
        if tool_name not in tool_map:
            continue
        props = tool_map[tool_name].get('properties', {})
        path_matches = re.findall(
            r'[`"\']([\w./:-]+\.(?:py|js|ts|sh|md|txt|json|yaml|yml|html|css|toml|cfg|ini))[`"\']',
            thinking
        )
        inline_code = re.findall(r'`([^`]+\([^`]*\)[^`]*)`', thinking)
        quoted_content = re.findall(r'[Cc]ontent[:\s]+`([^`]+)`', thinking)

        content = None
        if inline_code:
            content = inline_code[0]
        elif quoted_content:
            content = quoted_content[0]

        if path_matches and content and ('content' in props or 'text' in props):
            path_key = next((k for k in ('path', 'file_path', 'filePath') if k in props), 'path')
            content_key = 'content' if 'content' in props else 'text'
            args = {path_key: path_matches[0], content_key: content}
            tool_calls.append(_make_tool_call(tool_name, args))
            log.info(f"Strategy 5a matched: {tool_name} from NL plan")
            break

    if tool_calls:
        return tool_calls

    # Strategy 6: Simple pattern - file path + code block (common with gemma4)
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', thinking, re.DOTALL)
    path_matches = re.findall(
        r'[`"\']([\w./:-]+\.(?:py|js|ts|sh|md|txt|json|yaml|yml|html|css|toml|cfg|ini))[`"\']',
        thinking
    )

    if code_blocks and path_matches:
        write_tool = None
        for tn in mentioned_tools:
            if 'write' in tn.lower():
                write_tool = tn
                break
        if not write_tool:
            for tn in tool_map:
                props = tool_map[tn].get('properties', {})
                if ('path' in props or 'file_path' in props or 'filePath' in props) and 'content' in props:
                    write_tool = tn
                    break

        if write_tool:
            props = tool_map[write_tool].get('properties', {})
            path_key = 'path' if 'path' in props else ('file_path' if 'file_path' in props else 'filePath')
            content_key = 'content' if 'content' in props else 'text'
            args = {path_key: path_matches[0], content_key: code_blocks[0]}
            tool_calls.append(_make_tool_call(write_tool, args))
            log.info(f"Strategy 6 matched: {write_tool} with path={path_matches[0]}")

    return tool_calls


def _make_tool_call(name: str, args: dict) -> dict:
    return {
        "id": f"call_{uuid.uuid4().hex[:12]}",
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps(args, ensure_ascii=False)
        }
    }


def _parse_function_args(args_str: str, schema: dict) -> dict:
    args = {}
    pattern = r'(\w+)\s*=\s*(?:"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'|(\S+))'
    for m in re.finditer(pattern, args_str, re.DOTALL):
        key = m.group(1)
        value = (
            m.group(2) if m.group(2) is not None
            else (m.group(3) if m.group(3) is not None else m.group(4))
        )
        args[key] = value
    return args


# ---------------------------------------------------------------------------
# Conversation helpers
# ---------------------------------------------------------------------------

def _has_tool_results(messages: list) -> bool:
    """Check if the conversation contains tool result messages."""
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "tool":
            return True
    return False


def _sanitize_messages(messages: list) -> list:
    """
    Sanitize messages for multi-turn tool conversations.
    Ensures tool result messages have the required fields.
    """
    sanitized = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        if role == "tool":
            # Ensure tool_call_id is present
            if "tool_call_id" not in msg:
                msg = dict(msg)
                msg["tool_call_id"] = f"call_{uuid.uuid4().hex[:12]}"
            # Ensure content is a string
            content = msg.get("content", "")
            if not isinstance(content, str):
                msg = dict(msg)
                msg["content"] = json.dumps(content)
        sanitized.append(msg)
    return sanitized


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

class ShimHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.debug(format % args)

    def do_POST(self):
        _record_stats("requests")
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            body = self.rfile.read(content_length)
        except OSError as e:
            log.error(f"Failed to read request body: {e}")
            self.send_error(400, "Failed to read request body")
            return

        is_chat = self.path in ('/v1/chat/completions', '/api/chat')
        if is_chat:
            self._handle_chat(body)
        else:
            self._proxy(body)

    def do_GET(self):
        if self.path == '/health':
            self._handle_health()
        else:
            self._proxy(b'')

    def _handle_health(self):
        """Health check endpoint."""
        with _stats_lock:
            stats_copy = dict(_stats)
        payload = {
            "status": "ok",
            "version": "3",
            "shim_port": SHIM_PORT,
            "ollama_base": OLLAMA_BASE,
            "captures_file": CAPTURES_FILE,
            "stats": stats_copy,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Check Ollama connectivity
        try:
            req = Request(f"{OLLAMA_BASE}/api/tags", method="GET")
            with urlopen(req, timeout=3) as resp:
                payload["ollama_status"] = "reachable"
        except Exception as e:
            payload["ollama_status"] = f"unreachable: {e}"

        self._send_json(payload)

    def _proxy(self, body):
        url = f"{OLLAMA_BASE}{self.path}"
        try:
            req = Request(url, data=body if body else None, method=self.command)
            for key, val in self.headers.items():
                if key.lower() not in ('host', 'content-length'):
                    req.add_header(key, val)
            if body:
                req.add_header('Content-Length', str(len(body)))

            with urlopen(req, timeout=300) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for key, val in resp.getheaders():
                    if key.lower() != 'transfer-encoding':
                        self.send_header(key, val)
                self.end_headers()
                self.wfile.write(resp_body)
        except URLError as e:
            log.error(f"Proxy error: {e}")
            _record_stats("errors")
            self.send_error(502, str(e))
        except Exception as e:
            log.error(f"Unexpected proxy error: {e}", exc_info=True)
            _record_stats("errors")
            self.send_error(500, str(e))

    def _handle_chat(self, body):
        # Parse request
        try:
            request_data = json.loads(body)
        except (json.JSONDecodeError, ValueError) as e:
            log.warning(f"Malformed JSON request: {e}")
            self.send_error(400, f"Malformed JSON: {e}")
            return

        if not isinstance(request_data, dict):
            log.warning("Request body is not a JSON object")
            self.send_error(400, "Request body must be a JSON object")
            return

        tools = request_data.get("tools", [])
        if not isinstance(tools, list):
            tools = []
            request_data["tools"] = tools

        is_streaming = request_data.get("stream", True)
        is_openai = self.path == '/v1/chat/completions'

        # Sanitize messages for multi-turn tool conversations
        messages = request_data.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        request_data["messages"] = _sanitize_messages(messages)

        has_tool_results = _has_tool_results(request_data["messages"])
        if has_tool_results:
            log.info("Multi-turn: conversation contains tool results")

        if not tools:
            self._proxy(body)
            return

        log.info(
            f"Shimming: model={request_data.get('model', '?')}, "
            f"stream={is_streaming}, openai={is_openai}, "
            f"multi_turn={has_tool_results}, "
            f"tools={[t.get('function', {}).get('name', '') for t in tools if isinstance(t, dict)]}"
        )

        # Force non-streaming to Ollama so we can intercept the full response
        request_data["stream"] = False
        modified_body = json.dumps(request_data, ensure_ascii=False).encode()

        ollama_url = f"{OLLAMA_BASE}/api/chat"
        try:
            req = Request(ollama_url, data=modified_body, method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Content-Length', str(len(modified_body)))

            with urlopen(req, timeout=300) as resp:
                resp_body = resp.read()
        except URLError as e:
            log.error(f"Ollama request failed: {e}")
            _record_stats("errors")
            self.send_error(502, f"Ollama unreachable: {e}")
            return
        except Exception as e:
            log.error(f"Ollama request error: {e}", exc_info=True)
            _record_stats("errors")
            self.send_error(500, str(e))
            return

        # Parse Ollama response
        try:
            resp_data = json.loads(resp_body)
        except (json.JSONDecodeError, ValueError) as e:
            log.error(f"Malformed response from Ollama: {e}")
            log.error(f"Raw response (first 500): {resp_body[:500]}")
            _record_stats("errors")
            self.send_error(502, f"Ollama returned malformed JSON: {e}")
            return

        if not isinstance(resp_data, dict):
            log.error("Ollama response is not a JSON object")
            _record_stats("errors")
            self.send_error(502, "Ollama returned unexpected response format")
            return

        message = resp_data.get("message", {})
        if not isinstance(message, dict):
            log.warning(f"Unexpected message type: {type(message)}")
            message = {}
            resp_data["message"] = message

        existing_calls = message.get("tool_calls", [])
        capture_source = None

        if not existing_calls:
            thinking = message.get("thinking", "") or ""
            content = message.get("content", "") or ""
            source = thinking or content

            if source:
                try:
                    extracted = extract_tool_calls_from_thinking(source, tools)
                except Exception as e:
                    log.error(f"Tool extraction error: {e}", exc_info=True)
                    extracted = []

                if extracted:
                    log.info(f"Extracted {len(extracted)} tool call(s)")
                    for tc in extracted:
                        fn = tc.get("function", {})
                        log.info(f"  -> {fn.get('name')}: {str(fn.get('arguments', ''))[:100]}...")
                    message["tool_calls"] = extracted
                    message["content"] = ""
                    resp_data["message"] = message
                    capture_source = "thinking" if thinking else "content"
                    _record_stats("shims")
                else:
                    log.warning("Could not extract tool calls from thinking")
                    log.warning(f"Source (first 500): {source[:500]}")
            else:
                log.warning("No thinking/content to extract from")
        else:
            log.info(f"Native tool calls: {len(existing_calls)}")
            _, nte = _build_tool_map(tools)
            for tc in existing_calls:
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function", {})
                raw_name = fn.get("name", "")
                log.info(f"  Native -> {raw_name}: {str(fn.get('arguments', ''))[:200]}")
                resolved = _resolve_tool_name(raw_name, nte)
                if resolved and resolved != raw_name:
                    log.info(f"  Fixed name: {raw_name} -> {resolved}")
                    fn["name"] = resolved
            resp_data["message"] = message
            capture_source = "native"

        # Save training capture if we did any shimming or saw native calls
        if capture_source:
            try:
                save_training_capture(request_data, message, capture_source)
            except Exception as e:
                log.error(f"Training capture failed (non-fatal): {e}")

        # Format response based on what the client expects
        if is_openai:
            try:
                openai_resp = self._to_openai_format(resp_data, request_data.get("model", "gemma4:e4b"))
            except Exception as e:
                log.error(f"OpenAI format conversion failed: {e}", exc_info=True)
                _record_stats("errors")
                self.send_error(500, f"Response format error: {e}")
                return

            if is_streaming:
                self._send_as_sse(openai_resp)
            else:
                self._send_json(openai_resp)
        else:
            self._send_json(resp_data)

    def _to_openai_format(self, ollama_resp: dict, model: str) -> dict:
        """Convert Ollama response to OpenAI chat completion format."""
        message = ollama_resp.get("message", {})
        tool_calls = message.get("tool_calls", [])
        content = message.get("content", "") or ""

        choice_message = {"role": "assistant", "content": content or None}

        if tool_calls:
            oai_tool_calls = []
            for i, tc in enumerate(tool_calls):
                if not isinstance(tc, dict):
                    continue
                fn = tc.get("function", {})
                args = fn.get("arguments", "{}")
                if not isinstance(args, str):
                    args = json.dumps(args, ensure_ascii=False)
                oai_tool_calls.append({
                    "id": tc.get("id", f"call_{uuid.uuid4().hex[:12]}"),
                    "type": "function",
                    "index": i,
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": args
                    }
                })
            choice_message["tool_calls"] = oai_tool_calls
            finish_reason = "tool_calls"
        else:
            finish_reason = "stop"

        tokens = ollama_resp.get("prompt_eval_count", 0) or 0
        eval_count = ollama_resp.get("eval_count", 0) or 0

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": choice_message,
                "finish_reason": finish_reason
            }],
            "usage": {
                "prompt_tokens": tokens,
                "completion_tokens": eval_count,
                "total_tokens": tokens + eval_count
            }
        }

    def _send_as_sse(self, openai_resp: dict):
        """Send an OpenAI response as a single SSE stream."""
        model = openai_resp.get("model", "gemma4:e4b")
        resp_id = openai_resp.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}")
        created = openai_resp.get("created", int(time.time()))
        choice = openai_resp.get("choices", [{}])[0]
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "stop")
        chunks = []

        tool_calls = message.get("tool_calls", [])
        if tool_calls:
            for tc in tool_calls:
                chunk = {
                    "id": resp_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "tool_calls": [tc]},
                        "finish_reason": None
                    }]
                }
                chunks.append(chunk)
        elif message.get("content"):
            chunk = {
                "id": resp_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{
                    "index": 0,
                    "delta": {"role": "assistant", "content": message["content"]},
                    "finish_reason": None
                }]
            }
            chunks.append(chunk)

        final = {
            "id": resp_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}],
            "usage": openai_resp.get("usage", {})
        }
        chunks.append(final)

        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            for chunk in chunks:
                line = f"data: {json.dumps(chunk)}\n\n"
                self.wfile.write(line.encode())
                self.wfile.flush()

            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except BrokenPipeError:
            log.debug("Client disconnected during SSE stream")
        except OSError as e:
            log.warning(f"SSE write error: {e}")

    def _send_json(self, data):
        try:
            body = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:
            log.debug("Client disconnected before response sent")
        except OSError as e:
            log.warning(f"JSON send error: {e}")


def main():
    _ensure_training_dir()
    log.info(f"Gemma4 Tool-Call Shim v3 starting on port {SHIM_PORT}")
    log.info(f"Proxying to Ollama at {OLLAMA_BASE}")
    log.info(f"Training captures: {CAPTURES_FILE}")
    log.info("All tool-bearing requests shimmed (streaming + non-streaming)")

    server = HTTPServer(('127.0.0.1', SHIM_PORT), ShimHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
