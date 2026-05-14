"""Centrale promptlogica voor de narrative LLM-vertaalbrug.

Belangrijk: de prompt geeft NOOIT de LLM toestemming om astrologische
betekenis te verzinnen. De LLM mag alleen:
    - De gegeven InterpretationPoints en glossary-context herformuleren
      naar vloeiende Nederlandse tekst.
    - De toon en lengte aanpassen.
    - De stijl-eisen volgen ("dit kan wijzen op...", niet absoluut, etc.).

Toegestane inhoud is beperkt tot wat de app zelf toont: de teksten op de
kaarten in de blokken van de persoonlijke horoscoop en dezelfde
chart-afgeleide waarden in de visuele weergave (radix, kundali, vedic,
human design, enz.). Dit JSON-bericht is de gestructureerde weergave
daarvan; de LLM mag geen parallelle bronnen of ontbrekende chartdetails
invullen.

De prompt is gestructureerd in JSON-achtige secties zodat hij
versie-bewaakt en deterministisch is.
"""

from __future__ import annotations

import json

from .types import NarrativeRequest


PROMPT_VERSION = "1.0.1"


SYSTEM_INSTRUCTION_NL = (
    "Je bent een Nederlandstalige tekstvertaler voor een astrologie-/energieprofiel-app. "
    "Jouw enige taak is het herformuleren van GEGEVEN interpretatiepunten naar warme, "
    "uitnodigende Nederlandse tekst.\n"
    "BRONNEN (enkel dit bericht): De inhoud komt overeen met de kaarten in de blokken van "
    "de persoonlijke horoscoop en met de waarden die in de visuele chart staan (radix, "
    "kundali, vedic, human design, chinese/bazi, maya, enz.). Gebruik uitsluitend wat hier "
    "in interpretatiepunten, glossary-context en synthesis-punten staat; vul niets aan "
    "vanuit algemene astrologische kennis of ontbrekende chartgegevens.\n"
    "STRENG VERBODEN:\n"
    "- Astrologische betekenis verzinnen of toevoegen die niet in de gegeven punten of glossary staat.\n"
    "- Berekeningen maken of aannames doen over geboortedata.\n"
    "- Absolute uitspraken doen over wie iemand 'is'.\n"
    "- Voorspellingen doen over de toekomst.\n"
    "- Medische, financiele, juridische of psychologische adviezen geven.\n"
    "STRENG VERPLICHT:\n"
    "- Schrijf in het Nederlands.\n"
    "- Gebruik uitnodigende formuleringen: 'dit kan wijzen op...', 'mogelijk herken je...', "
    "'in balans kan dit zich tonen als...', 'wanneer dit uit balans raakt...'.\n"
    "- Houd de inhoud strikt binnen de gegeven interpretatiepunten en glossary-context.\n"
    "- Vermeld geen externe astrologische bronnen.\n"
)


def _summarize_glossary(glossary_context: list[dict]) -> list[dict]:
    out = []
    for entry in glossary_context or []:
        out.append(
            {
                "key": entry.get("key"),
                "label": entry.get("label"),
                "essence": entry.get("essence"),
                "balancedExpression": entry.get("balancedExpression"),
                "shadowExpression": entry.get("shadowExpression"),
                "lifeArea": entry.get("lifeArea"),
                "avoidClaims": entry.get("avoidClaims"),
            }
        )
    return out


def build_prompt(request: NarrativeRequest) -> dict[str, str]:
    """Bouw een controleerbare prompt voor de LLM.

    Retourneert dict met:
        - "system": systeemprompt
        - "user"  : user-bericht (JSON-encoded payload)
    """
    payload = {
        "promptVersion": PROMPT_VERSION,
        "sourceContract": {
            "allowed": [
                "Teksten die overeenkomen met de kaarten in de blokken van de persoonlijke horoscoop "
                "(weergegeven als interpretationPoints en gerelateerde glossary-context).",
                "Chart-afgeleide waarden die de app in de visuele chart toont (radix, kundali, vedic, "
                "human design, chinese/bazi, maya, enz.), voor zover ze in dit bericht verwerkt zijn.",
            ],
            "forbidden": [
                "Aanvullen met algemene astrologische kennis die niet in dit bericht staat.",
                "Planeten, tekens, huizen, aspecten of tijden noemen die niet uit deze bronnen volgen.",
            ],
        },
        "section": request.get("section"),
        "method": request.get("method"),
        "tone": request.get("tone", "warm"),
        "length": request.get("length", "medium"),
        "locale": request.get("locale", "nl"),
        "interpretationPoints": [
            {
                "formulaId": p.get("formulaId"),
                "section": p.get("section"),
                "technicalLabel": p.get("technicalLabel"),
                "humanMeaning": p.get("humanMeaning"),
                "balancedExpression": p.get("balancedExpression"),
                "shadowExpression": p.get("shadowExpression"),
                "reflectionQuestions": p.get("reflectionQuestions"),
                "glossarySources": p.get("glossarySources"),
            }
            for p in request.get("interpretationPoints", []) or []
        ],
        "glossaryContext": _summarize_glossary(request.get("glossaryContext") or []),
        "synthesisPoints": request.get("synthesisPoints") or [],
        "instructions": [
            "Herformuleer de bovenstaande interpretatiepunten als vloeiende Nederlandse tekst.",
            "Beperk je strikt tot de kaart-teksten en chartwaarden die dit bericht representeert "
            "(persoonlijke-horoscoopblokken en zichtbare chart; geen extra planeten, tekens, "
            "huizen of data verzinnen).",
            "Volg de gevraagde toon en lengte.",
            "Voeg geen astrologische uitspraken toe die niet hierboven staan.",
            "Sluit af met een uitnodiging tot reflectie als dat passend is.",
        ],
    }
    return {
        "system": SYSTEM_INSTRUCTION_NL,
        "user": json.dumps(payload, ensure_ascii=False, sort_keys=True),
    }
