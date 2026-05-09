"""Fallback Template Layer.

Genereert vloeiende Nederlandse tekst zonder LLM, op basis van
InterpretationPoints. Dit garandeert dat de app altijd bruikbaar blijft.
"""

from __future__ import annotations

from typing import Iterable

from ..data.glossary import get_entry_or_none
from ..formulas import get_formula_or_none
from ..interpretation.types import InterpretationPoint
from .types import (
    EnergyProfileNarrative,
    NarrativeSection,
    SynthesisPoint,
)


def render_point_fallback(point: InterpretationPoint) -> str:
    """Render een interpretationPoint deterministisch als prozablok."""
    parts: list[str] = []
    if point.get("technicalLabel"):
        parts.append(point["technicalLabel"] + ".")
    if point.get("humanMeaning"):
        sentence = point["humanMeaning"].strip()
        if sentence and not sentence.endswith("."):
            sentence += "."
        parts.append(sentence)
    if point.get("balancedExpression"):
        parts.append(point["balancedExpression"].strip())
    if point.get("shadowExpression"):
        parts.append(point["shadowExpression"].strip())
    return " ".join(p for p in parts if p)


def _section_for_points(
    section: str,
    method: str,
    points: list[InterpretationPoint],
) -> NarrativeSection:
    text_parts: list[str] = []
    bullets: list[str] = []
    reflections: list[str] = []
    sources: list[str] = []

    for p in points:
        text_parts.append(render_point_fallback(p))
        bullets.append(p.get("technicalLabel", ""))
        reflections.extend(p.get("reflectionQuestions", []) or [])
        sources.extend(p.get("glossarySources", []) or [])

    seen: set[str] = set()
    deduped_reflections = []
    for q in reflections:
        if q and q not in seen:
            seen.add(q)
            deduped_reflections.append(q)

    return {
        "section": section,
        "method": method,
        "text": "\n\n".join(t for t in text_parts if t),
        "bulletPoints": [b for b in bullets if b],
        "reflectionQuestions": deduped_reflections,
        "sources": sorted(set(sources)),
        "style": "warm",
        "generator": "fallback",
    }


def _intro_section() -> NarrativeSection:
    return {
        "section": "intro",
        "method": "energy-profile",
        "text": (
            "Dit profiel combineert berekende waarden uit meerdere methodes. "
            "De teksten zijn een uitnodiging tot zelfonderzoek, geen voorspelling. "
            "Lees ze als reflectiekader: \"dit kan wijzen op...\", niet als waarheid over wie je bent."
        ),
        "bulletPoints": [],
        "reflectionQuestions": [],
        "sources": [],
        "style": "warm",
        "generator": "fallback",
    }


def _summary_section(points: list[InterpretationPoint]) -> NarrativeSection:
    if not points:
        return {
            "section": "summary",
            "method": "energy-profile",
            "text": "Er zijn nog onvoldoende waarden beschikbaar om een samenvatting op te bouwen.",
            "bulletPoints": [],
            "reflectionQuestions": [],
            "sources": [],
            "style": "warm",
            "generator": "fallback",
        }
    high_conf = [p for p in points if p.get("confidence") == "high"]
    selected = high_conf[:3] if high_conf else points[:3]
    text = " ".join(p.get("humanMeaning", "") for p in selected if p.get("humanMeaning"))
    return {
        "section": "summary",
        "method": "energy-profile",
        "text": text.strip(),
        "bulletPoints": [p.get("technicalLabel", "") for p in selected],
        "reflectionQuestions": [],
        "sources": sorted({s for p in selected for s in (p.get("glossarySources") or [])}),
        "style": "warm",
        "generator": "fallback",
    }


def _synthesis_section(synthesis_points: list[SynthesisPoint], cross_points: list[InterpretationPoint]) -> NarrativeSection:
    text_parts: list[str] = []
    bullets: list[str] = []
    reflections: list[str] = []
    sources: list[str] = []
    for sp in synthesis_points:
        if sp.get("description"):
            text_parts.append(sp["description"])
        bullets.append(sp.get("id", ""))
        sources.extend(sp.get("glossaryKeys") or [])
        sources.extend(sp.get("sources") or [])
    for p in cross_points:
        text_parts.append(render_point_fallback(p))
        bullets.append(p.get("technicalLabel", ""))
        reflections.extend(p.get("reflectionQuestions") or [])
        sources.extend(p.get("glossarySources") or [])
    return {
        "section": "synthesis",
        "method": "energy-profile",
        "text": "\n\n".join(t for t in text_parts if t),
        "bulletPoints": [b for b in bullets if b],
        "reflectionQuestions": reflections,
        "sources": sorted(set(sources)),
        "style": "reflective",
        "generator": "fallback",
    }


def build_fallback_narrative(
    points: list[InterpretationPoint],
    synthesis_points: list[SynthesisPoint] | None = None,
) -> EnergyProfileNarrative:
    synthesis_points = synthesis_points or []

    by_method: dict[str, list[InterpretationPoint]] = {}
    for p in points:
        by_method.setdefault(p.get("method", "unknown"), []).append(p)

    method_overviews: dict[str, NarrativeSection] = {}
    for method, ps in by_method.items():
        if method == "cross":
            continue
        method_overviews[method] = _section_for_points("methodOverview", method, ps)

    cross_points = by_method.get("cross", [])

    themes_section = _section_for_points("themes", "energy-profile",
                                         [p for p in points if p.get("section") in {"energy", "themes", "balance"}])

    return {
        "intro": _intro_section(),
        "summary": _summary_section(points),
        "themes": [themes_section] if themes_section.get("text") else [],
        "methodOverviews": method_overviews,
        "synthesis": _synthesis_section(synthesis_points, cross_points),
    }
