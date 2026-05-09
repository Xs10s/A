"""Types for the Formula Registry and Meaning Constructs."""

from __future__ import annotations

from typing import Literal, TypedDict


FORMULA_REGISTRY_VERSION = "1.0.0"


RelationshipType = Literal[
    "expression_in_life_area",   # planet+sign+house
    "expression_in_sign",        # planet+sign
    "expression_in_life_area_only",  # planet+house
    "tension_or_flow",           # aspect between planets
    "balance_score",             # element / modality / polarity scores
    "developmental_direction",   # nodes
    "presentation_style",        # ascendant
    "public_direction",          # MC
    "decision_pattern",          # HD type+authority
    "rhythm",                    # tithi / nakshatra / wavespell
    "core_polarity",             # BaZi day master
    "cross_method_overlap",
    "cross_method_contrast",
    "cross_method_reinforcement",
]


class MeaningConstruct(TypedDict, total=False):
    """Semantic skeleton for a formula's meaning.

    `valueRoles` documents what each input value MEANS in this formula.
    Templates use placeholders that reference glossary fields:

        {planet.essence}, {sign.essence}, {house.lifeArea}

    Templates do NOT generate language outside the strict slots provided
    here. They never invent astrology.
    """

    valueRoles: dict[str, str]
    semanticPattern: str
    balancedTemplate: str
    shadowTemplate: str
    reflectionQuestionsTemplate: list[str]


class ConfidenceRules(TypedDict, total=False):
    minimumInputs: int


class FormulaDefinition(TypedDict, total=False):
    id: str
    method: Literal[
        "western", "vedic", "bazi", "human-design", "maya", "cross"
    ]
    inputTypes: list[str]
    requiredValues: list[str]
    optionalValues: list[str]
    relationshipType: RelationshipType
    outputSection: str
    glossaryKeysNeeded: list[str]
    meaningConstruct: MeaningConstruct
    fallbackTemplate: str
    llmAllowed: bool
    confidenceRules: ConfidenceRules
    description: str
