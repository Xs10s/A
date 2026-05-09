"""BaZi glossary entries (NL) - scaffolding."""

from __future__ import annotations

from .types import GlossaryEntry


_AVOID = [
    "geen absolute uitspraken over wie iemand 'is'",
    "geen voorspellingen over de toekomst",
    "geen medische claims",
]


_FIVE_ELEMENT_DATA = [
    (
        "wood",
        "Hout",
        "groei, plannen en ontwikkeling met richting",
        ["groei", "plannen", "ontwikkeling"],
        "veerkrachtig, plannend en bereid bij te buigen",
        "rigide of overstuurd in groei",
        "ontwikkeling en richting",
    ),
    (
        "fire",
        "Vuur",
        "expressie, zichtbaarheid en inspirerende warmte",
        ["expressie", "warmte", "vitaliteit"],
        "warm, inspirerend en uitnodigend",
        "verbranding of overprestatie",
        "expressie en zichtbaarheid",
    ),
    (
        "earth",
        "Aarde",
        "centreren, voeden en duurzaam dragen",
        ["centrum", "voeding", "ondersteuning"],
        "voedend, betrouwbaar en aanwezig",
        "vermoeidheid uit teveel verzorgen",
        "centrum en voeding",
    ),
    (
        "metal",
        "Metaal",
        "verfijning, helderheid en duidelijke grenzen",
        ["verfijning", "grens", "kwaliteit"],
        "helder, precies en bereid los te laten",
        "rigiditeit of vasthouden aan kwaliteit",
        "verfijning en grenzen",
    ),
    (
        "water",
        "Water",
        "diepte, wijsheid en stromende intu\u00eftie",
        ["diepte", "wijsheid", "intu\u00eftie"],
        "diepgaand, intu\u00eftief en bereid te stromen",
        "verlies in stemmingen of doelen vermijden",
        "diepte en wijsheid",
    ),
]


BAZI_ENTRIES: list[GlossaryEntry] = [
    {
        "key": f"bazi.element.{key}",
        "method": "bazi",
        "category": "five_element",
        "label": label,
        "shortLabel": label,
        "essence": essence,
        "keywords": keywords,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "lifeArea": life_area,
        "bodyOrEnergyLink": "BaZi vijf-elementen energetiek",
        "reflectionQuestions": [f"Waar herken ik {label.lower()}-energie?"],
        "avoidClaims": _AVOID,
    }
    for key, label, essence, keywords, balanced, shadow, life_area in _FIVE_ELEMENT_DATA
]


BAZI_ENTRIES.append(
    {
        "key": "bazi.concept.day_master",
        "method": "bazi",
        "category": "concept",
        "label": "Day Master",
        "shortLabel": "DM",
        "essence": "het dagelijkse 'ik' in BaZi: kernpolariteit en element van de dagstam",
        "keywords": ["dagstam", "kern", "polariteit"],
        "balancedExpression": "in contact met eigen kernkwaliteit",
        "shadowExpression": "kernkwaliteit verloochenen of verhardden",
        "lifeArea": "kern-identiteit binnen BaZi",
        "bodyOrEnergyLink": "energetisch zwaartepunt",
        "reflectionQuestions": ["Welke kerneigenschap herken ik in mezelf?"],
        "avoidClaims": _AVOID,
    }
)
