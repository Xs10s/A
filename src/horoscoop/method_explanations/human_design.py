"""Human Design: type/authority/strategy as facts + embodied personal guidance."""

from __future__ import annotations

from typing import Any

from ..knowledgebase import normalize_locale
from .types import ExplanationBlock, MethodExplanationBundle

_TYPE_PERSONAL: dict[str, dict[str, str]] = {
    "Manifestor": {
        "nl": "Persoonlijk: impact en initiatief voelen natuurlijk; irritatie ontstaat als je moet wachten op toestemming. Oefen met informeren zonder jezelf te verkleinen.",
        "en": "Personally: impact and initiative feel natural; friction grows when you must wait for permission. Practice informing without shrinking.",
    },
    "Generator": {
        "nl": (
            "Persoonlijk: duurzaamheid en respons voeden je; leegloop komt van 'moeten' en ja zeggen vanuit schuld. "
            "Je lichaam is je kompas."
        ),
        "en": "Personally: sustainability and response feed you; burnout comes from forcing yes from guilt. Your body is the compass.",
    },
    "Manifesting Generator": {
        "nl": "Persoonlijk: snelheid en veelheid horen bij jou; chaos ontstaat als je niet terugcheckt met je sacrale ja/nee na een sprint.",
        "en": "Personally: speed and multiplicity fit you; chaos comes when you skip the sacral yes/no check after a sprint.",
    },
    "Projector": {
        "nl": "Persoonlijk: zie je diepte en systemen snel; bitterheid groeit als je je niet uitgenodigd voelt. Wacht op erkenning, niet op validatie.",
        "en": "Personally: you see systems and depth fast; bitterness grows when you feel unseen. Wait for invitation, not validation.",
    },
    "Reflector": {
        "nl": "Persoonlijk: je spiegelt omgeving en tijd; beslissingen worden beter na een maanritme. Minder haast, meer monsters van plaats.",
        "en": "Personally: you mirror environment and time; decisions clarify across a lunar rhythm. Less rush, more sampling places.",
    },
}


def build_human_design_bundle(engine_json: dict[str, Any], *, locale: str) -> MethodExplanationBundle:
    lang = normalize_locale(locale)
    hd = engine_json.get("human_design") if isinstance(engine_json.get("human_design"), dict) else {}
    blocks: list[ExplanationBlock] = []

    type_str = hd.get("type")
    if isinstance(type_str, str) and type_str:
        strat = hd.get("strategy") if isinstance(hd.get("strategy"), dict) else {}
        strat_text = strat.get("text") or ""
        auth = hd.get("authority")
        prof = (hd.get("profile") or {}).get("value") if isinstance(hd.get("profile"), dict) else None
        cross = (hd.get("incarnation_cross") or {}).get("name_short") if isinstance(hd.get("incarnation_cross"), dict) else None

        if lang == "nl":
            headline = (
                f"Je type is {type_str}. Strategie: {strat_text}. Authoriteit: {auth}. "
                f"Profiel: {prof}. Thema-kruis: {cross}."
            )
        else:
            headline = (
                f"Your type is {type_str}. Strategy: {strat_text}. Authority: {auth}. "
                f"Profile: {prof}. Incarnation cross: {cross}."
            )
        personal = _TYPE_PERSONAL.get(type_str, {}).get(lang) or _TYPE_PERSONAL.get(type_str, {}).get("en", "")
        if lang == "nl":
            personal += (
                f" Authoriteit ({auth}) zegt welke innerlijke stem eerst krijgt bij keuzes; oefen daar bewust mee."
                if auth
                else ""
            )
        else:
            personal += (
                f" Authority ({auth}) names which inner voice leads decisions; practice with it intentionally."
                if auth
                else ""
            )
        blocks.append(
            {
                "id": "type_core",
                "title": "Type & besluitvorming" if lang == "nl" else "Type & decisions",
                "headline": headline,
                "personal_layer": personal,
                "reflection_questions": [
                    "Waar merk je je strategie het laatst in je week?"
                    if lang == "nl"
                    else "Where do you notice your strategy least in your week?",
                ],
            }
        )

        defined = (hd.get("centers") or {}).get("defined") if isinstance(hd.get("centers"), dict) else None
        undefined = (hd.get("centers") or {}).get("undefined") if isinstance(hd.get("centers"), dict) else None
        if isinstance(defined, list) and defined:
            if lang == "nl":
                h2 = (
                    f"Vaste centra: {', '.join(defined)}. Open centra: {', '.join(undefined or [])}. "
                    "Vast = consistente thema's; open = leerplekken waar je de wereld proeft."
                )
                p2 = (
                    "Persoonlijk: open centra zijn geen 'zwakte': ze zijn waar je wijs wordt van anderen, "
                    "mits je niet alles als waarheid aanneemt."
                )
            else:
                h2 = (
                    f"Defined centers: {', '.join(defined)}. Open centers: {', '.join(undefined or [])}. "
                    "Defined = consistent themes; open = learning where you sample the world."
                )
                p2 = (
                    "Personally: open centers are not weakness; they are where you learn from others "
                    "if you do not swallow every voice as truth."
                )
            blocks.append({"id": "centers", "title": "Centra", "headline": h2, "personal_layer": p2})

    if not blocks:
        blocks.append(
            {
                "id": "empty",
                "title": "Human Design",
                "headline": (
                    "Human Design is nog niet beschikbaar (betrouwbare geboortetijd nodig)."
                    if lang == "nl"
                    else "Human Design is not available yet (reliable birth time required)."
                ),
                "personal_layer": (
                    "Persoonlijk: zodra tijd klopt, verschijnen type en authoriteit als leidraad voor energie en keuzes."
                    if lang == "nl"
                    else "Personally: once time is solid, type and authority appear as guides for energy and choices.",
                ),
            }
        )

    overview = (
        "Human-Design-uitleg: bodygraph + type/authoriteit vertellen hoe energie stroomt en hoe je wijzer beslist."
        if lang == "nl"
        else "Human Design reading: bodygraph plus type/authority describe energy flow and wiser decisions."
    )
    closing = (
        "Experimenteer een week met strategie en authoriteit; ervaring wint van theorie."
        if lang == "nl"
        else "Experiment one week with strategy and authority; experience beats theory."
    )

    return {
        "method_id": "human_design",
        "locale": locale,
        "version": "1.0.0",
        "overview": overview,
        "blocks": blocks,
        "closing_note": closing,
    }
