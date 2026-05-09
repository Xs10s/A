"""Cross-method formules.

Deze formules combineren waarden uit meerdere methodes om resonantie en
contrast zichtbaar te maken (bijvoorbeeld Westerse vuur-balans met
BaZi vuur-balans). Ze claimen nooit absolute waarheid.
"""

from __future__ import annotations

from .types import FormulaDefinition


CROSS_ELEMENT_OVERLAP: FormulaDefinition = {
    "id": "cross.element_overlap",
    "method": "cross",
    "description": "Overlap in dominant element tussen Westers en BaZi.",
    "inputTypes": ["element", "score"],
    "requiredValues": [
        "western.balance.elements.fire",
        "bazi.element-balance.core",
    ],
    "optionalValues": [],
    "relationshipType": "cross_method_overlap",
    "outputSection": "synthesis",
    "glossaryKeysNeeded": ["element", "five_element"],
    "meaningConstruct": {
        "valueRoles": {
            "western": "Westerse elementenscores",
            "bazi": "BaZi elementenscores",
            "element": "het element dat in beide systemen sterk aanwezig is",
        },
        "semanticPattern": (
            "{element.essence} komt in meerdere systemen terug als zichtbaar thema."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {element.balancedExpression}."
        ),
        "shadowTemplate": (
            "Uit balans kan dit voelen als {element.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Waar herken ik dit terugkerend element in mijn dagelijkse keuzes?",
        ],
    },
    "fallbackTemplate": (
        "{element.label} komt in meerdere systemen terug als zichtbaar thema. "
        "Dit kan wijzen op {element.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 2},
}


CROSS_DECISION_PATTERN: FormulaDefinition = {
    "id": "cross.decision_pattern",
    "method": "cross",
    "description": "Beslispatroon: Human Design type+autoriteit en Westerse Maan.",
    "inputTypes": ["type", "authority", "sign"],
    "requiredValues": [
        "human-design.type.core",
        "human-design.authority.core",
    ],
    "optionalValues": [
        "western.planets.moon.sign",
    ],
    "relationshipType": "decision_pattern",
    "outputSection": "decision_pattern",
    "glossaryKeysNeeded": ["type", "authority", "sign"],
    "meaningConstruct": {
        "valueRoles": {
            "type": "Human Design type",
            "authority": "innerlijke autoriteit",
            "moon": "emotionele basis",
        },
        "semanticPattern": (
            "Beslissen lijkt te resoneren met {type.essence} en {authority.essence}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {type.balancedExpression}, ondersteund door "
            "{authority.balancedExpression}."
        ),
        "shadowTemplate": (
            "Uit balans kan dit voelen als {type.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Welke beslissing wacht nu op de juiste timing?",
        ],
    },
    "fallbackTemplate": (
        "Beslispatroon: {type.label} met {authority.label}. {type.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 2},
}


CROSS_FORMULAS: list[FormulaDefinition] = [
    CROSS_ELEMENT_OVERLAP,
    CROSS_DECISION_PATTERN,
]
