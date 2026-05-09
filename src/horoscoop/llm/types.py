"""LLM Service types."""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict


LLM_VERSION = "1.0.0"


LLMProviderName = Literal["null", "ollama", "llamacpp", "vllm", "airllm"]


class LLMConfig(TypedDict, total=False):
    provider: LLMProviderName
    baseUrl: str
    model: str
    temperature: float
    maxTokens: int
    topP: float
    timeoutSeconds: int


class LLMService(Protocol):
    """Common contract for any local LLM provider.

    Implementations must:
        - Accept a system message and a user message.
        - Never call out to paid third-party APIs.
        - Return the model output as a Python string (or empty string on failure).
    """

    def generate_text(
        self,
        *,
        system: str,
        user: str,
        section: str = "",
        method: str = "",
        length: str = "medium",
    ) -> str:
        ...
