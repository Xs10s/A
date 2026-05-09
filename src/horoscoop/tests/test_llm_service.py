from __future__ import annotations

from horoscoop.llm import (
    AirLLMProvider,
    LlamaCppProvider,
    NullProvider,
    OllamaProvider,
    VllmProvider,
    create_llm_service,
)


def test_default_factory_returns_null_provider():
    svc = create_llm_service()
    assert isinstance(svc, NullProvider)
    assert svc.generate_text(system="x", user="y") == ""


def test_factory_creates_ollama_provider():
    svc = create_llm_service({"provider": "ollama", "baseUrl": "http://localhost:11434", "model": "llama3.1"})
    assert isinstance(svc, OllamaProvider)


def test_factory_creates_llamacpp_provider():
    svc = create_llm_service({"provider": "llamacpp"})
    assert isinstance(svc, LlamaCppProvider)


def test_factory_creates_vllm_provider():
    svc = create_llm_service({"provider": "vllm"})
    assert isinstance(svc, VllmProvider)


def test_factory_creates_airllm_provider():
    svc = create_llm_service({"provider": "airllm"})
    assert isinstance(svc, AirLLMProvider)


def test_unknown_provider_falls_back_to_null():
    svc = create_llm_service({"provider": "unknown"})
    assert isinstance(svc, NullProvider)


def test_ollama_provider_returns_empty_when_unreachable():
    svc = OllamaProvider(base_url="http://127.0.0.1:1", timeout_seconds=1)
    assert svc.generate_text(system="x", user="y") == ""


def test_llamacpp_provider_returns_empty_when_unreachable():
    svc = LlamaCppProvider(base_url="http://127.0.0.1:1", timeout_seconds=1)
    assert svc.generate_text(system="x", user="y") == ""


def test_vllm_provider_returns_empty_when_unreachable():
    svc = VllmProvider(base_url="http://127.0.0.1:1", timeout_seconds=1)
    assert svc.generate_text(system="x", user="y") == ""


def test_airllm_provider_returns_empty_when_dependency_missing():
    svc = AirLLMProvider()
    assert svc.generate_text(system="x", user="y") == ""
