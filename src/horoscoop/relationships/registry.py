"""Relationship Matrix entries.

Bewust lean: de matrix bevat enkele krachtige relaties. Nieuwe relaties
kunnen worden toegevoegd zonder bestaande te breken.
"""

from __future__ import annotations

from .types import RelationshipDefinition


WESTERN_INTRA: list[RelationshipDefinition] = [
    {
        "id": "western_sun_moon_same_element",
        "left": "western.planets.sun.sign",
        "right": "western.planets.moon.sign",
        "relationshipType": "reinforcement",
        "condition": "same_element",
        "interpretation": (
            "Wanneer Zon en Maan hetzelfde element delen, kan een terugkerende "
            "energie zichtbaar worden tussen identiteit en gevoel."
        ),
        "synthesisWeight": 0.6,
        "glossaryKeysNeeded": ["element"],
        "description": "Zon en Maan in hetzelfde element",
    },
    {
        "id": "western_sun_moon_opposing_polarity",
        "left": "western.planets.sun.sign",
        "right": "western.planets.moon.sign",
        "relationshipType": "tension",
        "condition": "opposing_polarity",
        "interpretation": (
            "Een polariteitscontrast tussen Zon en Maan kan uitnodigen tot "
            "dialoog tussen actieve richting en innerlijk ritme."
        ),
        "synthesisWeight": 0.5,
        "glossaryKeysNeeded": ["polarity"],
        "description": "Zon en Maan in tegengestelde polariteit",
    },
    {
        "id": "western_element_dominance",
        "left": "western.balance.elements.fire",
        "right": "western.balance.elements.water",
        "relationshipType": "dominance",
        "condition": "left_high_right_low",
        "interpretation": (
            "Sterke vuur-aanwezigheid bij weinig water kan wijzen op een "
            "voorkeur voor actie boven verwerking."
        ),
        "synthesisWeight": 0.4,
        "glossaryKeysNeeded": ["element"],
        "description": "Vuur dominant, water laag",
    },
]


CROSS_METHOD: list[RelationshipDefinition] = [
    {
        "id": "western_fire_bazi_fire_overlap",
        "left": "western.balance.elements.fire",
        "right": "bazi.element-balance.core",
        "relationshipType": "overlap",
        "condition": "both_high_fire",
        "interpretation": (
            "Vuur komt in meerdere systemen terug als zichtbaar thema."
        ),
        "synthesisWeight": 0.8,
        "glossaryKeysNeeded": ["element", "five_element"],
        "description": "Westers vuur + BaZi vuur beide hoog",
    },
    {
        "id": "western_water_bazi_water_overlap",
        "left": "western.balance.elements.water",
        "right": "bazi.element-balance.core",
        "relationshipType": "overlap",
        "condition": "both_high_water",
        "interpretation": (
            "Water komt in meerdere systemen terug als terugkerend thema."
        ),
        "synthesisWeight": 0.8,
        "glossaryKeysNeeded": ["element", "five_element"],
        "description": "Westers water + BaZi water beide hoog",
    },
    {
        "id": "hd_authority_western_moon_resonance",
        "left": "human-design.authority.core",
        "right": "western.planets.moon.sign",
        "relationshipType": "reinforcement",
        "condition": "emotional_authority_water_moon",
        "interpretation": (
            "Een emotionele autoriteit naast een Maan in waterteken kan wijzen "
            "op een sterk emotioneel beslispatroon."
        ),
        "synthesisWeight": 0.7,
        "glossaryKeysNeeded": ["authority", "element"],
        "description": "HD emotional authority + watermaan",
    },
]


RELATIONSHIP_MATRIX: list[RelationshipDefinition] = WESTERN_INTRA + CROSS_METHOD


_BY_ID: dict[str, RelationshipDefinition] = {r["id"]: r for r in RELATIONSHIP_MATRIX}


def get_relationship(rel_id: str) -> RelationshipDefinition:
    return _BY_ID[rel_id]


def list_relationship_ids() -> list[str]:
    return sorted(_BY_ID.keys())
