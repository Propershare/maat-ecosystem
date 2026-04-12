"""
MAAT Ollama Model Adapter

Swap this for openai.py, vllm.py, or anthropic.py
without touching the kernel.
"""

from __future__ import annotations

import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from maat_adapters.base import ModelAdapter


class OllamaAdapter(ModelAdapter):

    def __init__(self, config: dict):
        super().__init__(config)
        self._host = config.get("host", "http://localhost:11434")
        self._model = config.get("model", "gemma4:e4b")
        self._embed_model = config.get("embed_model", "nomic-embed-text")

    @property
    def model_name(self) -> str:
        return f"ollama/{self._model}"

    def generate(self, messages: list[dict], system: str = "", **kwargs) -> str:
        if system:
            messages = [{"role": "system", "content": system}] + messages

        payload = json.dumps({
            "model": self._model,
            "messages": messages,
            "stream": False,
        }).encode()

        req = Request(
            f"{self._host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data.get("message", {}).get("content", "")
        except (URLError, Exception) as e:
            print(f"[ollama] generate error: {e}")
            return ""

    def embed(self, text: str) -> list[float]:
        payload = json.dumps({"model": self._embed_model, "prompt": text}).encode()
        req = Request(
            f"{self._host}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read()).get("embedding", [])
        except Exception as e:
            print(f"[ollama] embed error: {e}")
            return []
