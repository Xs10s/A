"""Factory voor LLMService instances."""

from __future__ import annotations

from .providers.airllm_provider import AirLLMProvider
from .providers.llamacpp_provider import LlamaCppProvider
from .providers.null_provider import NullProvider
from .providers.ollama_provider import OllamaProvider
from .providers.vllm_provider import VllmProvider
from .types import LLMConfig, LLMService


def create_llm_service(config: LLMConfig | None = None) -> LLMService:
    """Maak een `LLMService` op basis van config.

    Defaults naar NullProvider zodat de app altijd zonder LLM bruikbaar
    blijft. Een config zonder of met onbekende provider levert ook
    NullProvider.
    """
    if config is None:
        return NullProvider()
    provider = (config.get("provider") or "null").lower()
    if provider == "ollama":
        return OllamaProvider(
            base_url=config.get("baseUrl", "http://localhost:11434"),
            model=config.get("model", "llama3.1"),
            temperature=float(config.get("temperature", 0.4)),
            timeout_seconds=int(config.get("timeoutSeconds", 60)),
        )
    if provider == "llamacpp":
        return LlamaCppProvider(
            base_url=config.get("baseUrl", "http://localhost:8080"),
            model=config.get("model", ""),
            temperature=float(config.get("temperature", 0.4)),
            timeout_seconds=int(config.get("timeoutSeconds", 60)),
        )
    if provider == "vllm":
        return VllmProvider(
            base_url=config.get("baseUrl", "http://localhost:8000"),
            model=config.get("model", "meta-llama/Llama-3-8B-Instruct"),
            temperature=float(config.get("temperature", 0.4)),
            timeout_seconds=int(config.get("timeoutSeconds", 60)),
        )
    if provider == "airllm":
        return AirLLMProvider(
            model=config.get("model", "garage-bAInd/Platypus2-7B"),
            temperature=float(config.get("temperature", 0.4)),
        )
    return NullProvider()
