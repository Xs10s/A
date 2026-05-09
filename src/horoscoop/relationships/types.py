"""Types for the Relationship Matrix."""

from __future__ import annotations

from typing import Any, Callable, Literal, TypedDict


RELATIONSHIP_MATRIX_VERSION = "1.0.0"


RelationshipKind = Literal[
    "overlap",
    "contrast",
    "reinforcement",
    "tension",
    "nuance",
    "dominance",
    "balance",
    "imbalance",
    "developmentalDirection",
]


# A condition function takes the resolved value pair and returns True/False.
ConditionFn = Callable[[Any, Any], bool]


class RelationshipDefinition(TypedDict, total=False):
    id: str
    left: str            # value-id (or category)
    right: str           # value-id (or category)
    relationshipType: RelationshipKind
    condition: str       # symbolic name (e.g. "both_high", "same_element")
    interpretation: str  # neutral statement; not a final narrative
    synthesisWeight: float
    glossaryKeysNeeded: list[str]
    description: str
