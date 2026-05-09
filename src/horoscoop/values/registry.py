"""Values Registry.

Bouwt een verrijkte registry op rond de bestaande CALCULABLE_VALUES.
Belangrijk: deze laag dupliceert geen berekeningen of waarde-id's; ze
voegt alleen extra metadata toe (glossaryKey, valueType, requiredFor,
canRelateTo, priority).
"""

from __future__ import annotations

from typing import Any

from ..data.calculations.calculable_values import CALCULABLE_VALUES
from ..data.glossary import GLOSSARY, get_entry_or_none
from .types import (
    OutputSection,
    Priority,
    ValueDefinition,
    ValueType,
)


# ---------------------------------------------------------------------------
# Western metadata helpers
# ---------------------------------------------------------------------------


_WESTERN_PLANET_KEYS = {
    "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
    "uranus", "neptune", "pluto", "chiron",
}


def _western_metadata(value_id: str) -> dict[str, Any]:
    """Return enrichment metadata for a Western calculable value.

    The mapping is heuristic but deterministic; new entries fall back to
    sensible defaults.
    """
    parts = value_id.split(".")
    # parts e.g. ["western", "planets", "sun", "sign"]
    if len(parts) < 3:
        return {}

    if parts[1] == "planets" and len(parts) >= 4:
        planet = parts[2]
        attr = parts[3]
        if attr == "sign":
            return {
                "valueType": "sign",
                "glossaryKeyPrefix": "western.sign.",
                "requiredFor": _planet_sections(planet),
                "canRelateTo": [
                    f"western.planets.{planet}.house",
                    f"western.planets.{planet}.degree",
                ] + [
                    f"bazi.element-balance.core",
                ],
                "priority": "high" if planet in {"sun", "moon"} else "medium",
            }
        if attr == "house":
            return {
                "valueType": "house",
                "glossaryKeyPrefix": "western.house.",
                "requiredFor": _planet_sections(planet),
                "canRelateTo": [
                    f"western.planets.{planet}.sign",
                ],
                "priority": "high" if planet in {"sun", "moon"} else "medium",
            }
        if attr == "degree":
            return {
                "valueType": "score",
                "requiredFor": ["expression"],
                "canRelateTo": [],
                "priority": "low",
            }
        if attr == "retrograde":
            return {
                "valueType": "concept",
                "requiredFor": ["expression", "shadow"],
                "canRelateTo": [],
                "priority": "low",
            }

    if parts[1] == "ascendant":
        return {
            "valueType": "sign" if parts[2] == "sign" else "score",
            "glossaryKeyPrefix": "western.sign." if parts[2] == "sign" else "",
            "requiredFor": ["identity", "expression"],
            "canRelateTo": ["western.planets.sun.sign", "western.planets.moon.sign"],
            "priority": "high",
        }

    if parts[1] == "mc":
        return {
            "valueType": "sign" if parts[2] == "sign" else "score",
            "glossaryKeyPrefix": "western.sign." if parts[2] == "sign" else "",
            "requiredFor": ["purpose"],
            "canRelateTo": ["western.angle.mc"],
            "priority": "medium",
        }

    if parts[1] == "houses" and len(parts) >= 4:
        return {
            "valueType": "sign" if parts[3] == "cusp-sign" else "score",
            "glossaryKeyFixed": f"western.house.{parts[2]}",
            "requiredFor": ["expression"],
            "canRelateTo": [],
            "priority": "low",
        }

    if parts[1] == "aspects":
        return {
            "valueType": "aspect",
            "glossaryKeyPrefix": "western.aspect.",
            "requiredFor": ["relationships", "growth"],
            "canRelateTo": [],
            "priority": "medium",
        }

    if parts[1] == "balance" and len(parts) >= 4:
        kind = parts[2]  # elements / modalities / polarity
        sub = parts[3]
        if kind == "elements":
            return {
                "valueType": "score",
                "glossaryKeyFixed": f"western.element.{sub}",
                "requiredFor": ["energy", "balance", "themes", "synthesis"],
                "canRelateTo": [
                    f"bazi.element-balance.core",
                ],
                "priority": "high",
            }
        if kind == "modalities":
            return {
                "valueType": "score",
                "glossaryKeyFixed": f"western.modality.{sub}",
                "requiredFor": ["energy", "balance"],
                "canRelateTo": [],
                "priority": "medium",
            }
        if kind == "polarity":
            return {
                "valueType": "polarity_score",
                "glossaryKeyFixed": f"western.polarity.{sub}",
                "requiredFor": ["energy", "balance"],
                "canRelateTo": [],
                "priority": "medium",
            }

    if parts[1] == "nodes" and len(parts) >= 4:
        node = parts[2]
        attr = parts[3]
        if attr == "sign":
            return {
                "valueType": "sign",
                "glossaryKeyPrefix": "western.sign.",
                "requiredFor": ["growth", "purpose"],
                "canRelateTo": [f"western.nodes.{node}.house"],
                "priority": "medium",
            }
        if attr == "house":
            return {
                "valueType": "house",
                "glossaryKeyPrefix": "western.house.",
                "requiredFor": ["growth", "purpose"],
                "canRelateTo": [f"western.nodes.{node}.sign"],
                "priority": "medium",
            }

    return {}


def _planet_sections(planet: str) -> list[OutputSection]:
    if planet == "sun":
        return ["identity", "energy", "synthesis"]
    if planet == "moon":
        return ["identity", "energy", "rhythm", "synthesis"]
    if planet == "venus":
        return ["relationships", "expression"]
    if planet == "mars":
        return ["energy", "expression"]
    if planet == "mercury":
        return ["expression", "decision_pattern"]
    if planet == "jupiter":
        return ["growth", "purpose"]
    if planet == "saturn":
        return ["growth", "shadow"]
    return ["expression"]


# ---------------------------------------------------------------------------
# Cross-method metadata helpers (lean)
# ---------------------------------------------------------------------------


def _cross_method_metadata(value_id: str) -> dict[str, Any]:
    if value_id.startswith("vedic.panchanga.nakshatra"):
        return {
            "valueType": "nakshatra",
            "requiredFor": ["energy", "rhythm"],
            "canRelateTo": ["western.planets.moon.sign"],
            "priority": "medium",
        }
    if value_id.startswith("vedic.panchanga.tithi"):
        return {
            "valueType": "tithi",
            "requiredFor": ["rhythm"],
            "canRelateTo": ["western.planets.moon.sign"],
            "priority": "low",
        }
    if value_id.startswith("bazi.pillars."):
        return {
            "valueType": "pillar",
            "requiredFor": ["energy", "rhythm"],
            "canRelateTo": [],
            "priority": "medium",
        }
    if value_id == "bazi.element-balance.core":
        return {
            "valueType": "score",
            "requiredFor": ["energy", "balance", "synthesis"],
            "canRelateTo": [
                "western.balance.elements.fire",
                "western.balance.elements.earth",
                "western.balance.elements.air",
                "western.balance.elements.water",
            ],
            "priority": "high",
        }
    if value_id == "human-design.type.core":
        return {
            "valueType": "type",
            "glossaryKeyPrefix": "human-design.type.",
            "requiredFor": ["decision_pattern", "energy", "synthesis"],
            "canRelateTo": [
                "human-design.authority.core",
                "western.planets.sun.sign",
            ],
            "priority": "high",
        }
    if value_id == "human-design.authority.core":
        return {
            "valueType": "authority",
            "glossaryKeyPrefix": "human-design.authority.",
            "requiredFor": ["decision_pattern", "synthesis"],
            "canRelateTo": ["human-design.type.core"],
            "priority": "high",
        }
    if value_id == "maya.seal.core":
        return {
            "valueType": "seal",
            "glossaryKeyPrefix": "maya.seal.",
            "requiredFor": ["themes", "synthesis"],
            "canRelateTo": ["maya.tone.core"],
            "priority": "medium",
        }
    if value_id == "maya.tone.core":
        return {
            "valueType": "tone",
            "glossaryKeyFixed": "maya.concept.tone",
            "requiredFor": ["rhythm", "themes"],
            "canRelateTo": ["maya.seal.core"],
            "priority": "low",
        }
    return {}


# ---------------------------------------------------------------------------
# Build the registry
# ---------------------------------------------------------------------------


def _build_value_definition(raw: dict[str, Any]) -> ValueDefinition:
    value_id: str = raw["id"]
    method = raw.get("method", "western")

    enrichment: dict[str, Any] = {}
    if method == "western":
        enrichment = _western_metadata(value_id)
    if not enrichment:
        enrichment = _cross_method_metadata(value_id)

    definition: ValueDefinition = {
        "id": value_id,
        "method": method,
        "category": raw.get("category", "unknown"),
        "label": raw.get("label", value_id),
        "description": raw.get("label", value_id),
        "valueType": enrichment.get("valueType", "concept"),
        "requiredFor": enrichment.get("requiredFor", []),
        "canRelateTo": enrichment.get("canRelateTo", []),
        "priority": enrichment.get("priority", "low"),
        "sourceCalculationId": raw.get("calculationId", ""),
        "sourceOutputKey": raw.get("outputKey", ""),
    }
    if "glossaryKeyPrefix" in enrichment:
        definition["glossaryKeyPrefix"] = enrichment["glossaryKeyPrefix"]
    if "glossaryKeyFixed" in enrichment:
        definition["glossaryKeyFixed"] = enrichment["glossaryKeyFixed"]
    return definition


VALUES_REGISTRY: dict[str, ValueDefinition] = {
    raw["id"]: _build_value_definition(raw) for raw in CALCULABLE_VALUES
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_value(value_id: str) -> ValueDefinition:
    return VALUES_REGISTRY[value_id]


def get_value_or_none(value_id: str) -> ValueDefinition | None:
    return VALUES_REGISTRY.get(value_id)


def get_values_by_method(method: str) -> list[ValueDefinition]:
    return [v for v in VALUES_REGISTRY.values() if v.get("method") == method]


def get_values_by_section(section: OutputSection) -> list[ValueDefinition]:
    return [
        v for v in VALUES_REGISTRY.values()
        if section in (v.get("requiredFor") or [])
    ]


def list_value_ids() -> list[str]:
    return sorted(VALUES_REGISTRY.keys())


def glossary_key_for_value(value_id: str, raw_value: Any) -> str | None:
    """Resolve the glossary key for an instantiated value.

    For value definitions with a `glossaryKeyFixed`, the fixed key is
    returned. For definitions with a `glossaryKeyPrefix`, the suffix is
    derived from the raw value (lowercased, dotted).
    """
    definition = VALUES_REGISTRY.get(value_id)
    if not definition:
        return None
    if definition.get("glossaryKeyFixed"):
        return definition["glossaryKeyFixed"]
    prefix = definition.get("glossaryKeyPrefix")
    if not prefix:
        return None
    if raw_value is None:
        return None
    suffix = str(raw_value).strip().lower().replace(" ", "_")
    if not suffix:
        return None
    candidate = f"{prefix}{suffix}"
    if candidate in GLOSSARY:
        return candidate
    return None
