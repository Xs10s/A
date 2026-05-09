"""Maya glossary entries (NL) - scaffolding."""

from __future__ import annotations

from .types import GlossaryEntry


_AVOID = [
    "geen absolute uitspraken over wie iemand 'is'",
    "geen voorspellingen over de toekomst",
    "geen medische claims",
]


_SEAL_DATA = [
    ("dragon", "Drakenzegel", "voeden, oorsprong en zorg vanuit kern"),
    ("wind", "Windzegel", "communicatie en spirit dragen via taal"),
    ("night", "Nachtzegel", "diepte, droom en innerlijke schat"),
    ("seed", "Zaadzegel", "potentie tot bloei brengen"),
    ("serpent", "Slangzegel", "vitale levenskracht en transformatie"),
    ("worldbridger", "Wereld-brugzegel", "afronden en bruggen bouwen"),
    ("hand", "Handzegel", "helen door doen en aanraken"),
    ("star", "Sterzegel", "schoonheid en kunst tonen"),
    ("moon", "Maanzegel", "stromen met emotionele zuivering"),
    ("dog", "Hondzegel", "loyaliteit en hartverbinding"),
    ("monkey", "Aapzegel", "spel en magie via plezier"),
    ("human", "Mensenzegel", "vrije wil en wijsheid"),
    ("skywalker", "Hemelwandelzegel", "verkennen tussen werelden"),
    ("wizard", "Tovenaarszegel", "tijdloze aanwezigheid en betovering"),
    ("eagle", "Adelaarzegel", "overzicht en visie"),
    ("warrior", "Krijgerzegel", "vragen stellen en moedig handelen"),
    ("earth", "Aardezegel", "navigeren met natuurlijke stromen"),
    ("mirror", "Spiegelzegel", "reflecteren en orde scheppen"),
    ("storm", "Stormzegel", "vernieuwen en katalyseren"),
    ("sun", "Zonzegel", "verlichting en universele liefde"),
]


MAYA_ENTRIES: list[GlossaryEntry] = [
    {
        "key": f"maya.seal.{slug}",
        "method": "maya",
        "category": "seal",
        "label": label,
        "shortLabel": label,
        "essence": essence,
        "keywords": ["zonnezegel", slug],
        "balancedExpression": "energie van het zegel inzetten in dagelijkse keuzes",
        "shadowExpression": "vereenzelviging zonder reflectie",
        "lifeArea": "archetypisch dagelijks thema",
        "bodyOrEnergyLink": "Maya-archetypische energie",
        "reflectionQuestions": [f"Hoe herken ik {label.lower()}-energie vandaag?"],
        "avoidClaims": _AVOID,
    }
    for slug, label, essence in _SEAL_DATA
]


MAYA_ENTRIES.append(
    {
        "key": "maya.concept.tone",
        "method": "maya",
        "category": "tone",
        "label": "Galactische toon",
        "shortLabel": "Toon",
        "essence": "een nummer van 1-13 dat het ritme of de fase van de cyclus aangeeft",
        "keywords": ["ritme", "fase", "cyclus"],
        "balancedExpression": "afstemmen op de fase van de cyclus",
        "shadowExpression": "tegen de fase in willen werken",
        "lifeArea": "cyclisch ritme",
        "bodyOrEnergyLink": "cyclische energie",
        "reflectionQuestions": ["Welke fase van mijn cyclus voel ik?"],
        "avoidClaims": _AVOID,
    }
)
