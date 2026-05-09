"""
Relationship Matrix
===================

Beschrijft welke relaties er kunnen bestaan tussen waarden:

    overlap, contrast, reinforcement, tension, nuance, dominance,
    balance, imbalance, developmentalDirection.

Een relatie is een DECLARATIE: ze beschrijft wanneer twee waarden samen
betekenisvol worden. Het uitvoeren van een relatie (controleren of de
voorwaarde geldt) gebeurt in `evaluator.py`.
"""

from __future__ import annotations

from .types import (
    RELATIONSHIP_MATRIX_VERSION,
    RelationshipDefinition,
    RelationshipKind,
)
from .registry import (
    RELATIONSHIP_MATRIX,
    get_relationship,
    list_relationship_ids,
)
from .evaluator import (
    EvaluatedRelationship,
    evaluate_relationships,
)

__all__ = [
    "RELATIONSHIP_MATRIX_VERSION",
    "RELATIONSHIP_MATRIX",
    "RelationshipDefinition",
    "RelationshipKind",
    "EvaluatedRelationship",
    "evaluate_relationships",
    "get_relationship",
    "list_relationship_ids",
]
