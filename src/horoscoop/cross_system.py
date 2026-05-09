"""
Cross-system intelligence layer.

Goal: produce ONE coherent energy profile that resonates across Western,
Vedic, BaZi, Human Design, and Maya methods. This module does NOT compute
new astronomical data; it CONSUMES the engine output and the per-system
energy profiles, finds resonances and tensions, and emits human-readable
narrative blocks.

Resonance dimensions detected:
    - element_dominance     (fire / earth / air / water + bazi 5-element + maya day-sign element)
    - polarity              (yin/yang across BaZi stem, Maya, HD type-bias)
    - timing_cycles         (Vedic dasha hint, BaZi luck pillar, Maya wavespell, transits)
    - decision_pattern      (HD authority + Vedic Moon + Western Moon)
    - energy_management     (HD type + BaZi day master + Western Sun)
    - relational_pattern    (Western Venus, BaZi affinity, HD channels touching G/Throat)

The output is intentionally lean and structured so the UI / interpretation
layer can render it as cards, lists, or paragraphs. All texts are
generated in NL or EN.

ASCII-only source: special characters in NL strings are written using
\\u escape sequences to keep this file robust across platform encodings.
"""
from __future__ import annotations

from typing import Any, Optional

from .knowledgebase import normalize_locale as _norm_locale


# -----------------------------------------------------------------------------
# Element extraction helpers (per system)
# -----------------------------------------------------------------------------


_WESTERN_SIGN_ELEMENT: dict[str, str] = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

# BaZi 10 stems use diacritics in chinese.STEMS; we mirror the exact strings
# via Unicode escapes so this file is stable regardless of source encoding.
_BAZI_STEM_ELEMENT: dict[str, str] = {
    "Ji\u01ce": "wood", "Y\u01d0": "wood",
    "B\u01d0ng": "fire", "D\u012bng": "fire",
    "W\u00f9": "earth", "J\u01d0": "earth",
    "G\u0113ng": "metal", "X\u012bn": "metal",
    "R\u00e9n": "water", "Gu\u01d0": "water",
}

_BAZI_STEM_POLARITY: dict[str, str] = {
    "Ji\u01ce": "yang", "Y\u01d0": "yin",
    "B\u01d0ng": "yang", "D\u012bng": "yin",
    "W\u00f9": "yang", "J\u01d0": "yin",
    "G\u0113ng": "yang", "X\u012bn": "yin",
    "R\u00e9n": "yang", "Gu\u01d0": "yin",
}


def _western_dominant_element(engine_json: dict[str, Any]) -> Optional[str]:
    western = engine_json.get("western") or {}
    placements = western.get("placements") or {}
    if not isinstance(placements, dict):
        return None
    counts: dict[str, int] = {}
    for body, p in placements.items():
        if not isinstance(p, dict):
            continue
        elem = _WESTERN_SIGN_ELEMENT.get(p.get("sign"))
        if elem:
            counts[elem] = counts.get(elem, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _bazi_day_master_element(engine_json: dict[str, Any]) -> Optional[str]:
    chinese = engine_json.get("chinese") or {}
    bazi = chinese.get("bazi_pillars") or {}
    day = bazi.get("day") if isinstance(bazi, dict) else None
    if not isinstance(day, dict):
        return None
    return _BAZI_STEM_ELEMENT.get(day.get("stem"))


def _bazi_day_master_polarity(engine_json: dict[str, Any]) -> Optional[str]:
    chinese = engine_json.get("chinese") or {}
    bazi = chinese.get("bazi_pillars") or {}
    day = bazi.get("day") if isinstance(bazi, dict) else None
    if not isinstance(day, dict):
        return None
    return _BAZI_STEM_POLARITY.get(day.get("stem"))


def _maya_element(engine_json: dict[str, Any]) -> Optional[str]:
    maya = engine_json.get("maya") or {}
    sign = maya.get("sign") or {}
    return sign.get("element") if isinstance(sign, dict) else None


def _maya_polarity(engine_json: dict[str, Any]) -> Optional[str]:
    maya = engine_json.get("maya") or {}
    sign = maya.get("sign") or {}
    return sign.get("polarity") if isinstance(sign, dict) else None


def _hd_element_bias(engine_json: dict[str, Any]) -> Optional[str]:
    hd = engine_json.get("human_design") or {}
    auth = hd.get("authority")
    type_ = hd.get("type")
    if auth == "Emotional":
        return "water"
    if auth == "Sacral":
        return "fire"
    if auth == "Splenic":
        return "earth"
    if auth == "Ego":
        return "fire"
    if auth == "Self-projected":
        return "air"
    if auth == "Mental":
        return "air"
    if auth == "Lunar":
        return "water"
    if type_ == "Manifestor":
        return "fire"
    return None


def _vedic_moon_nakshatra(engine_json: dict[str, Any]) -> Optional[int]:
    vedic = engine_json.get("vedic") or {}
    pan = vedic.get("panchanga") or {}
    nak = pan.get("nakshatra") or {}
    if isinstance(nak, dict):
        idx = nak.get("index")
        return int(idx) if isinstance(idx, int) else None
    return None


# -----------------------------------------------------------------------------
# Resonance computation
# -----------------------------------------------------------------------------


def element_resonance(engine_json: dict[str, Any]) -> dict[str, Any]:
    systems = {
        "western": _western_dominant_element(engine_json),
        "bazi": _bazi_day_master_element(engine_json),
        "maya": _maya_element(engine_json),
        "hd": _hd_element_bias(engine_json),
    }
    counts: dict[str, int] = {}
    for s, elem in systems.items():
        if not elem:
            continue
        counts[elem] = counts.get(elem, 0) + 1
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else None
    agreements = [s for s, e in systems.items() if e == dominant]
    return {
        "systems": systems,
        "counts": counts,
        "dominant": dominant,
        "agreements": agreements,
        "agreement_score": len(agreements),
    }


def polarity_resonance(engine_json: dict[str, Any]) -> dict[str, Any]:
    bazi_pol = _bazi_day_master_polarity(engine_json)
    maya_pol = _maya_polarity(engine_json)
    hd_type = (engine_json.get("human_design") or {}).get("type")
    hd_pol = None
    if hd_type in ("Manifestor", "Manifesting Generator"):
        hd_pol = "yang"
    elif hd_type in ("Projector", "Reflector"):
        hd_pol = "yin"
    elif hd_type == "Generator":
        hd_pol = "balanced"
    counts: dict[str, int] = {}
    sources = {"bazi": bazi_pol, "maya": maya_pol, "human_design": hd_pol}
    for s, p in sources.items():
        if p:
            counts[p] = counts.get(p, 0) + 1
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else None
    return {"sources": sources, "counts": counts, "dominant": dominant}


def decision_resonance(engine_json: dict[str, Any]) -> dict[str, Any]:
    hd = engine_json.get("human_design") or {}
    auth = hd.get("authority")
    western = engine_json.get("western") or {}
    moon = (western.get("placements") or {}).get("Moon") if isinstance(western, dict) else None
    moon_sign = moon.get("sign") if isinstance(moon, dict) else None
    nak = _vedic_moon_nakshatra(engine_json)
    return {
        "hd_authority": auth,
        "western_moon_sign": moon_sign,
        "vedic_nakshatra_index": nak,
    }


def timing_resonance(engine_json: dict[str, Any]) -> dict[str, Any]:
    maya = engine_json.get("maya") or {}
    wave = maya.get("wavespell") or {}
    vedic = engine_json.get("vedic") or {}
    pan = vedic.get("panchanga") or {}
    chinese = engine_json.get("chinese") or {}
    pillars = chinese.get("bazi_pillars") or {}
    return {
        "maya_wavespell": wave,
        "maya_kin": maya.get("kin"),
        "vedic_vaara": pan.get("vaara") if isinstance(pan, dict) else None,
        "vedic_tithi_idx": (pan.get("tithi") or {}).get("index") if isinstance(pan, dict) else None,
        "bazi_pillar_year": pillars.get("year") if isinstance(pillars, dict) else None,
        "bazi_pillar_day": pillars.get("day") if isinstance(pillars, dict) else None,
    }


# -----------------------------------------------------------------------------
# Narrative generators (ASCII-safe NL via \u escapes for accented characters)
# -----------------------------------------------------------------------------


_ELEMENT_NL = {
    "fire": "vuur", "earth": "aarde", "air": "lucht", "water": "water",
    "wood": "hout", "metal": "metaal",
}
_ELEMENT_EN = {
    "fire": "fire", "earth": "earth", "air": "air", "water": "water",
    "wood": "wood", "metal": "metal",
}


def _element_label(elem: Optional[str], lang: str) -> str:
    if not elem:
        return "-"
    return (_ELEMENT_NL if lang == "nl" else _ELEMENT_EN).get(elem, elem)


def _element_narrative(res: dict[str, Any], lang: str) -> str:
    if not res.get("dominant"):
        return ""
    score = int(res.get("agreement_score") or 0)
    dom = res["dominant"]
    agreements = res.get("agreements") or []
    label = _element_label(dom, lang)
    if score >= 3:
        if lang == "nl":
            return (
                "Meerdere methodes (" + ", ".join(agreements) + ") wijzen tegelijk naar " + label + ". "
                "Dat is een sterk gedeelde grondtoon: jouw natuurlijke uitdrukking, "
                "ritme en herstel hebben deze kwaliteit duidelijk nodig."
            )
        return (
            "Multiple methods (" + ", ".join(agreements) + ") point at " + label + " together. "
            "This is a strongly shared keynote: your natural expression, rhythm and "
            "recovery clearly need this quality."
        )
    if score == 2:
        if lang == "nl":
            return (
                "Twee methodes benadrukken " + label + ". Daar zit een terugkerend thema, "
                "maar het is niet absoluut: andere lagen geven aanvullende kleuren."
            )
        return (
            "Two methods emphasize " + label + ". There is a recurring theme here, "
            "but it is not absolute - other layers add complementary colors."
        )
    if lang == "nl":
        return (
            "Slechts \u00e9\u00e9n methode wijst sterk naar " + label + ". Lees het als \u00e9\u00e9n "
            "invalshoek tussen meerdere; harde conclusies zijn hier niet op zijn plaats."
        )
    return (
        "Only one method points strongly at " + label + ". Read it as one angle among "
        "several; firm conclusions are not warranted here."
    )


def _decision_narrative(res: dict[str, Any], lang: str) -> str:
    auth = res.get("hd_authority")
    moon_sign = res.get("western_moon_sign")
    if not auth and not moon_sign:
        return ""
    if lang == "nl":
        if auth and moon_sign:
            return (
                "Je Human Design authoriteit is " + str(auth) + ", en je westerse Maan staat in " +
                str(moon_sign) + ". Beide systemen beschrijven hoe jij innerlijk een 'ja' herkent: "
                "vertrouw eerder op lichaamssignalen of emotionele helderheid dan op pure ratio."
            )
        if auth:
            return (
                "Je Human Design authoriteit is " + str(auth) + ". Dit is de leidraad voor "
                "besluitvorming binnen jouw type."
            )
        return (
            "Je westerse Maan staat in " + str(moon_sign) + "; dat tekent hoe je emotioneel "
            "keuzes weegt."
        )
    if auth and moon_sign:
        return (
            "Your Human Design authority is " + str(auth) + ", and your Western Moon is in " +
            str(moon_sign) + ". Both methods describe how you recognise an inner 'yes' - "
            "trust body signals or emotional clarity over pure rationality."
        )
    if auth:
        return "Your Human Design authority is " + str(auth) + ". This is the decision compass for your type."
    return "Your Western Moon is in " + str(moon_sign) + "; this shapes how you weigh choices emotionally."


def _timing_narrative(res: dict[str, Any], lang: str) -> str:
    parts: list[str] = []
    wave = res.get("maya_wavespell") or {}
    if wave.get("wavespell_index"):
        if lang == "nl":
            parts.append(
                "Maya wavespell " + str(wave.get("wavespell_index")) +
                " (positie " + str(wave.get("wavespell_position")) + ")"
            )
        else:
            parts.append(
                "Maya wavespell " + str(wave.get("wavespell_index")) +
                " (position " + str(wave.get("wavespell_position")) + ")"
            )
    vaara = res.get("vedic_vaara")
    if vaara:
        parts.append(
            ("Vedische Vaara: " if lang == "nl" else "Vedic Vaara: ") + str(vaara)
        )
    bazi_day = res.get("bazi_pillar_day") or {}
    if bazi_day.get("stem") and bazi_day.get("branch"):
        bazi_label = str(bazi_day.get("stem")) + str(bazi_day.get("branch"))
        parts.append(
            ("BaZi-dagpillaar: " if lang == "nl" else "BaZi day pillar: ") + bazi_label
        )
    if not parts:
        return ""
    if lang == "nl":
        return (
            "Tijdslaag van het profiel: " + " - ".join(parts) +
            ". Combineer ze als opeenvolgende bewegingsritmes, niet als concurrerende stempels."
        )
    return (
        "Profile timing layer: " + " - ".join(parts) +
        ". Read them as successive movement rhythms rather than competing stamps."
    )


def _polarity_narrative(res: dict[str, Any], lang: str) -> str:
    counts = res.get("counts") or {}
    if not counts:
        return ""
    dom = res.get("dominant")
    if dom == "balanced":
        return (
            "Polariteit voelt evenwichtig over methodes heen; je beweegt natuurlijk tussen "
            "actief en ontvankelijk."
            if lang == "nl"
            else "Polarity feels balanced across methods; you move naturally between active and receptive."
        )
    if dom == "yang":
        return (
            "Polariteit neigt naar Yang: actief, vooruitstrevend en richting-gevend. "
            "Pas op voor uitputting; bouw bewust ontvangende rust in."
            if lang == "nl"
            else "Polarity leans Yang: active, forward, direction-giving. Watch for burnout; "
                 "build receptive rest in deliberately."
        )
    if dom == "yin":
        return (
            "Polariteit neigt naar Yin: ontvangend, reflectief en stromend. Activatie komt "
            "via bewuste impuls of uitnodiging, niet via forceren."
            if lang == "nl"
            else "Polarity leans Yin: receptive, reflective, flowing. Activation comes through "
                 "conscious impulse or invitation - not by force."
        )
    return ""


# -----------------------------------------------------------------------------
# Main builder
# -----------------------------------------------------------------------------


def build_cross_system(engine_json: dict[str, Any], *, locale: str = "nl-NL") -> dict[str, Any]:
    """Top-level cross-system intelligence block."""
    lang = _norm_locale(locale)
    elem = element_resonance(engine_json)
    pol = polarity_resonance(engine_json)
    decision = decision_resonance(engine_json)
    timing = timing_resonance(engine_json)

    sections: list[dict[str, Any]] = []
    sections.append({
        "key": "element_resonance",
        "title": "Elementresonantie" if lang == "nl" else "Element resonance",
        "data": elem,
        "text": _element_narrative(elem, lang),
    })
    sections.append({
        "key": "polarity_resonance",
        "title": "Polariteit" if lang == "nl" else "Polarity",
        "data": pol,
        "text": _polarity_narrative(pol, lang),
    })
    sections.append({
        "key": "decision_resonance",
        "title": "Besluitvorming" if lang == "nl" else "Decision making",
        "data": decision,
        "text": _decision_narrative(decision, lang),
    })
    sections.append({
        "key": "timing_resonance",
        "title": "Tijdscycli" if lang == "nl" else "Time cycles",
        "data": timing,
        "text": _timing_narrative(timing, lang),
    })

    if lang == "nl":
        summary = (
            "Dit is geen losse horoscoop, maar een ge\u00efntegreerd energieprofiel. "
            "De systemen versterken elkaar wanneer ze convergeren, en bieden nuance "
            "wanneer ze verschillen. Behandel elke uitspraak als een perspectief - "
            "niet als absolute waarheid."
        )
    else:
        summary = (
            "This is not a loose horoscope but an integrated energy profile. "
            "The systems reinforce each other when they converge and add nuance "
            "when they differ. Treat every statement as a perspective, not as "
            "an absolute truth."
        )

    return {
        "summary": summary,
        "sections": sections,
        "convergence": {
            "element": elem.get("dominant"),
            "polarity": pol.get("dominant"),
            "agreement_score_element": elem.get("agreement_score", 0),
        },
    }
