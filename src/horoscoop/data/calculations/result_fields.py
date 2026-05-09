from __future__ import annotations

ResultFieldDefinition = dict[str, object]


RESULT_FIELD_DEFINITIONS: list[ResultFieldDefinition] = [
    {
        "id": "western.personal.ascendant",
        "kind": "variable",
        "method": "western",
        "calculationIds": ["western.calculate.angles"],
        "requiredInputs": ["birthDate", "birthTime", "birthPlace"],
        "requiredCalculatedValues": ["western.ascendant.sign", "western.ascendant.degree"],
        "templateId": "western.template.ascendant",
        "fallback": {
            "missingInput": "De ascendant kan nog niet worden berekend, omdat hiervoor geboortetijd en geboorteplaats nodig zijn.",
            "calculationFailed": "De ascendant kon niet betrouwbaar worden berekend. Controleer de geboortegegevens.",
        },
    },
    {
        "id": "vedic.personal.panchanga",
        "kind": "variable",
        "method": "vedic",
        "calculationIds": ["vedic.calculate.panchanga"],
        "requiredInputs": ["birthDate", "birthTime"],
        "requiredCalculatedValues": ["vedic.panchanga.tithi", "vedic.panchanga.vaara", "vedic.panchanga.nakshatra"],
        "templateId": "vedic.template.panchanga",
        "fallback": {
            "missingInput": "Voor Panchanga zijn geboortedatum en geboortetijd nodig.",
            "calculationFailed": "Panchanga kon niet worden opgebouwd met de huidige invoer.",
        },
    },
    {
        "id": "bazi.personal.four-pillars",
        "kind": "variable",
        "method": "bazi",
        "calculationIds": ["bazi.calculate.four-pillars"],
        "requiredInputs": ["birthDate", "birthTime", "timezone"],
        "requiredCalculatedValues": ["bazi.pillars.year.stem", "bazi.pillars.year.branch", "bazi.pillars.day.stem", "bazi.pillars.day.branch"],
        "templateId": "bazi.template.four-pillars",
        "fallback": {
            "missingInput": "Voor de vier pilaren zijn geboortedatum, geboortetijd en tijdzone nodig.",
            "calculationFailed": "De vier pilaren konden niet betrouwbaar worden berekend.",
        },
    },
    {
        "id": "human-design.personal.type",
        "kind": "variable",
        "method": "human-design",
        "calculationIds": ["human-design.calculate.type"],
        "requiredInputs": ["birthDate", "birthTime", "timezone", "coordinates"],
        "requiredCalculatedValues": ["human-design.type"],
        "templateId": "human-design.template.type",
        "fallback": {
            "missingInput": "Voor Human Design type zijn datum, tijd, tijdzone en coordinaten nodig.",
            "calculationFailed": "Human Design type kon niet betrouwbaar worden vastgesteld.",
        },
    },
    {
        "id": "maya.personal.signature",
        "kind": "variable",
        "method": "maya",
        "calculationIds": ["maya.calculate.galactic-signature"],
        "requiredInputs": ["birthDate"],
        "requiredCalculatedValues": ["maya.signature.name", "maya.kin.number"],
        "templateId": "maya.template.signature",
        "fallback": {
            "missingInput": "Voor de Maya-signatuur is minimaal geboortedatum nodig.",
            "calculationFailed": "Maya-signatuur kon niet betrouwbaar worden berekend.",
        },
    },
    {
        "id": "energy-profile.summary",
        "kind": "variable",
        "method": "energy-profile",
        "calculationIds": ["energy-profile.generate.summary"],
        "requiredInputs": [],
        "requiredCalculatedValues": ["energy-profile.summary.available"],
        "templateId": "energy-profile.template.summary",
        "fallback": {
            "missingInput": "Er zijn onvoldoende geldige methode-resultaten voor een energieprofielsamenvatting.",
            "calculationFailed": "Energieprofielsamenvatting kon niet worden opgebouwd.",
        },
    },
]

