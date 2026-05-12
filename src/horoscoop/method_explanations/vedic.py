"""Vedic Panchanga: each factor gets factual text + a personal reading layer."""

from __future__ import annotations

from typing import Any

from ..knowledgebase import (
    karana_meaning,
    nakshatra_meaning,
    normalize_locale,
    tithi_meaning,
    vaara_meaning,
    yoga_meaning,
)
from .types import ExplanationBlock, MethodExplanationBundle


def _personal_wrap(lang: str, *, topic: str) -> str:
    if lang == "nl":
        return (
            f"Persoonlijk ({topic}): dit kleurt hoe je een dag ervaart; niet als lot, "
            "maar als stemming en tempo. Merk op wanneer dit herkenbaar terugkomt in je ritme."
        )
    return (
        f"Personally ({topic}): this tints how a day feels; not fate, but tone and tempo. "
        "Notice when it shows up in your rhythm."
    )


def build_vedic_panchanga_bundle(engine_json: dict[str, Any], *, locale: str) -> MethodExplanationBundle:
    lang = normalize_locale(locale)
    vedic = engine_json.get("vedic") if isinstance(engine_json.get("vedic"), dict) else {}
    panchanga = vedic.get("panchanga") if isinstance(vedic.get("panchanga"), dict) else {}
    blocks: list[ExplanationBlock] = []

    vaara = panchanga.get("vaara")
    if isinstance(vaara, str) and vaara:
        base = vaara_meaning(locale, vaara)
        blocks.append(
            {
                "id": "vaara",
                "title": "Vaara" if lang == "nl" else "Weekday quality",
                "headline": base,
                "personal_layer": _personal_wrap(lang, topic="weekdag" if lang == "nl" else "weekday"),
            }
        )

    tithi = panchanga.get("tithi") if isinstance(panchanga.get("tithi"), dict) else {}
    if tithi.get("index") is not None:
        idx = tithi.get("index")
        base = tithi_meaning(locale, idx)
        blocks.append(
            {
                "id": "tithi",
                "title": "Tithi",
                "headline": base,
                "personal_layer": _personal_wrap(lang, topic="maanfase" if lang == "nl" else "lunar phase layer"),
            }
        )

    nak = panchanga.get("nakshatra") if isinstance(panchanga.get("nakshatra"), dict) else {}
    if nak.get("index") is not None:
        idx = nak.get("index")
        base = nakshatra_meaning(locale, idx)
        blocks.append(
            {
                "id": "nakshatra",
                "title": "Nakshatra",
                "headline": base,
                "personal_layer": _personal_wrap(lang, topic="emotionele grondtoon" if lang == "nl" else "emotional undertone"),
            }
        )

    yoga = panchanga.get("yoga") if isinstance(panchanga.get("yoga"), dict) else {}
    if yoga.get("index") is not None:
        idx = yoga.get("index")
        base = yoga_meaning(locale, idx)
        blocks.append(
            {
                "id": "yoga",
                "title": "Yoga",
                "headline": base,
                "personal_layer": _personal_wrap(lang, topic="dagthema" if lang == "nl" else "day theme"),
            }
        )

    karana = panchanga.get("karana") if isinstance(panchanga.get("karana"), dict) else {}
    kidx = karana.get("indices") if isinstance(karana.get("indices"), list) else None
    if kidx:
        base = karana_meaning(locale, kidx[0])
        blocks.append(
            {
                "id": "karana",
                "title": "Karana",
                "headline": base,
                "personal_layer": _personal_wrap(lang, topic="overgang" if lang == "nl" else "transition"),
            }
        )

    if not blocks:
        blocks.append(
            {
                "id": "empty",
                "title": "Panchanga",
                "headline": (
                    "Nog geen Panchanga-waarden beschikbaar voor deze berekening."
                    if lang == "nl"
                    else "No Panchanga values available for this calculation yet."
                ),
                "personal_layer": (
                    "Persoonlijk: zodra tijd en kalenderdata compleet zijn, vullen deze blokken zich met jouw momentkwaliteit."
                    if lang == "nl"
                    else "Personally: once time and calendar inputs are complete, these blocks fill with your moment quality.",
                ),
            }
        )

    overview = (
        "Vedische uitleg: Panchanga beschrijft de kwaliteit van het geboortemoment als tijd; los van westerse planetenposities."
        if lang == "nl"
        else "Vedic reading: Panchanga describes birth-moment quality as time; separate from Western planetary positions."
    )
    closing = (
        "Lees dit als ritme en stemming: het helpt patronen te herkennen in energie en timing."
        if lang == "nl"
        else "Read this as rhythm and tone: it helps you notice patterns in energy and timing."
    )

    return {
        "method_id": "vedic_panchanga",
        "locale": locale,
        "version": "1.0.0",
        "overview": overview,
        "blocks": blocks,
        "closing_note": closing,
    }
