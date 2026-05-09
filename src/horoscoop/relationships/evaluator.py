"""Evaluator voor de Relationship Matrix.

Voert de symbolische `condition` van elke relatie uit op een resolved
value-mapping. De resolved values zijn de RAW outputs zoals afgeleid uit
de calculation layer (sign-namen, scores, type-namen, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .registry import RELATIONSHIP_MATRIX
from .types import RelationshipDefinition, RelationshipKind


_WESTERN_SIGN_ELEMENT = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

_WESTERN_SIGN_POLARITY = {
    "Aries": "yang", "Gemini": "yang", "Leo": "yang", "Libra": "yang",
    "Sagittarius": "yang", "Aquarius": "yang",
    "Taurus": "yin", "Cancer": "yin", "Virgo": "yin", "Scorpio": "yin",
    "Capricorn": "yin", "Pisces": "yin",
}


@dataclass(frozen=True)
class EvaluatedRelationship:
    relationship_id: str
    relationship_type: RelationshipKind
    matched: bool
    interpretation: str
    synthesis_weight: float
    left_value: Any
    right_value: Any


def _is_high(score: Any, threshold: float = 0.6) -> bool:
    try:
        return float(score) >= threshold
    except (TypeError, ValueError):
        return False


def _is_low(score: Any, threshold: float = 0.3) -> bool:
    try:
        return float(score) <= threshold
    except (TypeError, ValueError):
        return False


def _bazi_element_score(bazi_value: Any, element: str) -> float | None:
    """`bazi.element-balance.core` is doorgaans een dict met scores per element."""
    if isinstance(bazi_value, dict):
        for key in (element, element.capitalize(), element.upper()):
            if key in bazi_value:
                try:
                    return float(bazi_value[key])
                except (TypeError, ValueError):
                    return None
    return None


def _element_of_sign(sign: Any) -> str | None:
    if not isinstance(sign, str):
        return None
    return _WESTERN_SIGN_ELEMENT.get(sign)


def _polarity_of_sign(sign: Any) -> str | None:
    if not isinstance(sign, str):
        return None
    return _WESTERN_SIGN_POLARITY.get(sign)


_CONDITIONS: dict[str, Callable[[Any, Any], bool]] = {}


def _register(name: str) -> Callable[[Callable[[Any, Any], bool]], Callable[[Any, Any], bool]]:
    def deco(fn: Callable[[Any, Any], bool]) -> Callable[[Any, Any], bool]:
        _CONDITIONS[name] = fn
        return fn
    return deco


@_register("same_element")
def _same_element(left: Any, right: Any) -> bool:
    a = _element_of_sign(left)
    b = _element_of_sign(right)
    return a is not None and a == b


@_register("opposing_polarity")
def _opposing_polarity(left: Any, right: Any) -> bool:
    a = _polarity_of_sign(left)
    b = _polarity_of_sign(right)
    return bool(a and b and a != b)


@_register("left_high_right_low")
def _left_high_right_low(left: Any, right: Any) -> bool:
    return _is_high(left) and _is_low(right)


@_register("both_high_fire")
def _both_high_fire(western_fire: Any, bazi_balance: Any) -> bool:
    bazi_fire = _bazi_element_score(bazi_balance, "fire")
    if bazi_fire is None:
        return False
    return _is_high(western_fire) and _is_high(bazi_fire)


@_register("both_high_water")
def _both_high_water(western_water: Any, bazi_balance: Any) -> bool:
    bazi_water = _bazi_element_score(bazi_balance, "water")
    if bazi_water is None:
        return False
    return _is_high(western_water) and _is_high(bazi_water)


@_register("emotional_authority_water_moon")
def _emo_authority_water_moon(authority: Any, moon_sign: Any) -> bool:
    if not isinstance(authority, str):
        return False
    is_emotional = "emotional" in authority.lower() or "solar plexus" in authority.lower()
    return is_emotional and _element_of_sign(moon_sign) == "water"


def evaluate_relationships(
    resolved_values: dict[str, Any],
    matrix: list[RelationshipDefinition] | None = None,
) -> list[EvaluatedRelationship]:
    """Evalueer alle relaties tegen een mapping van value_id -> raw value.

    Onbekende condities resulteren in een niet-gematchte evaluatie (matched=False),
    nooit in een crash; dit houdt de pipeline robuust.
    """
    matrix = matrix or RELATIONSHIP_MATRIX
    out: list[EvaluatedRelationship] = []
    for rel in matrix:
        left = resolved_values.get(rel["left"])
        right = resolved_values.get(rel["right"])
        cond_name = rel.get("condition", "")
        cond_fn = _CONDITIONS.get(cond_name)
        matched = False
        if cond_fn is not None and left is not None and right is not None:
            try:
                matched = bool(cond_fn(left, right))
            except Exception:
                matched = False
        out.append(
            EvaluatedRelationship(
                relationship_id=rel["id"],
                relationship_type=rel["relationshipType"],
                matched=matched,
                interpretation=rel.get("interpretation", ""),
                synthesis_weight=float(rel.get("synthesisWeight", 0.0)),
                left_value=left,
                right_value=right,
            )
        )
    return out
