"""
Orb rules: resolution from in-code defaults or DB (kb_item_property / kb_weight_rule).
OrbRuleResolver: get_orb(aspect_type, body_a, body_b, context) -> float.
"""
from __future__ import annotations

from typing import Any, Optional, Protocol


class OrbRuleResolver(Protocol):
    """Resolve allowed orb (degrees) for an aspect between two bodies."""

    def get_orb(
        self,
        aspect_type: str,
        body_a: str,
        body_b: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        ...


# Default orbs (degrees) per aspect type; used when no DB.
DEFAULT_ORBS: dict[str, float] = {
    "conjunction": 10.0,
    "opposition": 10.0,
    "trine": 8.0,
    "square": 8.0,
    "sextile": 6.0,
    "quincunx": 3.0,
    "semi-square": 2.0,
    "sesquiquadrate": 2.0,
}


class DefaultOrbResolver:
    """In-code orb rules; no DB. Uses DEFAULT_ORBS with fallback."""

    def get_orb(
        self,
        aspect_type: str,
        body_a: str,
        body_b: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        return DEFAULT_ORBS.get(aspect_type, 8.0)


def _sqlite_resolver_from_path(db_path: str, profile_code: Optional[str] = None) -> Optional["SqliteOrbResolver"]:
    """Create SqliteOrbResolver if path exists and has required tables."""
    import sqlite3
    import os
    if not db_path or not os.path.isfile(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('kb_item_type','kb_item','kb_property_def','kb_item_property')"
        )
        tables = {r[0] for r in cur.fetchall()}
        conn.close()
        if len(tables) >= 4:
            return SqliteOrbResolver(db_path, profile_code=profile_code)
    except Exception:
        pass
    return None


class SqliteOrbResolver:
    """
    Resolve orbs from SQLite: kb_item (type=aspect, code=aspect_type) + kb_item_property (orb_deg).
    Falls back to DefaultOrbResolver when value missing.
    """

    def __init__(self, db_path: str, profile_code: Optional[str] = None):
        self.db_path = db_path
        self.profile_code = profile_code or "default"
        self._fallback = DefaultOrbResolver()

    def get_orb(
        self,
        aspect_type: str,
        body_a: str,
        body_b: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT ip.value_float
                FROM kb_item_type it
                JOIN kb_item i ON i.type_id = it.type_id AND it.code = 'aspect'
                JOIN kb_item_property ip ON ip.item_id = i.item_id
                JOIN kb_property_def pd ON ip.prop_id = pd.prop_id AND pd.code = 'orb_deg'
                WHERE i.code = ? AND ip.value_float IS NOT NULL
                LIMIT 1
                """,
                (aspect_type,),
            )
            row = cur.fetchone()
            conn.close()
            if row is not None and row[0] is not None:
                return float(row[0])
        except Exception:
            pass
        return self._fallback.get_orb(aspect_type, body_a, body_b, context)


def create_orb_resolver(
    db_path: Optional[str] = None,
    orb_profile: Optional[str] = None,
) -> OrbRuleResolver:
    """Factory: DB resolver if db_path and tables exist, else default."""
    if db_path:
        res = _sqlite_resolver_from_path(db_path, profile_code=orb_profile)
        if res is not None:
            return res
    return DefaultOrbResolver()
