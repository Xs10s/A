"""Tzolkin / Maya kin: symbolic facts + personal meaning hooks."""

from __future__ import annotations

from typing import Any

from ..knowledgebase import normalize_locale
from .types import ExplanationBlock, MethodExplanationBundle


def build_maya_bundle(engine_json: dict[str, Any], *, locale: str) -> MethodExplanationBundle:
    lang = normalize_locale(locale)
    maya = engine_json.get("maya") if isinstance(engine_json.get("maya"), dict) else {}
    blocks: list[ExplanationBlock] = []

    kin = maya.get("kin")
    sign = maya.get("sign") if isinstance(maya.get("sign"), dict) else {}
    tone = maya.get("tone") if isinstance(maya.get("tone"), dict) else {}
    wave = maya.get("wavespell") if isinstance(maya.get("wavespell"), dict) else {}
    haab = maya.get("haab") if isinstance(maya.get("haab"), dict) else {}
    lc = maya.get("long_count") if isinstance(maya.get("long_count"), dict) else {}

    if kin is not None:
        snl = sign.get("nl") or sign.get("en") or ""
        sen = sign.get("en") or sign.get("nl") or ""
        kw = sign.get("kw_nl") if lang == "nl" else sign.get("kw_en")
        tnl = tone.get("name_nl") or tone.get("name_en") or ""
        ten = tone.get("name_en") or tone.get("name_nl") or ""
        tone_kw = tone.get("kw_nl") if lang == "nl" else tone.get("kw_en")
        if lang == "nl":
            headline = (
                f"Je kin is {kin}: {tnl} {snl}. Kernkwaliteit van het teken: {kw}. "
                f"Toon: {tone_kw}."
            )
        else:
            headline = (
                f"Your kin is {kin}: {ten} {sen}. Sign core quality: {kw}. "
                f"Tone: {tone_kw}."
            )
        if lang == "nl":
            personal = (
                "Persoonlijk: het teken geeft een archetypische toon; de toon bepaalt hoe je die toon "
                "uitspreekt (vast, licht, uitdagend, enz.). Zoek herkenning in kleine dagelijkse keuzes, niet in labels."
            )
        else:
            personal = (
                "Personally: the sign gives an archetypal tone; the tone shapes how you express it "
                "(steady, light, challenging, etc.). Look for recognition in small daily choices, not labels."
            )
        blocks.append({"id": "kin_core", "title": "Tzolkin", "headline": headline, "personal_layer": personal})

    if wave and (wave.get("number") is not None or wave.get("label")):
        label = wave.get("label") or str(wave.get("number"))
        if lang == "nl":
            h = f"Wavespell-context: {label}. Dit plaatst je kin in een 13-daags ritme met een gedeelde leerlijn."
            p = (
                "Persoonlijk: merk in een wavespell welke thema's terugkeren; "
                "dat is je 'les van de week' in zachte vorm."
            )
        else:
            h = f"Wavespell context: {label}. This places your kin in a 13-day rhythm with a shared learning line."
            p = "Personally: notice repeating themes across a wavespell; that is your soft weekly lesson."
        blocks.append({"id": "wavespell", "title": "Wavespell", "headline": h, "personal_layer": p})

    if haab and haab.get("label"):
        if lang == "nl":
            h = f"Haab (zonnejaar): {haab.get('label')}. Dit verbindt je met het agrarische/seizoensritme van de Maya-kalender."
            p = "Persoonlijk: denk aan lichaam, seizoen, eenvoudige routines: waar haal je grond onder je voeten vandaan?"
        else:
            h = f"Haab (solar year): {haab.get('label')}. This ties you to the seasonal rhythm of the Maya calendar."
            p = "Personally: think body, season, simple routines: where do you find ground under your feet?"
        blocks.append({"id": "haab", "title": "Haab", "headline": h, "personal_layer": p})

    if lc and lc.get("label"):
        if lang == "nl":
            h = f"Lange telling: {lc.get('label')}."
            p = (
                "Persoonlijk: dit is de 'grote datum': meer kosmisch decor dan dagelijks handboek; "
                "gebruik het als perspectief, niet als druk."
            )
        else:
            h = f"Long count: {lc.get('label')}."
            p = "Personally: this is the 'big date': more cosmic backdrop than daily manual; use it for perspective, not pressure."
        blocks.append({"id": "long_count", "title": "Lange telling" if lang == "nl" else "Long count", "headline": h, "personal_layer": p})

    if not blocks:
        blocks.append(
            {
                "id": "empty",
                "title": "Maya",
                "headline": (
                    "Maya-kalender nog niet beschikbaar (datum nodig)."
                    if lang == "nl"
                    else "Maya calendar not available yet (date required)."
                ),
                "personal_layer": (
                    "Persoonlijk: zodra de kin berekend is, lees je hier ritme en archetypen als spiegel."
                    if lang == "nl"
                    else "Personally: once the kin computes, you read rhythm and archetypes as a mirror.",
                ),
            }
        )

    overview = (
        "Maya-uitleg: Tzolkin (kin + toon), wavespell, Haab en lange telling vullen elkaar aan; klein ritme en groot perspectief."
        if lang == "nl"
        else "Maya reading: Tzolkin (kin + tone), wavespell, Haab, and long count complement; small rhythm and big view."
    )
    closing = (
        "Gebruik Maya als taal voor timing en zingeving, niet als vast label."
        if lang == "nl"
        else "Use Maya as language for timing and meaning, not a fixed label."
    )

    return {
        "method_id": "maya",
        "locale": locale,
        "version": "1.0.0",
        "overview": overview,
        "blocks": blocks,
        "closing_note": closing,
    }
