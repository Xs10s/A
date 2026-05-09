"""
Energy profile layer: derive human-readable, multi-system "energy profile"
from the existing deterministic engine output.

Design goals (inspired by Body-Energy-Profile):
- deterministic chartSignature
- domain scores with evidence signals
- system-agnostic structure so multiple methods can be compared
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Literal, Optional, TypedDict

from .knowledgebase import (
    aspect_meaning,
    karana_meaning,
    house_meaning,
    nakshatra_meaning,
    normalize_locale as kb_normalize_locale,
    pillar_meaning,
    planet_meaning,
    sign_meaning,
    tithi_meaning,
    vaara_meaning,
    yoga_meaning,
)


SystemId = Literal[
    "western_tropical",
    "western_sidereal",
    "vedic_panchanga",
    "chinese_bazi",
    "human_design",
    "maya",
]


class Signal(TypedDict, total=False):
    key: str
    label: str
    category: str  # e.g. "western", "vedic", "chinese"
    tags: list[str]
    weight: float  # signed contribution
    meta: dict[str, Any]


class DomainScore(TypedDict, total=False):
    key: str
    label: str
    score: float
    scoreMin: float
    scoreMax: float
    spread: float
    evidence: dict[str, Any]


class EnergyProfile(TypedDict, total=False):
    chartSignature: str
    system: dict[str, Any]
    domains: list[DomainScore]
    signals: list[Signal]
    explain: dict[str, Any]
    narrative: dict[str, Any]


class CombinedEnergyProfile(TypedDict, total=False):
    chartSignature: str
    profiles: list[EnergyProfile]
    parityNotes: list[str]
    systems: list[str]


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def chart_signature(engine_json: dict[str, Any], *, system: SystemId) -> str:
    """
    Stable signature for caching/identity.
    Includes birth input + key settings + selected system.
    """
    birth = (engine_json.get("input") or {}).get("birth") or {}
    place = birth.get("place") or {}
    tz = birth.get("timezone") or {}
    stable = {
        "system": system,
        "birth": {
            "date": birth.get("date"),
            "time_local": birth.get("time_local"),
            "lat": place.get("lat"),
            "lon": place.get("lon"),
            "elevation_m": place.get("elevation_m"),
            "timezone_iana": tz.get("iana"),
            "utc_offset_minutes": tz.get("utc_offset_minutes"),
            "utc_offset_hours": tz.get("utc_offset_hours"),
        },
        # include a subset of computation settings when present
        "settings": {
            "house_system": ((engine_json.get("western") or {}).get("houses") or {}).get("system"),
            "ayanamsha_mode": ((engine_json.get("vedic") or {}).get("ayanamsha") or {}).get("mode"),
            "vedic_at": (engine_json.get("vedic") or {}).get("at_mode"),
            "chinese_year_boundary": ((engine_json.get("chinese") or {}).get("boundary_settings") or {}).get("year"),
            "chinese_day_boundary": ((engine_json.get("chinese") or {}).get("boundary_settings") or {}).get("day"),
        },
    }
    raw = _canonical_json(stable).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def _element_of_sign(sign_code: str) -> Optional[str]:
    # Western sign -> element
    fire = {"Aries", "Leo", "Sagittarius"}
    earth = {"Taurus", "Virgo", "Capricorn"}
    air = {"Gemini", "Libra", "Aquarius"}
    water = {"Cancer", "Scorpio", "Pisces"}
    if sign_code in fire:
        return "fire"
    if sign_code in earth:
        return "earth"
    if sign_code in air:
        return "air"
    if sign_code in water:
        return "water"
    return None


def _domain_defs() -> list[tuple[str, str, str]]:
    """
    Canonical domains shared across systems.
    label_nl is used for UI/narrative text.
    """
    return [
        ("body_energy", "Body energy", "Lichaamsenergie"),
        ("emotion", "Emotional resilience", "Emotionele veerkracht"),
        ("mind", "Mental focus", "Mentale focus"),
        ("relationships", "Relationships", "Relaties & verbinding"),
        ("purpose", "Purpose & work", "Doel & werk"),
        ("growth", "Personal growth", "Persoonlijke groei"),
        ("stability", "Grounding & stability", "Gronding & stabiliteit"),
        ("spirit", "Spiritual tone", "Spirituele toon"),
    ]


def _score_from_sign_element(element: Optional[str]) -> dict[str, float]:
    # Simple heuristic mapping for demo-level energy scoring.
    # Returned dict: per-domain base contributions.
    if element == "fire":
        return {"vitality": 8, "drive": 6, "growth": 3}
    if element == "earth":
        return {"discipline": 7, "vitality": 3, "harmony": 2}
    if element == "air":
        return {"mind": 8, "growth": 3, "harmony": 2}
    if element == "water":
        return {"emotion": 8, "harmony": 4, "vitality": 2}
    return {}


def _domain_meaning(domain: str, level: str, *, locale: Optional[str]) -> str:
    """Short human text for what a score level means per domain."""
    lang = kb_normalize_locale(locale)
    high = level == "high"
    low = level == "low"

    if domain == "body_energy":
        if lang == "nl":
            if high:
                return "Je fysieke energie laadt snel op; beweging en activiteit geven je vaak energie."
            if low:
                return "Je lichaam heeft baat bij bewuste pacing en herstel; energie kan dalen bij te veel beloven."
            return "Je fysieke energie is gemiddeld; je blijft in balans door activiteit én rust te plannen."
        if high:
            return "Your physical energy tends to recharge quickly; movement and activity often give you energy."
        if low:
            return "Your body may need more conscious pacing and recovery; energy can dip if you over-commit."
        return "Your physical energy is moderate; planning both activity and rest keeps you in balance."

    if domain == "emotion":
        if lang == "nl":
            if high:
                return "Emotioneel veer je snel terug; je kunt gevoelens dragen zonder erin te verdrinken."
            if low:
                return "Emoties kunnen intens of uitputtend voelen; veilige uitlaatkleppen en ritme zijn dan extra belangrijk."
            return "Je emotionele klimaat is gemengd; sommige situaties voeden je, andere vragen om heldere grenzen."
        if high:
            return "You bounce back emotionally and can hold space for feelings without drowning in them."
        if low:
            return "Emotions can feel intense or draining; creating safe outlets and rhythms really matters."
        return "Your emotional climate is mixed; some situations uplift you, others ask for careful boundaries."

    if domain == "mind":
        if lang == "nl":
            if high:
                return "Je geest focust sterk; ideeën, leren en analyse zijn natuurlijke krachtbronnen."
            if low:
                return "Je mentale focus kan versnipperen of snel vermoeid raken; zachte structuur en pauzes helpen."
            return "Je denken is flexibel: je kunt focussen wanneer nodig, maar je kunt ook afdwalen als het niet boeit."
        if high:
            return "Your mind focuses strongly; ideas, learning and analysis are natural strengths."
        if low:
            return "Mental focus can scatter or tire easily; gentle structure and breaks help a lot."
        return "Your thinking is flexible; you can focus when needed but also drift if the topic doesn't engage you."

    if domain == "relationships":
        if lang == "nl":
            if high:
                return "Relaties zijn een kernkanaal voor jouw levenenergie en groei."
            if low:
                return "Relationele situaties kunnen energie kosten; duidelijke signalen en gezonde afstand helpen."
            return "Contact kan zowel geven als nemen; de juiste mensen kiezen is sleutel."
        if high:
            return "Relationships are a main channel for your life energy and growth."
        if low:
            return "Relational situations may cost energy; you benefit from clear signals and healthy distance."
        return "Connections can both give and take energy; choosing the right people is key."

    if domain == "purpose":
        if lang == "nl":
            if high:
                return "Een gevoel van missie of richting voedt je motivatie en keuzes sterk."
            if low:
                return "Doel kan soms onduidelijk voelen; je verkent mogelijk verschillende rollen tot iets 'klikt'."
            return "Je hebt wel richting, maar er is ruimte om te verfijnen wat echt betekenis voor je heeft."
        if high:
            return "A sense of mission or direction strongly fuels your motivation and choices."
        if low:
            return "Purpose can feel unclear at times; you may explore different roles before something clicks."
        return "You have some direction, but there's room to refine what feels truly meaningful."

    if domain == "growth":
        if lang == "nl":
            if high:
                return "Je groeit via uitdaging; je voelt je vaak aangetrokken tot jezelf ontwikkelen."
            if low:
                return "Verandering kan vermoeiend voelen; kleine, langzame verbeteringen werken beter dan grote sprongen."
            return "Je leert in golven: soms ga je vooruit, soms consolideer je."
        if high:
            return "You grow through challenge and are often drawn to develop yourself."
        if low:
            return "Change can feel tiring; slow, small improvements work better than big leaps."
        return "You learn in waves; sometimes you push forward, sometimes you consolidate."

    if domain == "stability":
        if lang == "nl":
            if high:
                return "Je creëert stabiele structuren en kunt een aardende aanwezigheid zijn."
            if low:
                return "Het leven kan veranderlijk voelen; routines en ankers waarop je kunt leunen helpen."
            return "Je balanceert zekerheid met flexibiliteit; soms stevig, soms experimenteel."
        if high:
            return "You create stable structures around you and can be a grounding presence."
        if low:
            return "Life may feel changeable; you benefit from routines and anchors you can rely on."
        return "You balance security with flexibility; sometimes steady, sometimes experimental."

    if domain == "spirit":
        if lang == "nl":
            if high:
                return "Spiritualiteit of innerlijke betekenis is een sterke stroom in je leven."
            if low:
                return "Je kunt spirituele thema's betwijfelen, negeren of heel privé houden."
            return "Je relateert aan betekenis en spiritualiteit op een persoonlijke, situatie-gebonden manier."
        if high:
            return "Spiritual or inner meaning is a strong current in your life."
        if low:
            return "You may question or ignore spiritual themes, or keep them very private."
        return "You relate to meaning and spirituality in a personal, situational way."

    return ""


def _init_domain_acc() -> dict[str, float]:
    return {k: 0.0 for k, _, _ in _domain_defs()}


def _apply_signal(acc: dict[str, float], signal: Signal, contributions: dict[str, float]) -> None:
    w = float(signal.get("weight", 0.0))
    for dk, dv in contributions.items():
        if dk in acc:
            acc[dk] += w * float(dv)


def _western_signals(engine_json: dict[str, Any]) -> list[Signal]:
    western = engine_json.get("western") or {}
    placements = western.get("placements") or {}
    aspects = western.get("aspects") or []
    out: list[Signal] = []

    sun = placements.get("Sun") or {}
    moon = placements.get("Moon") or {}
    asc = placements.get("Asc") or {}
    if isinstance(sun, dict) and sun.get("sign"):
        out.append(
            {
                "key": "sun_sign",
                "label": f"Sun in {sun.get('sign')}",
                "category": "western",
                "tags": ["sun", "sign"],
                "weight": 1.0,
                "meta": {"planet": "Sun", "sign": sun.get("sign"), "house": sun.get("house")},
            }
        )
    if isinstance(moon, dict) and moon.get("sign"):
        out.append(
            {
                "key": "moon_sign",
                "label": f"Moon in {moon.get('sign')}",
                "category": "western",
                "tags": ["moon", "sign"],
                "weight": 1.0,
                "meta": {"planet": "Moon", "sign": moon.get("sign"), "house": moon.get("house")},
            }
        )
    if isinstance(asc, dict) and asc.get("sign"):
        out.append(
            {
                "key": "asc_sign",
                "label": f"Ascendant in {asc.get('sign')}",
                "category": "western",
                "tags": ["asc", "sign"],
                "weight": 0.8,
                "meta": {"planet": "Asc", "sign": asc.get("sign"), "house": asc.get("house")},
            }
        )
    # Add 1-2 tight aspects as signals (orb <= 2°) for punchy evidence.
    tight = []
    for a in aspects:
        if not isinstance(a, dict):
            continue
        orb = a.get("orb_deg") if a.get("orb_deg") is not None else a.get("orb_degrees")
        try:
            orb_f = float(orb)
        except Exception:
            continue
        if orb_f <= 2.0 and a.get("a") and a.get("b") and a.get("type"):
            tight.append((orb_f, a))
    tight.sort(key=lambda x: x[0])
    for orb_f, a in tight[:2]:
        out.append(
            {
                "key": "tight_aspect",
                "label": f"{a.get('a')} {a.get('type')} {a.get('b')} (orb {orb_f:.2f}°)",
                "category": "western",
                "tags": ["aspect", str(a.get("type") or "")],
                "weight": 0.6,
                "meta": {
                    "a": a.get("a"),
                    "b": a.get("b"),
                    "type": a.get("type"),
                    "orb_deg": orb_f,
                    "applying": a.get("applying", False),
                },
            }
        )
    return out


def _vedic_signals(engine_json: dict[str, Any]) -> list[Signal]:
    vedic = engine_json.get("vedic") or {}
    pan = vedic.get("panchanga") or {}
    out: list[Signal] = []
    if not isinstance(pan, dict) or not pan:
        return out
    if pan.get("vaara"):
        out.append(
            {
                "key": "vaara",
                "label": f"Vaara: {pan.get('vaara')}",
                "category": "vedic",
                "tags": ["vaara"],
                "weight": 0.35,
                "meta": {"vaara": pan.get("vaara")},
            }
        )
    for k, tag in [("tithi", "tithi"), ("nakshatra", "nakshatra"), ("yoga", "yoga")]:
        block = pan.get(k)
        if isinstance(block, dict) and block.get("index") is not None:
            out.append(
                {
                    "key": k,
                    "label": f"{k.title()}: {block.get('index')}",
                    "category": "vedic",
                    "tags": [tag],
                    "weight": 0.25,
                    "meta": {"index": block.get("index"), "ends_at_local": block.get("ends_at_local")},
                }
            )

    kar = pan.get("karana") or {}
    if isinstance(kar, dict):
        indices = kar.get("indices") or []
        if isinstance(indices, list) and indices:
            out.append(
                {
                    "key": "karana",
                    "label": "Karana: " + ", ".join(str(x) for x in indices[:2]),
                    "category": "vedic",
                    "tags": ["karana"],
                    "weight": 0.2,
                    "meta": {"indices": indices},
                }
            )
    return out


def _chinese_signals(engine_json: dict[str, Any]) -> list[Signal]:
    chinese = engine_json.get("chinese") or {}
    bazi = chinese.get("bazi_pillars") or {}
    out: list[Signal] = []
    if not isinstance(bazi, dict) or not bazi:
        return out

    year = bazi.get("year") or {}
    if isinstance(year, dict) and year.get("stem") and year.get("branch"):
        out.append(
            {
                "key": "bazi_year",
                "label": f"Year pillar: {year.get('stem')}{year.get('branch')}",
                "category": "chinese",
                "tags": ["bazi", "year_pillar"],
                "weight": 0.5,
                "meta": {
                    "stem": year.get("stem"),
                    "branch": year.get("branch"),
                    "index_60": year.get("index_60"),
                },
            }
        )
    # Day pillar is the "core" pillar in many BaZi readings.
    day = bazi.get("day") or {}
    if isinstance(day, dict) and day.get("stem") and day.get("branch"):
        out.append(
            {
                "key": "bazi_day",
                "label": f"Day pillar: {day.get('stem')}{day.get('branch')}",
                "category": "chinese",
                "tags": ["bazi", "day_pillar"],
                "weight": 0.7,
                "meta": {"stem": day.get("stem"), "branch": day.get("branch"), "index_60": day.get("index_60")},
            }
        )
    month = bazi.get("month") or {}
    if isinstance(month, dict) and month.get("stem") and month.get("branch"):
        out.append(
            {
                "key": "bazi_month",
                "label": f"Month pillar: {month.get('stem')}{month.get('branch')}",
                "category": "chinese",
                "tags": ["bazi", "month_pillar"],
                "weight": 0.45,
                "meta": {"stem": month.get("stem"), "branch": month.get("branch")},
            }
        )
    hour = bazi.get("hour") or {}
    if isinstance(hour, dict) and hour.get("stem") and hour.get("branch"):
        out.append(
            {
                "key": "bazi_hour",
                "label": f"Hour pillar: {hour.get('stem')}{hour.get('branch')}",
                "category": "chinese",
                "tags": ["bazi", "hour_pillar"],
                "weight": 0.4,
                "meta": {"stem": hour.get("stem"), "branch": hour.get("branch")},
            }
        )
    return out


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def _normalize_domains(raw: dict[str, float], *, locale: Optional[str]) -> list[DomainScore]:
    # Map accumulated contributions to a friendly 0..100 score.
    # We keep it deterministic and intentionally simple.
    out: list[DomainScore] = []
    lang = kb_normalize_locale(locale)
    for dk, label_en, label_nl in _domain_defs():
        # typical raw range is small; scale + center
        score = 50.0 + raw.get(dk, 0.0)
        score = _clamp(score, 0.0, 100.0)
        # Simple tiered meaning per domain.
        if score >= 70:
            level = "high"
        elif score <= 40:
            level = "low"
        else:
            level = "medium"
        meaning = _domain_meaning(dk, level, locale=locale)
        out.append(
            {
                "key": dk,
                "label": label_nl if lang == "nl" else label_en,
                "score": round(score, 1),
                "scoreMin": 0.0,
                "scoreMax": 100.0,
                "spread": 100.0,
                "evidence": {"signals": [], "level": level, "meaning": meaning},
            }
        )
    return out


def _human_design_signals(engine_json: dict[str, Any]) -> list[Signal]:
    hd = engine_json.get("human_design") or {}
    out: list[Signal] = []
    if not isinstance(hd, dict) or not hd.get("type"):
        return out
    out.append({
        "key": "hd_type",
        "label": f"Type: {hd.get('type')}",
        "category": "human_design",
        "tags": ["type"],
        "weight": 0.8,
        "meta": {"type": hd.get("type"), "authority": hd.get("authority")},
    })
    profile = hd.get("profile") or {}
    if profile.get("value"):
        out.append({
            "key": "hd_profile",
            "label": f"Profiel: {profile.get('value')}",
            "category": "human_design",
            "tags": ["profile"],
            "weight": 0.6,
            "meta": {
                "value": profile.get("value"),
                "personality_line": profile.get("personality_line"),
                "design_line": profile.get("design_line"),
            },
        })
    auth = hd.get("authority")
    if auth:
        out.append({
            "key": "hd_authority",
            "label": f"Authority: {auth}",
            "category": "human_design",
            "tags": ["authority"],
            "weight": 0.7,
            "meta": {"authority": auth},
        })
    centers = hd.get("centers") or {}
    defined = centers.get("defined") or []
    if defined:
        out.append({
            "key": "hd_defined_centers",
            "label": f"Defined centers: {', '.join(defined)}",
            "category": "human_design",
            "tags": ["centers"],
            "weight": 0.45,
            "meta": {"defined": defined, "undefined": centers.get("undefined") or []},
        })
    channels = hd.get("channels") or []
    for ch in channels[:6]:
        out.append({
            "key": "hd_channel",
            "label": f"Kanaal {ch.get('name')}",
            "category": "human_design",
            "tags": ["channel", str(ch.get("circuit") or "")],
            "weight": 0.4,
            "meta": ch,
        })
    return out


def _maya_signals(engine_json: dict[str, Any]) -> list[Signal]:
    maya_block = engine_json.get("maya") or {}
    out: list[Signal] = []
    if not isinstance(maya_block, dict) or not maya_block.get("kin"):
        return out
    sign = maya_block.get("sign") or {}
    tone = maya_block.get("tone") or {}
    out.append({
        "key": "maya_kin",
        "label": f"Kin {maya_block.get('kin')} - {sign.get('yucatec', '')}",
        "category": "maya",
        "tags": ["kin", "tzolkin"],
        "weight": 0.8,
        "meta": {
            "kin": maya_block.get("kin"),
            "tone_index": tone.get("index"),
            "sign_index": sign.get("index"),
            "element": sign.get("element"),
            "polarity": sign.get("polarity"),
            "direction": sign.get("direction"),
        },
    })
    wave = maya_block.get("wavespell") or {}
    if wave.get("wavespell_index"):
        out.append({
            "key": "maya_wavespell",
            "label": f"Wavespell {wave.get('wavespell_index')}",
            "category": "maya",
            "tags": ["wavespell"],
            "weight": 0.45,
            "meta": wave,
        })
    haab = maya_block.get("haab") or {}
    if haab.get("month_name"):
        out.append({
            "key": "maya_haab",
            "label": f"Haab: {haab.get('label')}",
            "category": "maya",
            "tags": ["haab"],
            "weight": 0.35,
            "meta": haab,
        })
    return out


def build_energy_profile(
    engine_json: dict[str, Any],
    *,
    system: SystemId,
    locale: str = "nl-NL",
) -> EnergyProfile:
    sig = chart_signature(engine_json, system=system)
    lang = kb_normalize_locale(locale)

    signals: list[Signal] = []
    if system in ("western_tropical", "western_sidereal"):
        signals.extend(_western_signals(engine_json))
    if system == "vedic_panchanga":
        signals.extend(_vedic_signals(engine_json))
    if system == "chinese_bazi":
        signals.extend(_chinese_signals(engine_json))
    if system == "human_design":
        signals.extend(_human_design_signals(engine_json))
    if system == "maya":
        signals.extend(_maya_signals(engine_json))

    acc = _init_domain_acc()

    # Core mapping: Sun, Moon, Ascendant sign elements drive base domains.
    western = engine_json.get("western") or {}
    placements = western.get("placements") or {}
    sun_sign = (placements.get("Sun") or {}).get("sign") if isinstance(placements, dict) else None
    moon_sign = (placements.get("Moon") or {}).get("sign") if isinstance(placements, dict) else None
    asc_sign = (placements.get("Asc") or {}).get("sign") if isinstance(placements, dict) else None

    if isinstance(sun_sign, str):
        contrib = _score_from_sign_element(_element_of_sign(sun_sign))
        # Sun: life force & purpose.
        for k in contrib:
            contrib[k] *= 1.4
        _apply_signal(acc, {"weight": 1.0}, contrib)
        acc["purpose"] += 4.0
    if isinstance(moon_sign, str):
        contrib = _score_from_sign_element(_element_of_sign(moon_sign))
        # Moon: emotional tone.
        for k in contrib:
            contrib[k] *= 1.1
        _apply_signal(acc, {"weight": 1.0}, contrib)
        acc["emotion"] += 3.0
    if isinstance(asc_sign, str):
        contrib = _score_from_sign_element(_element_of_sign(asc_sign))
        # Ascendant: how energy is expressed in the body and towards others.
        for k in contrib:
            contrib[k] *= 0.9
        _apply_signal(acc, {"weight": 0.8}, contrib)
        acc["body_energy"] += 3.0
        acc["relationships"] += 2.0

    # Human Design contribution: type/authority/centers shape body energy,
    # decision-making (mind/spirit/emotion) and relationships.
    if system == "human_design":
        hd = engine_json.get("human_design") or {}
        hd_type = hd.get("type")
        if hd_type in ("Generator", "Manifesting Generator"):
            acc["body_energy"] += 14.0
            acc["purpose"] += 10.0
        elif hd_type == "Manifestor":
            acc["body_energy"] += 8.0
            acc["purpose"] += 12.0
            acc["relationships"] -= 1.0
        elif hd_type == "Projector":
            acc["mind"] += 10.0
            acc["relationships"] += 6.0
            acc["body_energy"] -= 4.0
        elif hd_type == "Reflector":
            acc["spirit"] += 10.0
            acc["relationships"] += 6.0
            acc["body_energy"] -= 6.0

        auth = hd.get("authority")
        if auth == "Emotional":
            acc["emotion"] += 10.0
            acc["mind"] -= 2.0
        elif auth == "Sacral":
            acc["body_energy"] += 8.0
        elif auth == "Splenic":
            acc["spirit"] += 6.0
            acc["mind"] += 2.0
        elif auth == "Ego":
            acc["purpose"] += 6.0
            acc["stability"] += 4.0
        elif auth == "Self-projected":
            acc["growth"] += 6.0
            acc["spirit"] += 4.0
        elif auth == "Mental":
            acc["mind"] += 6.0
        elif auth == "Lunar":
            acc["spirit"] += 8.0

        centers = hd.get("centers") or {}
        defined = set(centers.get("defined") or [])
        # Each defined center adds stability (consistency) to its theme.
        for center, dom_keys in (
            ("Sacral", ["body_energy"]),
            ("Heart", ["purpose", "stability"]),
            ("SolarPlexus", ["emotion"]),
            ("Spleen", ["spirit", "body_energy"]),
            ("Throat", ["relationships"]),
            ("G", ["growth"]),
            ("Ajna", ["mind"]),
            ("Head", ["mind"]),
            ("Root", ["body_energy"]),
        ):
            if center in defined:
                for k in dom_keys:
                    acc[k] += 4.0

    # Maya contribution: signs map to elements (already in signs metadata).
    if system == "maya":
        maya_block = engine_json.get("maya") or {}
        sign = maya_block.get("sign") or {}
        elem = sign.get("element")
        polarity = sign.get("polarity")
        contrib = _score_from_sign_element(elem)
        for k in contrib:
            acc[k] = acc.get(k, 0.0) + 1.4 * contrib[k]
        if polarity == "yang":
            acc["body_energy"] += 4.0
            acc["purpose"] += 3.0
        elif polarity == "yin":
            acc["emotion"] += 4.0
            acc["spirit"] += 3.0
        # Tone shapes the rhythm of energy: low tones (1-4) initiate, mid (5-9) build,
        # high (10-13) integrate / release.
        tone_idx = (maya_block.get("tone") or {}).get("index")
        if isinstance(tone_idx, int):
            if tone_idx <= 4:
                acc["growth"] += 4.0
            elif tone_idx <= 9:
                acc["stability"] += 4.0
            else:
                acc["spirit"] += 4.0

    # Aspect tone: harmonics add harmony/growth; hard aspects add drive/stability with tension.
    aspects = (western.get("aspects") or []) if isinstance(western, dict) else []
    harm = 0.0
    hard = 0.0
    for a in aspects:
        if not isinstance(a, dict):
            continue
        t = a.get("type")
        orb = a.get("orb_deg") if a.get("orb_deg") is not None else a.get("orb_degrees")
        try:
            orb_f = float(orb)
        except Exception:
            continue
        if orb_f > 6.0:
            continue
        if t in ("trine", "sextile", "conjunction"):
            harm += max(0.0, 1.2 - (orb_f / 6.0))
        if t in ("square", "opposition"):
            hard += max(0.0, 1.2 - (orb_f / 6.0))
    acc["growth"] += 4.0 * harm
    acc["relationships"] += 3.0 * harm
    acc["stability"] += 2.0 * harm
    acc["body_energy"] += 3.0 * hard
    acc["purpose"] += 3.0 * hard
    acc["stability"] += 4.0 * hard
    acc["emotion"] -= 2.0 * hard

    domains = _normalize_domains(acc, locale=locale)

    # Attach some evidence per domain: top signals (by abs weight) and summary counts.
    sig_sorted = sorted(signals, key=lambda s: abs(float(s.get("weight", 0.0))), reverse=True)
    top = sig_sorted[:6]
    domain_index = {d["key"]: d for d in domains if "key" in d}
    for d in domains:
        d.setdefault("evidence", {})
        d["evidence"]["signals"] = top
        d["evidence"]["notes"] = []

    # Build narrative details that explicitly connect placements to domains.
    details = _build_narrative_details(signals, domains, locale=locale)

    parity_notes: list[str] = []
    if system == "western_sidereal":
        if lang == "nl":
            parity_notes.append("Sidereale interpretaties gebruiken een sterren-geankerde dierenriem; tekens kunnen verschuiven t.o.v. tropisch, terwijl het om dezelfde hemelposities gaat.")
        else:
            parity_notes.append("Sidereal readings use a star-anchored zodiac; sign labels may differ from tropical while describing the same sky positions.")

    narrative = _narrative_from_domains(domains, system=system, locale=locale)
    narrative["details"] = details

    return {
        "chartSignature": sig,
        "system": {"id": system},
        "domains": domains,
        "signals": signals,
        "explain": {"parityNotes": parity_notes, "scoringVersion": "0.1.0"},
        "narrative": narrative,
    }


def build_combined_energy_profile(
    engine_json: dict[str, Any],
    *,
    locale: str = "nl-NL",
    include_human_design: bool = True,
    include_maya: bool = True,
) -> CombinedEnergyProfile:
    """
    Build a combined profile for the main systems so they can be compared side-by-side.

    By default Human Design and Maya are included; consumers that only need
    the original three systems can pass include_*=False.
    """
    systems: list[SystemId] = ["western_tropical", "vedic_panchanga", "chinese_bazi"]
    if include_human_design:
        systems.append("human_design")
    if include_maya:
        systems.append("maya")
    profiles: list[EnergyProfile] = [build_energy_profile(engine_json, system=s, locale=locale) for s in systems]
    # Use western_tropical signature as canonical combined signature.
    sig = profiles[0]["chartSignature"] if profiles else ""

    parity: list[str] = []
    lang = kb_normalize_locale(locale)
    if len(profiles) >= 2:
        # Simple deterministic note about agreement between highest domains.
        top_keys = []
        for p in profiles:
            doms = sorted(p.get("domains", []), key=lambda d: float(d.get("score", 0.0)), reverse=True)
            top_keys.append(doms[0].get("key") if doms else None)
        if len({k for k in top_keys if k is not None}) == 1 and top_keys[0] is not None:
            parity.append(
                (
                    f"Alle systemen benadrukken hetzelfde hoofdthema ({top_keys[0]}), wat wijst op een stevige, gedeelde focus over methodes heen."
                    if lang == "nl"
                    else f"All systems highlight the same main theme ({top_keys[0]}), suggesting a robust life focus across methods."
                )
            )
        else:
            parity.append(
                (
                    "Verschillende systemen benadrukken verschillende hoofdthema's; lees ze als aanvullende invalshoeken, niet als tegenstrijdigheden."
                    if lang == "nl"
                    else "Different systems highlight different main themes; read them as complementary angles rather than contradictions."
                )
            )

    return {
        "chartSignature": sig,
        "profiles": profiles,
        "parityNotes": parity,
        "systems": [p["system"]["id"] for p in profiles],
    }


def _narrative_from_domains(
    domains: list[DomainScore], *, system: SystemId, locale: Optional[str]
) -> dict[str, Any]:
    # Deterministic narrative: convert highest/lowest domains into a concise story.
    if not domains:
        return {"summary": "", "highlights": []}
    sorted_domains = sorted(domains, key=lambda d: float(d.get("score", 0.0)), reverse=True)
    top2 = sorted_domains[:2]
    low1 = sorted_domains[-1:]

    lang = kb_normalize_locale(locale)
    system_label = {
        "western_tropical": "Westers (tropisch)" if lang == "nl" else "Western (tropical)",
        "western_sidereal": "Westers (sidereaal)" if lang == "nl" else "Western (sidereal)",
        "vedic_panchanga": "Vedisch (Panchanga)" if lang == "nl" else "Vedic (Panchanga)",
        "chinese_bazi": "Chinees (BaZi)" if lang == "nl" else "Chinese (BaZi)",
        "human_design": "Human Design" if lang == "nl" else "Human Design",
        "maya": "Maya (Tzolkin/Haab)" if lang == "nl" else "Maya (Tzolkin/Haab)",
    }.get(system, system)
    highs = ", ".join(f"{d.get('label')} {d.get('score')}" for d in top2)
    lows = ", ".join(f"{d.get('label')} {d.get('score')}" for d in low1)

    if lang == "nl":
        summary = (
            f"{system_label} energiesnapshot: jouw sterkste thema's zijn {highs}. "
            f"Je ontwikkelkans ligt bij {lows}. "
            "Gebruik de signalen als concrete ankers tussen tradities, niet als 'bepaling' of vast lot."
        )
    else:
        summary = (
            f"{system_label} energy snapshot: strongest themes are {highs}. "
            f"Your developmental edge is {lows}. "
            "Use the signals as concrete anchors across systems, rather than treating any single score as fate."
        )
    details = _narrative_details_from_signals_and_domains(domains)
    return {
        "summary": summary,
        "highlights": [{"domain": d.get("key"), "label": d.get("label"), "score": d.get("score")} for d in top2],
        "cautions": [{"domain": d.get("key"), "label": d.get("label"), "score": d.get("score")} for d in low1],
        "details": details,
    }


def _narrative_details_from_signals_and_domains(domains: list[DomainScore]) -> list[dict[str, Any]]:
    # This function is kept for backward compatibility; details are injected in build_energy_profile.
    return []


def _build_narrative_details(
    signals: list[Signal],
    domains: list[DomainScore],
    *,
    locale: Optional[str],
) -> list[dict[str, Any]]:
    domain_labels = {d["key"]: d.get("label", d["key"]) for d in domains if "key" in d}
    out: list[dict[str, Any]] = []
    lang = kb_normalize_locale(locale)

    def add(dom_key: str, text: str, source: str) -> None:
        if dom_key not in domain_labels or not text:
            return
        out.append(
            {
                "domain": dom_key,
                "domain_label": domain_labels[dom_key],
                "text": text,
                "source": source,
            }
        )

    for s in signals:
        key = s.get("key")
        meta = s.get("meta") or {}

        if key == "sun_sign":
            planet = meta.get("planet")
            sign = meta.get("sign")
            house = meta.get("house")
            src = f"{planet or 'Sun'} in {sign}" if sign else f"{planet or 'Sun'}"
            house_txt = house_meaning(locale, house)
            planet_txt = planet_meaning(locale, planet)
            sign_txt = f" in {sign}" if sign else ""
            sign_mean = sign_meaning(locale, sign)
            if lang == "nl":
                txt = f"Jouw Zon staat{sign_txt}. {sign_mean} De Zon draagt ook de kwaliteiten van {planet_txt}. {house_txt} Daardoor kleurt dit vooral jouw Body energy en Purpose."
            else:
                txt = f"Your Sun stands{sign_txt}. {sign_mean} The Sun also carries the qualities of {planet_txt}. {house_txt} That's why it strongly colors your Body energy and Purpose."
            add("body_energy", txt, src)
            add("purpose", txt, src)

        elif key == "moon_sign":
            planet = meta.get("planet")
            sign = meta.get("sign")
            house = meta.get("house")
            src = f"{planet or 'Moon'} in {sign}" if sign else f"{planet or 'Moon'}"
            house_txt = house_meaning(locale, house)
            planet_txt = planet_meaning(locale, planet)
            sign_txt = f" in {sign}" if sign else ""
            sign_mean = sign_meaning(locale, sign)
            if lang == "nl":
                txt = f"Jouw Maan staat{sign_txt}. {sign_mean} De Maan draagt ook de kwaliteiten van {planet_txt}. {house_txt} Daardoor ontstaat een specifieke emotionele beleving en een duidelijke relatie-kant: het kleurt jouw emotion en relationships."
            else:
                txt = f"Your Moon stands{sign_txt}. {sign_mean} The Moon also carries the qualities of {planet_txt}. {house_txt} That shapes your emotional tone and relational focus - primarily through emotion and relationships."
            add("emotion", txt, src)
            add("relationships", txt, src)

        elif key == "asc_sign":
            sign = meta.get("sign")
            planet = meta.get("planet") or "Asc"
            src = f"Ascendant in {sign}" if sign else "Ascendant"
            planet_txt = planet_meaning(locale, planet)
            sign_txt = f" in {sign}" if sign else ""
            sign_mean = sign_meaning(locale, sign)
            if lang == "nl":
                txt = f"Met een Ascendant{sign_txt} komt jouw 'eerste signaal' tot leven: {sign_mean} en {planet_txt}. Dit beïnvloedt hoe jouw Body energy naar buiten komt en hoe je verbinding maakt."
            else:
                txt = f"With an Ascendant{sign_txt}, your first signal comes to life: {planet_txt}. This affects how your Body energy expresses and how you connect."
            add("body_energy", txt, src)
            add("relationships", txt, src)

        elif key == "tight_aspect":
            a = meta.get("a")
            b = meta.get("b")
            t = meta.get("type")
            applying = meta.get("applying")
            orb_f = meta.get("orb_deg")
            src = f"{a} {t} {b}".strip()
            base = aspect_meaning(locale, t or "", applying=bool(applying))
            orb_txt = f" (orb {orb_f:.2f}°)" if isinstance(orb_f, (int, float)) else ""
            if lang == "nl":
                txt = f"Een opvallende aspectlijn: {src}{orb_txt}. {base}"
            else:
                txt = f"A notable aspect thread: {src}{orb_txt}. {base}"

            if t in ("trine", "sextile", "conjunction"):
                add("growth", txt, src)
                add("relationships", txt, src)
            elif t in ("square", "opposition"):
                add("stability", txt, src)
                add("emotion", txt, src)

        elif key == "vaara":
            vaara = meta.get("vaara")
            src = f"Vaara {vaara}" if vaara else "Vaara"
            base = vaara_meaning(locale, vaara)
            if lang == "nl":
                txt = f"De weekday-kwaliteit (Vaara: {vaara}) zet de achtergrondtoon van de dag neer. {base}"
            else:
                txt = f"The weekday quality (Vaara: {vaara}) sets the day's background tone. {base}"
            add("emotion", txt, src)

        elif key in ("tithi", "nakshatra", "yoga"):
            idx = meta.get("index")
            src = f"{key.title()} {idx}"
            if key == "tithi":
                base = tithi_meaning(locale, idx)
                if lang == "nl":
                    txt = f"Tithi (lunaire dag) {idx}: {base} Dit beïnvloedt vooral emotion en innerlijke betekenis."
                else:
                    txt = f"Tithi (lunar day) {idx}: {base} This especially influences emotion and inner meaning."
                add("emotion", txt, src)
                add("spirit", txt, src)
            elif key == "nakshatra":
                base = nakshatra_meaning(locale, idx)
                if lang == "nl":
                    txt = f"Nakshatra {idx}: {base} Zo zie je je emotionele 'veld' en je intuïtieve manier van lezen."
                else:
                    txt = f"Nakshatra {idx}: {base} This reveals your emotional field and intuitive reading style."
                add("emotion", txt, src)
                add("spirit", txt, src)
            else:
                base = yoga_meaning(locale, idx)
                if lang == "nl":
                    txt = f"Yoga {idx}: {base} Je ziet hoe lichaam en gevoel in elkaar grijpen."
                else:
                    txt = f"Yoga {idx}: {base} You can sense how body and feeling intertwine."
                add("body_energy", txt, src)
                add("emotion", txt, src)

        elif key == "karana":
            indices = meta.get("indices") or []
            if isinstance(indices, list) and indices:
                idx0 = indices[0]
                base = karana_meaning(locale, idx0)
                src = "Karana " + ", ".join(str(x) for x in indices[:2])
                if lang == "nl":
                    txt = f"{src}: {base} Dit is de fase waarin de dagenergie doorwerkt."
                else:
                    txt = f"{src}: {base} This is the phase where the day's energy works through."
                add("emotion", txt, src)
                add("body_energy", txt, src)

        elif key in ("bazi_day", "bazi_month", "bazi_year", "bazi_hour"):
            stem = meta.get("stem")
            branch = meta.get("branch")
            pillar_kind = "day" if key == "bazi_day" else "month" if key == "bazi_month" else "year" if key == "bazi_year" else "hour"
            src = f"{pillar_kind.title()} pillar {stem}{branch}" if stem and branch else f"{pillar_kind.title()} pillar"
            base = pillar_meaning(locale, pillar_kind=pillar_kind, stem=str(stem or ""), branch=str(branch or ""))
            if lang == "nl":
                txt = f"BaZi {pillar_kind}: {stem}{branch}. {base}"
            else:
                txt = f"BaZi {pillar_kind}: {stem}{branch}. {base}"

            if key == "bazi_day":
                add("relationships", txt, src)
                add("purpose", txt, src)
            elif key == "bazi_month":
                add("purpose", txt, src)
                add("stability", txt, src)
            elif key == "bazi_year":
                add("purpose", txt, src)
                add("stability", txt, src)
            elif key == "bazi_hour":
                add("body_energy", txt, src)
                add("emotion", txt, src)

    return out

