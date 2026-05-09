"""Null provider: geen LLM, lege string. Triggert automatisch fallback."""

from __future__ import annotations


class NullProvider:
    name = "null"

    def generate_text(
        self,
        *,
        system: str,
        user: str,
        section: str = "",
        method: str = "",
        length: str = "medium",
    ) -> str:
        return ""
