"""
Narrative Generation Layer
==========================

Zet `InterpretationPoint`s om naar vloeiende Nederlandse tekst.

Twee paden:

1. Fallback Template Layer (`fallback.py`)
   Deterministisch, geen LLM nodig. App blijft volledig bruikbaar zonder
   externe afhankelijkheden.

2. LLM-vertaalbrug (`generator.py`)
   Roept de `LLMService` aan met een gecontroleerde context: alleen de
   InterpretationPoints, glossary-bronnen en synthesis-punten worden
   doorgegeven; de LLM mag NIET astrologie verzinnen.

Promptlogica blijft centraal in `prompts.py`.
"""

from __future__ import annotations

from .types import (
    NARRATIVE_VERSION,
    EnergyProfileNarrative,
    NarrativeRequest,
    NarrativeSection,
    NarrativeStyle,
    SynthesisPoint,
)
from .fallback import (
    build_fallback_narrative,
    render_point_fallback,
)
from .prompts import (
    PROMPT_VERSION,
    build_prompt,
)
from .generator import (
    generate_narrative,
)

__all__ = [
    "NARRATIVE_VERSION",
    "PROMPT_VERSION",
    "EnergyProfileNarrative",
    "NarrativeRequest",
    "NarrativeSection",
    "NarrativeStyle",
    "SynthesisPoint",
    "build_fallback_narrative",
    "render_point_fallback",
    "build_prompt",
    "generate_narrative",
]
