"""BaZi / Ganzhi: pillar facts + how that layer tends to show up in life."""

from __future__ import annotations

from typing import Any

from ..knowledgebase import branch_meaning, normalize_locale, pillar_meaning, stem_meaning
from .types import ExplanationBlock, MethodExplanationBundle

_PILLAR_PERSONAL: dict[str, dict[str, str]] = {
    "year": {
        "nl": (
            "Persoonlijk: dit is vaak je buitenste verhaal (familie, context, wat je van nature meekrijgt). "
            "Minder keuze, wel invloed op hoe je groeit."
        ),
        "en": "Personally: this is often your outer story (family, context, what you inherit). Less choice, still influence on how you grow.",
    },
    "month": {
        "nl": (
            "Persoonlijk: dit werkt als carriere- of werkritme: hoe je zichtbaar wordt en welke druk je normaal voelt in teams."
        ),
        "en": "Personally: this works like career rhythm: how you become visible and what pressure you usually feel in teams.",
    },
    "day": {
        "nl": (
            "Persoonlijk: dit raakt je kern en relaties: wat je zoekt in partnerschap en hoe je jezelf opnieuw centreert."
        ),
        "en": "Personally: this touches core and partnership: what you seek in relationship and how you re-center yourself.",
    },
    "hour": {
        "nl": (
            "Persoonlijk: dit kleurt innerlijk werk, nalatenschap en wat je prive verwerkt; vaak subtieler, maar hardnekkig."
        ),
        "en": "Personally: this tints inner work, legacy, and private processing; often subtle but persistent.",
    },
}


def build_bazi_bundle(engine_json: dict[str, Any], *, locale: str) -> MethodExplanationBundle:
    lang = normalize_locale(locale)
    chinese = engine_json.get("chinese") if isinstance(engine_json.get("chinese"), dict) else {}
    bazi = chinese.get("bazi_pillars") if isinstance(chinese.get("bazi_pillars"), dict) else {}
    blocks: list[ExplanationBlock] = []

    titles = {
        "year": ("Jaarpilaar", "Year pillar"),
        "month": ("Maandpilaar", "Month pillar"),
        "day": ("Dagpilaar", "Day pillar"),
        "hour": ("Uurpilaar", "Hour pillar"),
    }

    for kind in ("year", "month", "day", "hour"):
        p = bazi.get(kind) if isinstance(bazi.get(kind), dict) else {}
        stem = p.get("stem")
        branch = p.get("branch")
        if not stem or not branch:
            continue
        base = pillar_meaning(locale, pillar_kind=kind, stem=str(stem), branch=str(branch))
        stem_txt = stem_meaning(locale, str(stem))
        branch_txt = branch_meaning(locale, str(branch))
        if lang == "nl":
            headline = (
                f"{base} De hemelse stam ({stem}) draagt: {stem_txt}. "
                f"De aardse tak ({branch}) draagt: {branch_txt}."
            )
        else:
            headline = (
                f"{base} The stem ({stem}) carries: {stem_txt}. "
                f"The branch ({branch}) carries: {branch_txt}."
            )
        personal = _PILLAR_PERSONAL.get(kind, {}).get(lang) or _PILLAR_PERSONAL.get(kind, {}).get("en", "")
        blocks.append(
            {
                "id": f"pillar_{kind}",
                "title": titles[kind][0] if lang == "nl" else titles[kind][1],
                "headline": headline,
                "personal_layer": personal,
            }
        )

    if not blocks:
        blocks.append(
            {
                "id": "empty",
                "title": "BaZi",
                "headline": (
                    "Nog geen Ganzhi-pilaren beschikbaar (controleer invoer en grenzen van de Chinese kalender)."
                    if lang == "nl"
                    else "No Ganzhi pillars yet (check inputs and Chinese calendar boundaries)."
                ),
                "personal_layer": (
                    "Persoonlijk: zodra de pilaren berekend zijn, lees je hier laag voor laag hoe je cycli je richting geven."
                    if lang == "nl"
                    else "Personally: once pillars compute, you read layer-by-layer how cycles steer you.",
                ),
            }
        )

    overview = (
        "BaZi-uitleg: jaar, maand, dag en uur zijn lagen van je patroon; niet een label, maar een samenspel."
        if lang == "nl"
        else "BaZi reading: year, month, day, and hour are layers of your pattern; not one label, but interplay."
    )
    closing = (
        "Kijk vooral naar spanning en steun tussen de pilaren; dat is waar het verhaal levend wordt."
        if lang == "nl"
        else "Watch tension and support between pillars; that is where the story comes alive."
    )

    return {
        "method_id": "chinese_ganzhi_bazi",
        "locale": locale,
        "version": "1.0.0",
        "overview": overview,
        "blocks": blocks,
        "closing_note": closing,
    }
