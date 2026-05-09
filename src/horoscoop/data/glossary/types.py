"""Types for the Glossary Layer."""

from __future__ import annotations

from typing import Literal, TypedDict


GLOSSARY_VERSION = "1.0.0"


Locale = Literal["nl", "en"]


GlossaryMethod = Literal[
    "western",
    "vedic",
    "bazi",
    "human-design",
    "maya",
    "shared",
]


GlossaryCategory = Literal[
    "sign",
    "planet",
    "house",
    "aspect",
    "element",
    "modality",
    "polarity",
    "node",
    "angle",
    "nakshatra",
    "rashi",
    "tithi",
    "yoga",
    "karana",
    "pillar",
    "stem",
    "branch",
    "five_element",
    "ten_god",
    "type",
    "authority",
    "center",
    "channel",
    "gate",
    "profile",
    "kin",
    "seal",
    "tone",
    "wavespell",
    "theme",
    "concept",
]


class GlossaryEntry(TypedDict, total=False):
    """One controlled meaning unit.

    Required:
        key, label, essence, keywords, balancedExpression, shadowExpression,
        lifeArea, reflectionQuestions, avoidClaims, method, category.

    Optional:
        bodyOrEnergyLink, shortLabel, synonyms, sourceNotes, locale.
    """

    key: str
    method: GlossaryMethod
    category: GlossaryCategory
    label: str
    shortLabel: str
    essence: str
    keywords: list[str]
    balancedExpression: str
    shadowExpression: str
    lifeArea: str
    bodyOrEnergyLink: str
    reflectionQuestions: list[str]
    avoidClaims: list[str]
    synonyms: list[str]
    sourceNotes: str
    locale: Locale


GlossaryRegistry = dict[str, GlossaryEntry]
