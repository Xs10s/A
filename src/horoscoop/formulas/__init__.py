"""
Formula Registry + Meaning Constructs
=====================================

Een formule beschrijft betekenisvol HOE meerdere waarden samen iets zeggen:

    western.planet_in_sign_in_house
    western.aspect_between_planets
    western.element_balance_dominant
    cross.element_overlap

Elke formule heeft:
    - inputTypes        : welke valueTypes nodig zijn
    - requiredValues    : welke value-id's verplicht zijn
    - optionalValues    : welke value-id's aanvullend mogen zijn
    - relationshipType  : welke betekenisrol de combinatie heeft
    - outputSection     : op welk deel van het profiel deze formule
                           bijdraagt (identity, energy, ...)
    - glossaryKeysNeeded: welke glossary-categorieen geraadpleegd worden
    - meaningConstruct  : SEMANTISCH model dat een tekstvorm definieert
                           zonder zelf vrije tekst te genereren
    - fallbackTemplate  : deterministische tekst zonder LLM
    - llmAllowed        : of de LLM deze mag herschrijven
    - confidenceRules   : minimum aantal aanwezige inputs

Belangrijk: Formules genereren GEEN absolute uitspraken. Alle templates
zijn uitnodigend ("dit kan wijzen op...", "in balans toont dit...").
"""

from __future__ import annotations

from .types import (
    FORMULA_REGISTRY_VERSION,
    FormulaDefinition,
    MeaningConstruct,
    RelationshipType,
)
from .registry import (
    FORMULA_REGISTRY,
    get_formula,
    get_formula_or_none,
    get_formulas_by_method,
    get_formulas_by_section,
    list_formula_ids,
)

__all__ = [
    "FORMULA_REGISTRY_VERSION",
    "FORMULA_REGISTRY",
    "FormulaDefinition",
    "MeaningConstruct",
    "RelationshipType",
    "get_formula",
    "get_formula_or_none",
    "get_formulas_by_method",
    "get_formulas_by_section",
    "list_formula_ids",
]
