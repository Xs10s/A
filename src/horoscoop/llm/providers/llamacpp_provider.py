"""llama.cpp HTTP server provider.

Werkt met de in `llama-server` ingebouwde HTTP API:
    POST /completion  { "prompt": "...", "n_predict": ... }

Gebruikt geen authenticatie en geen externe libraries.
"""

from __future__ import annotations

from ._http import post_json


class LlamaCppProvider:
    name = "llamacpp"

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        model: str = "",
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
        prompt = f"<<SYS>>\n{system}\n<</SYS>>\n\n{user}\n"
        payload = {
            "prompt": prompt,
            "temperature": self.temperature,
            "n_predict": 512 if length == "short" else (1024 if length == "medium" else 2048),
            "stream": False,
        }
        result = post_json(f"{self.base_url}/completion", payload, timeout=self.timeout_seconds)
        if result is None:
            return ""
        if isinstance(result.get("content"), str):
            return result["content"]
        if isinstance(result.get("response"), str):
            return result["response"]
        return ""
