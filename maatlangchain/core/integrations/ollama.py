"""
Ollama LLM Client Wrapper
Shared infrastructure for LLM access
Maat: Balance - Efficient model usage
"""

import logging
import requests
from typing import Optional, Dict, Any, Iterator
import json

from config.shared_config import get_shared_config

log = logging.getLogger(__name__)


class OllamaClient:
    """Ollama LLM client with connection pooling and error handling."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        config = get_shared_config()
        self.base_url = base_url or config.ollama_base_url
        self.default_model = default_model or config.ollama_default_model
        self.timeout = timeout or config.ollama_timeout
        self.session = requests.Session()
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt
            model: Model name (defaults to configured model)
            stream: Whether to stream response
            **kwargs: Additional parameters (temperature, top_p, etc.)
        
        Returns:
            Response dictionary with 'response' and 'metadata'
        """
        model = model or self.default_model
        
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs,
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                stream=stream,
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                data = response.json()
                return {
                    "response": data.get("response", ""),
                    "metadata": {
                        "model": model,
                        "done": data.get("done", True),
                        "context": data.get("context", []),
                        "total_duration": data.get("total_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "eval_count": data.get("eval_count", 0),
                    },
                }
        
        except requests.exceptions.RequestException as e:
            log.error(f"Ollama API request failed: {e}")
            raise
    
    def _handle_stream_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Handle streaming response from Ollama."""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield {
                        "response": data.get("response", ""),
                        "done": data.get("done", False),
                        "metadata": {
                            "model": data.get("model", ""),
                            "total_duration": data.get("total_duration", 0),
                        },
                    }
                except json.JSONDecodeError:
                    continue
    
    def chat(
        self,
        messages: list,
        model: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Chat completion using Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to configured model)
            stream: Whether to stream response
            **kwargs: Additional parameters
        
        Returns:
            Response dictionary
        """
        model = model or self.default_model
        
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }
        
        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                stream=stream,
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                data = response.json()
                return {
                    "response": data.get("message", {}).get("content", ""),
                    "metadata": {
                        "model": model,
                        "done": data.get("done", True),
                        "total_duration": data.get("total_duration", 0),
                    },
                }
        
        except requests.exceptions.RequestException as e:
            log.error(f"Ollama chat API request failed: {e}")
            raise
    
    def list_models(self) -> list:
        """List available Ollama models."""
        url = f"{self.base_url}/api/tags"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model.get("name", "") for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to list Ollama models: {e}")
            return []
    
    def health_check(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200
        except Exception:
            return False


# Global client instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
        log.info("Ollama client initialized")
    return _ollama_client

