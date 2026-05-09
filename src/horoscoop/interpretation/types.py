"""Types for the Interpretation Builder."""

from __future__ import annotations

from typing import Literal, TypedDict


INTERPRETATION_BUILDER_VERSION = "1.0.0"


InterpretationConfidence = Literal["low", "medium", "high"]


class InterpretationPoint(TypedDict, total=False):
    formulaId: str
    method: str
    section: str
    technicalLabel: str
    humanMeaning: str
    balancedExpression: str
    shadowExpression: str
    reflectionQuestions: list[str]
    glossarySources: list[str]
    inputs: dict[str, str]
    confidence: InterpretationConfidence
    relationshipType: str
    notes: list[str]
