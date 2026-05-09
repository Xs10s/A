"""Westerse formules met Meaning Constructs.

Elke formule beschrijft hoe een combinatie van values betekenis krijgt
via gecontroleerde sjablonen. Templates gebruiken placeholders die
verwijzen naar glossary-velden, bijvoorbeeld:

    {planet.essence}, {sign.essence}, {house.lifeArea}

De Interpretation Builder vervangt deze placeholders door de
glossary-content. Er wordt geen vrije tekst gegenereerd.
"""

from __future__ import annotations

from .types import FormulaDefinition


PLANET_IN_SIGN_IN_HOUSE: FormulaDefinition = {
    "id": "western.planet_in_sign_in_house",
    "method": "western",
    "description": "Planeet in teken in huis: drie-laags expressie van een planetaire energie.",
    "inputTypes": ["planet", "sign", "house"],
    "requiredValues": [
        "western.planets.<planet>.sign",
        "western.planets.<planet>.house",
    ],
    "optionalValues": [
        "western.planets.<planet>.retrograde",
    ],
    "relationshipType": "expression_in_life_area",
    "outputSection": "core_identity",
    "glossaryKeysNeeded": ["planet", "sign", "house"],
    "meaningConstruct": {
        "valueRoles": {
            "planet": "wat actief is",
            "sign": "hoe deze energie zich uitdrukt",
            "house": "waar deze energie zichtbaar wordt",
        },
        "semanticPattern": (
            "{planet.essence} wordt gekleurd door {sign.essence} en wordt vooral "
            "zichtbaar in {house.lifeArea}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {planet.balancedExpression}, via "
            "{sign.balancedExpression}, rond {house.lifeArea}."
        ),
        "shadowTemplate": (
            "Wanneer dit uit balans raakt, kan het voelen als {sign.shadowExpression} "
            "rond {house.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Waar herken ik {sign.essence} in mijn {house.lifeArea}?",
            "Wanneer helpt dit mij groeien en wanneer wordt het te absoluut?",
        ],
    },
    "fallbackTemplate": (
        "{planet.label} in {sign.label} (huis {house.shortLabel}). "
        "{planet.essence}, gekleurd door {sign.essence}, wordt zichtbaar rond {house.lifeArea}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 2},
}


PLANET_IN_SIGN: FormulaDefinition = {
    "id": "western.planet_in_sign",
    "method": "western",
    "description": "Planeet in teken (zonder huis-context).",
    "inputTypes": ["planet", "sign"],
    "requiredValues": [
        "western.planets.<planet>.sign",
    ],
    "optionalValues": [],
    "relationshipType": "expression_in_sign",
    "outputSection": "core_identity",
    "glossaryKeysNeeded": ["planet", "sign"],
    "meaningConstruct": {
        "valueRoles": {
            "planet": "wat actief is",
            "sign": "hoe deze energie zich uitdrukt",
        },
        "semanticPattern": (
            "{planet.essence} wordt gekleurd door {sign.essence}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {planet.balancedExpression} via "
            "{sign.balancedExpression}."
        ),
        "shadowTemplate": (
            "Wanneer dit uit balans raakt, kan het voelen als {sign.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Waar herken ik {sign.essence} bij mezelf?",
        ],
    },
    "fallbackTemplate": (
        "{planet.label} in {sign.label}: {planet.essence}, gekleurd door {sign.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 1},
}


PLANET_IN_HOUSE: FormulaDefinition = {
    "id": "western.planet_in_house",
    "method": "western",
    "description": "Planeet in huis (zonder teken-context).",
    "inputTypes": ["planet", "house"],
    "requiredValues": [
        "western.planets.<planet>.house",
    ],
    "optionalValues": [],
    "relationshipType": "expression_in_life_area_only",
    "outputSection": "core_identity",
    "glossaryKeysNeeded": ["planet", "house"],
    "meaningConstruct": {
        "valueRoles": {
            "planet": "wat actief is",
            "house": "waar deze energie zichtbaar wordt",
        },
        "semanticPattern": (
            "{planet.essence} wordt vooral zichtbaar in {house.lifeArea}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {planet.balancedExpression} rond {house.lifeArea}."
        ),
        "shadowTemplate": (
            "Wanneer dit uit balans raakt, kan het schuren met {house.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Hoe herken ik {planet.essence} in mijn {house.lifeArea}?",
        ],
    },
    "fallbackTemplate": (
        "{planet.label} in huis {house.shortLabel}: {planet.essence} wordt zichtbaar in {house.lifeArea}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 1},
}


ASPECT_BETWEEN_PLANETS: FormulaDefinition = {
    "id": "western.aspect_between_planets",
    "method": "western",
    "description": "Aspect tussen twee planeten met orb-bewustheid.",
    "inputTypes": ["planet", "planet", "aspect"],
    "requiredValues": [
        "western.planets.<a>.sign",
        "western.planets.<b>.sign",
    ],
    "optionalValues": [],
    "relationshipType": "tension_or_flow",
    "outputSection": "relationships",
    "glossaryKeysNeeded": ["planet", "aspect"],
    "meaningConstruct": {
        "valueRoles": {
            "a": "eerste planetaire energie",
            "b": "tweede planetaire energie",
            "aspect": "hoekrelatie tussen de twee",
        },
        "semanticPattern": (
            "{a.essence} ontmoet {b.essence}; deze ontmoeting heeft de kwaliteit van "
            "{aspect.essence}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {aspect.balancedExpression} tussen "
            "{a.label} en {b.label}."
        ),
        "shadowTemplate": (
            "Uit balans kan dit voelen als {aspect.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Waar herken ik deze ontmoeting tussen {a.label} en {b.label}?",
        ],
    },
    "fallbackTemplate": (
        "{a.label} {aspect.label} {b.label}: {aspect.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 2},
}


ELEMENT_BALANCE_DOMINANT: FormulaDefinition = {
    "id": "western.element_balance_dominant",
    "method": "western",
    "description": "Dominant of zwak element binnen de Westerse chart.",
    "inputTypes": ["element", "score"],
    "requiredValues": [
        "western.balance.elements.fire",
        "western.balance.elements.earth",
        "western.balance.elements.air",
        "western.balance.elements.water",
    ],
    "optionalValues": [],
    "relationshipType": "balance_score",
    "outputSection": "energy",
    "glossaryKeysNeeded": ["element"],
    "meaningConstruct": {
        "valueRoles": {
            "element": "het element met de hoogste of laagste score",
        },
        "semanticPattern": (
            "Een terugkerend thema lijkt {element.essence}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {element.balancedExpression}."
        ),
        "shadowTemplate": (
            "Wanneer dit uit balans raakt, kan het schuren met {element.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Waar herken ik {element.essence} in mijn dagelijkse keuzes?",
        ],
    },
    "fallbackTemplate": (
        "Element-accent: {element.label}. Dit kan wijzen op {element.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 1},
}


ASCENDANT_PRESENTATION: FormulaDefinition = {
    "id": "western.ascendant_presentation",
    "method": "western",
    "description": "Ascendant: de manier waarop iemand binnenstapt.",
    "inputTypes": ["sign"],
    "requiredValues": ["western.ascendant.sign"],
    "optionalValues": ["western.ascendant.degree"],
    "relationshipType": "presentation_style",
    "outputSection": "expression",
    "glossaryKeysNeeded": ["sign", "angle"],
    "meaningConstruct": {
        "valueRoles": {
            "sign": "hoe deze energie zich uitdrukt aan de oppervlakte",
        },
        "semanticPattern": (
            "Je presenteert je vaak in de kleur van {sign.essence}."
        ),
        "balancedTemplate": (
            "In balans kan dit zich tonen als {sign.balancedExpression} bij eerste indruk."
        ),
        "shadowTemplate": (
            "Wanneer dit uit balans raakt, kan presentatie voelen als {sign.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Hoe stap ik nu nieuwe situaties in?",
        ],
    },
    "fallbackTemplate": (
        "Ascendant in {sign.label}: presentatie kleurt vaak in {sign.essence}."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 1},
}


NODE_DEVELOPMENTAL_DIRECTION: FormulaDefinition = {
    "id": "western.node_developmental_direction",
    "method": "western",
    "description": "Noord/Zuid-knoop: vertrouwde basis en ontwikkelrichting.",
    "inputTypes": ["sign", "house"],
    "requiredValues": [
        "western.nodes.north.sign",
        "western.nodes.south.sign",
    ],
    "optionalValues": [
        "western.nodes.north.house",
        "western.nodes.south.house",
    ],
    "relationshipType": "developmental_direction",
    "outputSection": "growth",
    "glossaryKeysNeeded": ["sign", "house", "node"],
    "meaningConstruct": {
        "valueRoles": {
            "northSign": "richting van groei",
            "southSign": "vertrouwde basis",
        },
        "semanticPattern": (
            "Een ontwikkelrichting kan liggen in {northSign.essence}, terwijl "
            "{southSign.essence} vertrouwd terrein is."
        ),
        "balancedTemplate": (
            "In balans kan dit nodigen tot {northSign.balancedExpression}, "
            "rustend op {southSign.balancedExpression}."
        ),
        "shadowTemplate": (
            "Uit balans kan men terugvallen op {southSign.shadowExpression}."
        ),
        "reflectionQuestionsTemplate": [
            "Welke richting nodigt mijn groei uit?",
            "Wat draag ik al dat mij ondersteunt onderweg?",
        ],
    },
    "fallbackTemplate": (
        "Noordknoop in {northSign.label}, Zuidknoop in {southSign.label}: "
        "een uitnodiging om vertrouwd terrein te integreren met nieuwe richting."
    ),
    "llmAllowed": True,
    "confidenceRules": {"minimumInputs": 1},
}


WESTERN_FORMULAS: list[FormulaDefinition] = [
    PLANET_IN_SIGN_IN_HOUSE,
    PLANET_IN_SIGN,
    PLANET_IN_HOUSE,
    ASPECT_BETWEEN_PLANETS,
    ELEMENT_BALANCE_DOMINANT,
    ASCENDANT_PRESENTATION,
    NODE_DEVELOPMENTAL_DIRECTION,
]
