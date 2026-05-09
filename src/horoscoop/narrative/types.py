"""Types for narrative generation."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from ..interpretation.types import InterpretationPoint


NARRATIVE_VERSION = "1.0.0"


NarrativeStyle = Literal["concise", "warm", "reflective"]


class SynthesisPoint(TypedDict, total=False):
    """Een verbinding over methodes heen.

    De Synthesis Layer (zie cross_system) produceert overeenkomsten,
    contrasten en spanningen. We beschrijven ze hier in een uniform
    schema dat de Narrative Layer kan consumeren.
    """

    id: str
    relationshipType: str
    description: str
    sources: list[str]
    confidence: Literal["low", "medium", "high"]
    glossaryKeys: list[str]


class NarrativeRequest(TypedDict, total=False):
    """Gecontroleerde input voor de LLM (of fallback)."""

    section: str
    method: str
    profileData: dict[str, Any]
    glossaryContext: list[dict[str, Any]]
    interpretationPoints: list[InterpretationPoint]
    synthesisPoints: list[SynthesisPoint]
    tone: NarrativeStyle
    length: Literal["short", "medium", "long"]
    locale: Literal["nl", "en"]


class NarrativeSection(TypedDict, total=False):
    section: str
    method: str
    text: str
    bulletPoints: list[str]
    reflectionQuestions: list[str]
    sources: list[str]
    style: NarrativeStyle
    generator: Literal["fallback", "llm"]


class EnergyProfileNarrative(TypedDict, total=False):
    intro: NarrativeSection
    summary: NarrativeSection
    themes: list[NarrativeSection]
    methodOverviews: dict[str, NarrativeSection]
    synthesis: NarrativeSection
