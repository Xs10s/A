"""
Values Registry
===============

Verrijkt elke berekende waarde met expliciete metadata zodat formules,
relaties en validatie deterministisch kunnen werken.

De Values Registry is een verrijking BOVENOP de bestaande
`horoscoop.data.calculations.calculable_values.CALCULABLE_VALUES`
om duplicatie te voorkomen. Elke entry vertaalt zich naar een
`ValueDefinition` met:

    id, method, category, valueType, glossaryKey, requiredFor,
    canRelateTo, priority, description.

Conventies:
    - `valueType` is een betekenisrol (bv. "sign", "house", "planet",
      "score", "element", "polarity", "aspect", ...).
    - `glossaryKey` verwijst NAAR een dynamische glossary lookup; een
      `sign`-waarde verwijst niet naar 1 vaste sleutel maar naar een
      *prefix*: "western.sign.<value>" (zie `glossary_key_for_value`).
    - `requiredFor` benoemt de output-secties die deze waarde nodig
      hebben (bv. "identity", "energy", "synthesis").
    - `canRelateTo` somt andere value-id's op waarmee deze waarde
      betekenisvol gerelateerd mag worden in de Relationship Matrix.
"""

from __future__ import annotations

from .types import (
    VALUES_REGISTRY_VERSION,
    ValueDefinition,
    ValueType,
    Priority,
    OutputSection,
)
from .registry import (
    VALUES_REGISTRY,
    get_value,
    get_value_or_none,
    get_values_by_method,
    get_values_by_section,
    glossary_key_for_value,
    list_value_ids,
)

__all__ = [
    "VALUES_REGISTRY_VERSION",
    "VALUES_REGISTRY",
    "ValueDefinition",
    "ValueType",
    "Priority",
    "OutputSection",
    "get_value",
    "get_value_or_none",
    "get_values_by_method",
    "get_values_by_section",
    "glossary_key_for_value",
    "list_value_ids",
]
