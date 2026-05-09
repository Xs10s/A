"""Narrative generator: vertaalbrug naar de LLM service.

Deze module is bewust dun. Hij:
- bouwt een controlled prompt via `prompts.build_prompt`
- stuurt die naar een `LLMService`
- valt automatisch terug op de fallback-template als de LLM faalt
  of niet beschikbaar is

De LLM krijgt NOOIT directe toegang tot ruwe berekeningen of glossary-
mutaties. Alle context komt via de Interpretation Builder.
"""

from __future__ import annotations

from typing import Any

from .fallback import build_fallback_narrative, render_point_fallback
from .prompts import build_prompt
from .types import (
    EnergyProfileNarrative,
    NarrativeRequest,
    NarrativeSection,
    SynthesisPoint,
)


def generate_section_with_llm(
    request: NarrativeRequest,
    llm_service: Any | None,
) -> NarrativeSection:
    """Vraag de LLM-service om \u00e9\u00e9n narrative section.

    Bij ontbrekende of falende LLM valt de functie terug op een
    deterministische fallback-tekst opgebouwd uit de interpretatiepunten.
    """
    points = list(request.get("interpretationPoints") or [])
    fallback_text = "\n\n".join(render_point_fallback(p) for p in points if p)

    if llm_service is None:
        return _fallback_section(request, fallback_text)

    prompt = build_prompt(request)
    try:
        text = llm_service.generate_text(
            system=prompt["system"],
            user=prompt["user"],
            section=request.get("section", "section"),
            method=request.get("method", "energy-profile"),
            length=request.get("length", "medium"),
        )
        if not isinstance(text, str) or not text.strip():
            return _fallback_section(request, fallback_text)
        return {
            "section": request.get("section", "section"),
            "method": request.get("method", "energy-profile"),
            "text": text.strip(),
            "bulletPoints": [p.get("technicalLabel", "") for p in points],
            "reflectionQuestions": _collect_reflections(points),
            "sources": _collect_sources(points),
            "style": request.get("tone", "warm"),
            "generator": "llm",
        }
    except Exception:
        return _fallback_section(request, fallback_text)


def _fallback_section(request: NarrativeRequest, fallback_text: str) -> NarrativeSection:
    points = list(request.get("interpretationPoints") or [])
    return {
        "section": request.get("section", "section"),
        "method": request.get("method", "energy-profile"),
        "text": fallback_text,
        "bulletPoints": [p.get("technicalLabel", "") for p in points],
        "reflectionQuestions": _collect_reflections(points),
        "sources": _collect_sources(points),
        "style": request.get("tone", "warm"),
        "generator": "fallback",
    }


def _collect_reflections(points: list) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for p in points:
        for q in p.get("reflectionQuestions") or []:
            if q not in seen:
                seen.add(q)
                out.append(q)
    return out


def _collect_sources(points: list) -> list[str]:
    sources: set[str] = set()
    for p in points:
        for s in p.get("glossarySources") or []:
            sources.add(s)
    return sorted(sources)


def generate_narrative(
    points: list,
    synthesis_points: list[SynthesisPoint] | None = None,
    glossary_context: list[dict] | None = None,
    llm_service: Any | None = None,
    tone: str = "warm",
    length: str = "medium",
    locale: str = "nl",
) -> EnergyProfileNarrative:
    """Bouw een complete EnergyProfileNarrative.

    Wanneer `llm_service` None is, wordt de Fallback Template Layer
    gebruikt voor alle secties.

    Wanneer een LLM service is opgegeven, worden secties parallel
    aangeleverd; iedere sectie valt automatisch terug op fallback bij een
    LLM-fout (zonder de hele narrative te breken).
    """
    if llm_service is None:
        return build_fallback_narrative(points, synthesis_points)

    by_method: dict[str, list] = {}
    for p in points:
        by_method.setdefault(p.get("method", "unknown"), []).append(p)

    method_overviews: dict[str, NarrativeSection] = {}
    for method, ps in by_method.items():
        if method == "cross":
            continue
        request: NarrativeRequest = {
            "section": "methodOverview",
            "method": method,
            "interpretationPoints": ps,
            "synthesisPoints": [],
            "glossaryContext": glossary_context or [],
            "tone": tone,  # type: ignore[typeddict-item]
            "length": length,  # type: ignore[typeddict-item]
            "locale": locale,  # type: ignore[typeddict-item]
            "profileData": {},
        }
        method_overviews[method] = generate_section_with_llm(request, llm_service)

    cross_points = by_method.get("cross", [])
    synthesis_request: NarrativeRequest = {
        "section": "synthesis",
        "method": "energy-profile",
        "interpretationPoints": cross_points,
        "synthesisPoints": synthesis_points or [],
        "glossaryContext": glossary_context or [],
        "tone": "reflective",  # type: ignore[typeddict-item]
        "length": length,  # type: ignore[typeddict-item]
        "locale": locale,  # type: ignore[typeddict-item]
        "profileData": {},
    }
    synthesis_section = generate_section_with_llm(synthesis_request, llm_service)

    summary_request: NarrativeRequest = {
        "section": "summary",
        "method": "energy-profile",
        "interpretationPoints": [p for p in points if p.get("confidence") == "high"][:5],
        "synthesisPoints": synthesis_points or [],
        "glossaryContext": glossary_context or [],
        "tone": tone,  # type: ignore[typeddict-item]
        "length": "short",  # type: ignore[typeddict-item]
        "locale": locale,  # type: ignore[typeddict-item]
        "profileData": {},
    }
    summary_section = generate_section_with_llm(summary_request, llm_service)

    intro_request: NarrativeRequest = {
        "section": "intro",
        "method": "energy-profile",
        "interpretationPoints": [],
        "synthesisPoints": [],
        "glossaryContext": [],
        "tone": "warm",  # type: ignore[typeddict-item]
        "length": "short",  # type: ignore[typeddict-item]
        "locale": locale,  # type: ignore[typeddict-item]
        "profileData": {},
    }
    intro_section = build_fallback_narrative([])["intro"]

    themes_request: NarrativeRequest = {
        "section": "themes",
        "method": "energy-profile",
        "interpretationPoints": [
            p for p in points if p.get("section") in {"energy", "themes", "balance"}
        ],
        "synthesisPoints": [],
        "glossaryContext": glossary_context or [],
        "tone": tone,  # type: ignore[typeddict-item]
        "length": length,  # type: ignore[typeddict-item]
        "locale": locale,  # type: ignore[typeddict-item]
        "profileData": {},
    }
    themes_section = generate_section_with_llm(themes_request, llm_service)

    return {
        "intro": intro_section,
        "summary": summary_section,
        "themes": [themes_section] if themes_section.get("text") else [],
        "methodOverviews": method_overviews,
        "synthesis": synthesis_section,
    }
