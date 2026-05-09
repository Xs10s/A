"""Centrale glossary-registry.

Verzamelt alle glossary-entries van alle methodes in \u00e9\u00e9n
deterministische mapping op `key`. De registry wordt opgebouwd bij
import-tijd; entries zijn statisch.
"""

from __future__ import annotations

from typing import Iterable

from .bazi import BAZI_ENTRIES
from .human_design import HUMAN_DESIGN_ENTRIES
from .maya import MAYA_ENTRIES
from .types import GlossaryEntry, GlossaryMethod, GlossaryRegistry
from .vedic import VEDIC_ENTRIES
from .western import WESTERN_ENTRIES


def _build_registry(*entry_lists: Iterable[GlossaryEntry]) -> GlossaryRegistry:
    registry: GlossaryRegistry = {}
    for entries in entry_lists:
        for entry in entries:
            key = entry["key"]
            if key in registry:
                raise ValueError(f"Duplicate glossary key: {key}")
            registry[key] = entry
    return registry


GLOSSARY: GlossaryRegistry = _build_registry(
    WESTERN_ENTRIES,
    VEDIC_ENTRIES,
    BAZI_ENTRIES,
    HUMAN_DESIGN_ENTRIES,
    MAYA_ENTRIES,
)


def get_entry(key: str) -> GlossaryEntry:
    """Return entry for `key`, raising KeyError if missing."""
    return GLOSSARY[key]


def get_entry_or_none(key: str) -> GlossaryEntry | None:
    """Return entry for `key`, or None if missing."""
    return GLOSSARY.get(key)


def get_entries_by_method(method: GlossaryMethod) -> list[GlossaryEntry]:
    return [e for e in GLOSSARY.values() if e.get("method") == method]


def get_entries_by_category(category: str) -> list[GlossaryEntry]:
    return [e for e in GLOSSARY.values() if e.get("category") == category]


def list_keys() -> list[str]:
    return sorted(GLOSSARY.keys())
