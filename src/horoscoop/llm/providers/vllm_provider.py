"""vLLM provider via OpenAI-compatible endpoint.

vLLM exposeert een OpenAI-compatibele API:
    POST /v1/chat/completions

We gebruiken een DUMMY API-key (lokaal vereist door OpenAI client-stijl
servers maar niet daadwerkelijk gevalideerd) en geen externe libraries.
"""

from __future__ import annotations

from ._http import post_json


class VllmProvider:
    name = "vllm"

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model: str = "meta-llama/Llama-3-8B-Instruct",
        temperature: float = 0.4,
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    def generate_text(
        self,
        *,
        system: str,
        user: str,
        section: str = "",
        method: str = "",
        length: str = "medium",
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "max_tokens": 512 if length == "short" else (1024 if length == "medium" else 2048),
            "stream": False,
        }
        result = post_json(
            f"{self.base_url}/v1/chat/completions",
            payload,
            timeout=self.timeout_seconds,
        )
        if result is None:
            return ""
        choices = result.get("choices") or []
        if not choices:
            return ""
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if isinstance(content, str):
            return content
        return ""
