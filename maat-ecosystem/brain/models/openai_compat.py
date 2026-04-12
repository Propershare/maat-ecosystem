"""
MAAT OpenAI-Compatible Model Adapter

Works with any OpenAI-compatible API:
- OpenAI
- Together.ai
- Groq
- LM Studio
- vLLM
- Anyscale
"""

from __future__ import annotations

import json
from urllib.request import Request, urlopen
from maat_adapters.base import ModelAdapter


class OpenAICompatAdapter(ModelAdapter):

    def __init__(self, config: dict):
        super().__init__(config)
        self._base_url = config.get("base_url", "https://api.openai.com/v1")
        self._api_key = config.get("api_key", "")
        self._model = config.get("model", "gpt-4o-mini")
        self._embed_model = config.get("embed_model", "text-embedding-3-small")

    @property
    def model_name(self) -> str:
        return f"openai-compat/{self._model}"

    def generate(self, messages: list[dict], system: str = "", **kwargs) -> str:
        if system:
            messages = [{"role": "system", "content": system}] + messages

        payload = json.dumps({
            "model": self._model,
            "messages": messages,
        }).encode()

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        req = Request(
            f"{self._base_url}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[openai-compat] generate error: {e}")
            return ""

    def embed(self, text: str) -> list[float]:
        payload = json.dumps({"model": self._embed_model, "input": text}).encode()
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        req = Request(f"{self._base_url}/embeddings", data=payload, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())["data"][0]["embedding"]
        except Exception as e:
            print(f"[openai-compat] embed error: {e}")
            return []
