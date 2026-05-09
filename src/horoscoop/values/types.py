"""Types for the Values Registry."""

from __future__ import annotations

from typing import Literal, TypedDict


VALUES_REGISTRY_VERSION = "1.0.0"


ValueType = Literal[
    "sign",
    "planet",
    "house",
    "aspect",
    "element",
    "modality",
    "polarity",
    "node",
    "angle",
    "score",
    "polarity_score",
    "type",
    "authority",
    "center",
    "channel",
    "gate",
    "profile",
    "rashi",
    "nakshatra",
    "tithi",
    "yoga",
    "karana",
    "pillar",
    "stem",
    "branch",
    "five_element",
    "ten_god",
    "kin",
    "seal",
    "tone",
    "wavespell",
    "pattern",
    "concept",
]


Priority = Literal["high", "medium", "low"]


OutputSection = Literal[
    "identity",
    "energy",
    "relationships",
    "purpose",
    "shadow",
    "growth",
    "synthesis",
    "themes",
    "balance",
    "rhythm",
    "decision_pattern",
    "expression",
]


class ValueDefinition(TypedDict, total=False):
    id: str
    method: Literal[
        "western", "vedic", "bazi", "human-design", "maya", "energy-profile"
    ]
    category: str
    valueType: ValueType
    glossaryKeyPrefix: str
    glossaryKeyFixed: str
    requiredFor: list[OutputSection]
    canRelateTo: list[str]
    priority: Priority
    description: str
    label: str
    sourceCalculationId: str
    sourceOutputKey: str
