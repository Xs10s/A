"""Vedische glossary entries (NL).

Scaffolding: kernconcepten beschikbaar zodat de architectuur dezelfde
formules en interpretaties kan dragen als voor de Westerse methode.
Verdere uitbreiding (alle 27 nakshatra's, alle yoga's, etc.) volgt
hetzelfde patroon.
"""

from __future__ import annotations

from .types import GlossaryEntry


_AVOID = [
    "geen absolute uitspraken over wie iemand 'is'",
    "geen voorspellingen over de toekomst",
    "geen medische claims",
]


VEDIC_ENTRIES: list[GlossaryEntry] = [
    {
        "key": "vedic.concept.lagna",
        "method": "vedic",
        "category": "concept",
        "label": "Lagna",
        "shortLabel": "Lagna",
        "essence": "het rijzende teken dat de fysieke en zichtbare laag van het leven kleurt",
        "keywords": ["rijzend teken", "lichaam", "richting"],
        "balancedExpression": "lichamelijk verankerde aanwezigheid en duidelijke richting",
        "shadowExpression": "afwezigheid uit eigen lijf of richting",
        "lifeArea": "lichaam, persoonlijkheid, levensrichting",
        "bodyOrEnergyLink": "fysieke verankering",
        "reflectionQuestions": ["Hoe ben ik nu fysiek aanwezig?", "Welke richting voelt levensecht?"],
        "avoidClaims": _AVOID,
    },
    {
        "key": "vedic.concept.nakshatra",
        "method": "vedic",
        "category": "nakshatra",
        "label": "Nakshatra (algemeen)",
        "shortLabel": "Nakshatra",
        "essence": "lunaire constellatie die de emotionele en instinctieve basis kleurt",
        "keywords": ["maan-mansie", "instinct", "patroon"],
        "balancedExpression": "in contact met instinctieve patronen",
        "shadowExpression": "vluchten uit instinct of overheersing van het patroon",
        "lifeArea": "emotionele en instinctieve thema's",
        "bodyOrEnergyLink": "lunair ritme",
        "reflectionQuestions": ["Welk instinctief patroon herken ik?"],
        "avoidClaims": _AVOID,
    },
    {
        "key": "vedic.tithi.generic",
        "method": "vedic",
        "category": "tithi",
        "label": "Tithi (algemeen)",
        "shortLabel": "Tithi",
        "essence": "fase van de maancyclus die het ritme van de dag inkleurt",
        "keywords": ["maan-fase", "ritme", "energie"],
        "balancedExpression": "in afstemming met de fase van het ritme",
        "shadowExpression": "tegen het ritme inwerken",
        "lifeArea": "dagelijks ritme",
        "bodyOrEnergyLink": "lunair ritme",
        "reflectionQuestions": ["Welk ritme voelt nu natuurlijk?"],
        "avoidClaims": _AVOID,
    },
]
