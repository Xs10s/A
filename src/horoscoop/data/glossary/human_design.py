"""Human Design glossary entries (NL) - scaffolding."""

from __future__ import annotations

from .types import GlossaryEntry


_AVOID = [
    "geen absolute uitspraken over wie iemand 'is'",
    "geen voorspellingen over de toekomst",
    "geen medische claims",
    "Human Design is een reflectiemodel; geen vervanging voor professioneel advies",
]


_TYPE_DATA = [
    ("manifestor", "Manifestor", "initiatie en impuls geven aan iets nieuws", "krachtig in initiatie", "stuiteren tegen weerstand zonder informeren", ["initi\u00ebren", "informeren"]),
    ("generator", "Generator", "responderen op wat het lijf aantrekt", "duurzame energie in respons", "doorduwen zonder respons", ["respons", "energie"]),
    ("manifesting-generator", "Manifesterende Generator", "snel schakelen tussen impulsen die het lijf bevestigt", "snel en effectief schakelen", "stappen overslaan en daardoor frustreren", ["respons", "snelheid"]),
    ("projector", "Projector", "ander leiden door uitnodiging te krijgen en te geven", "scherp inzicht in anderen", "doorduwen zonder uitgenodigd te zijn", ["uitnodiging", "leiding"]),
    ("reflector", "Reflector", "spiegelen wat in de omgeving leeft", "diep helder over groepsenergie", "vereenzelviging met de groep", ["spiegel", "omgeving"]),
]


TYPE_ENTRIES: list[GlossaryEntry] = [
    {
        "key": f"human-design.type.{slug}",
        "method": "human-design",
        "category": "type",
        "label": label,
        "shortLabel": label,
        "essence": essence,
        "keywords": keywords,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "lifeArea": "energie- en beslissingsstijl",
        "bodyOrEnergyLink": "energetische bouw",
        "reflectionQuestions": [f"Hoe herken ik mijn {label.lower()}-energie in keuzes?"],
        "avoidClaims": _AVOID,
    }
    for slug, label, essence, balanced, shadow, keywords in _TYPE_DATA
]


_AUTHORITY_DATA = [
    ("emotional", "Emotionele autoriteit", "wachten tot de emotionele golf duidelijkheid geeft"),
    ("sacral", "Sacrale autoriteit", "luisteren naar de sacrale 'ja' of 'nee'"),
    ("splenic", "Splenic autoriteit", "luisteren naar het zachte, intuitieve 'nu-signaal'"),
    ("ego", "Ego autoriteit", "kiezen vanuit wat het hart-ego echt wil dragen"),
    ("self-projected", "Zelf-geprojecteerde autoriteit", "horen wat je zegt en luisteren of het klopt"),
    ("mental", "Mental projector autoriteit", "klankborden met vertrouwde anderen"),
    ("lunar", "Lunaire autoriteit", "een maancyclus afwachten voor grote keuzes"),
]


AUTHORITY_ENTRIES: list[GlossaryEntry] = [
    {
        "key": f"human-design.authority.{slug}",
        "method": "human-design",
        "category": "authority",
        "label": label,
        "shortLabel": label,
        "essence": essence,
        "keywords": ["autoriteit", "beslissen"],
        "balancedExpression": "beslissen in lijn met deze autoriteit",
        "shadowExpression": "via mental geluid beslissen tegen deze autoriteit in",
        "lifeArea": "beslissingen",
        "bodyOrEnergyLink": "lichaamswijsheid",
        "reflectionQuestions": ["Welke beslissing wacht op de juiste timing?"],
        "avoidClaims": _AVOID,
    }
    for slug, label, essence in _AUTHORITY_DATA
]


HUMAN_DESIGN_ENTRIES: list[GlossaryEntry] = TYPE_ENTRIES + AUTHORITY_ENTRIES
