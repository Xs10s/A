"""
Interpretation Builder
======================

Vertaalt berekende waarden naar gecontroleerde `InterpretationPoint`s
zonder vrije proza te genereren. Een InterpretationPoint bevat:

    technicalLabel        : "Zon in Boogschutter in huis 9"
    humanMeaning          : ingevulde semanticPattern
    balancedExpression    : ingevulde balancedTemplate
    shadowExpression      : ingevulde shadowTemplate
    reflectionQuestions   : ingevulde reflectionQuestionsTemplate
    glossarySources       : list of glossary keys gebruikt
    confidence            : low/medium/high
    formulaId             : id van de formule
    method                : western/vedic/...
    section               : output-sectie

De Narrative Generation Layer ontvangt deze punten en zet ze om in
vloeiende tekst (LLM of fallback).
"""

from __future__ import annotations

from .types import (
    INTERPRETATION_BUILDER_VERSION,
    InterpretationPoint,
    InterpretationConfidence,
)
from .builder import (
    build_interpretation_points,
    extract_resolved_values,
)

__all__ = [
    "INTERPRETATION_BUILDER_VERSION",
    "InterpretationPoint",
    "InterpretationConfidence",
    "build_interpretation_points",
    "extract_resolved_values",
]
