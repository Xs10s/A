"""Ollama provider.

Gebruikt de standaard Ollama HTTP API. Verwacht een lokale server op
`http://localhost:11434`. Geen authenticatie nodig.

Endpoint: `/api/chat` (modern) of `/api/generate` (fallback).
"""

from __future__ import annotations

from ._http import post_json


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.1",
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
            "stream": False,
            "options": {"temperature": self.temperature},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        result = post_json(f"{self.base_url}/api/chat", payload, timeout=self.timeout_seconds)
        if result is None:
            return ""
        message = result.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        return str(result.get("response", ""))
