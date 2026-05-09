"""
Glossary Layer
==============

Statische, controleerbare betekenisdata voor alle methodes.

Ontwerpprincipes:
- Glossary entries zijn deterministisch en versie-bewaakt.
- Entries leveren expliciete velden (essence, balancedExpression,
  shadowExpression, lifeArea, reflectionQuestions, avoidClaims).
- De LLM mag NOOIT nieuwe glossary-betekenis verzinnen; de tekstgeneratie
  put uit deze entries.
- Bestaande korte teksten in `horoscoop.knowledgebase` blijven bruikbaar
  als beknopte zinnen; deze laag levert het rijke, gestructureerde model.

Naming convention voor `key`:
    "<method>.<category>.<id>"

Voorbeelden:
    "western.sign.aries"
    "western.planet.sun"
    "western.house.9"
    "western.aspect.trine"
    "western.element.fire"
"""

from __future__ import annotations

from .types import (
    GLOSSARY_VERSION,
    GlossaryEntry,
    GlossaryRegistry,
    Locale,
)
from .registry import (
    GLOSSARY,
    get_entry,
    get_entry_or_none,
    get_entries_by_method,
    get_entries_by_category,
    list_keys,
)

__all__ = [
    "GLOSSARY_VERSION",
    "GLOSSARY",
    "GlossaryEntry",
    "GlossaryRegistry",
    "Locale",
    "get_entry",
    "get_entry_or_none",
    "get_entries_by_method",
    "get_entries_by_category",
    "list_keys",
]
