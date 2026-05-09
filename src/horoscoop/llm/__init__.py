"""
LLM Service Layer
=================

Abstracte interface voor self-hosted LLMs. GEEN betaalde externe APIs.

Providers (allen optioneel; afhankelijk van wat er lokaal draait):
    - OllamaProvider     (HTTP /api/generate of /api/chat)
    - LlamaCppProvider   (HTTP server met /completion)
    - VllmProvider       (HTTP /v1/chat/completions, OpenAI-compatibel)
    - AirLLMProvider     (in-process; placeholder, optionele dependency)
    - NullProvider       (geen LLM, alleen fallback)

Het hoofdcontract is het `LLMService` Protocol; iedere provider levert
de methode `generate_text(...)` terug.

Belangrijk: deze laag voert NIETS astrologisch uit. Hij ontvangt een
gecontroleerde prompt vanuit de Narrative Generation Layer.
"""

from __future__ import annotations

from .types import (
    LLM_VERSION,
    LLMConfig,
    LLMProviderName,
    LLMService,
)
from .service import (
    create_llm_service,
)
from .providers.null_provider import NullProvider
from .providers.ollama_provider import OllamaProvider
from .providers.llamacpp_provider import LlamaCppProvider
from .providers.vllm_provider import VllmProvider
from .providers.airllm_provider import AirLLMProvider

__all__ = [
    "LLM_VERSION",
    "LLMConfig",
    "LLMProviderName",
    "LLMService",
    "NullProvider",
    "OllamaProvider",
    "LlamaCppProvider",
    "VllmProvider",
    "AirLLMProvider",
    "create_llm_service",
]
