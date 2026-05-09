"""
ViewModel builder: engine JSON → normalized ViewModel for UI/PDF/SVG.
"""
from __future__ import annotations

from typing import Any, Optional

from .formatters import (
    format_degrees,
    format_orb,
    sign_code_to_nl,
    BODY_LABELS_NL,
    BODY_2LETTER,
    SIGN_CODES,
)
from .diagnostics import normalize_diagnostics


def _input_summary(engine_json: dict[str, Any]) -> dict[str, Any]:
    birth = (engine_json.get("input") or {}).get("birth") or {}
    place = birth.get("place") or {}
    tz = birth.get("timezone") or {}
    date_val = birth.get("date") or ""
    time_val = birth.get("time_local")
    lat = place.get("lat")
    lon = place.get("lon")
    has_tz = (
        tz.get("iana") is not None
        or tz.get("utc_offset_hours") is not None
        or tz.get("utc_offset_minutes") is not None
    )
    if tz.get("utc_offset_hours") is not None:
        off = tz["utc_offset_hours"]
        zone_label = f"UTC{'+' if off >= 0 else ''}{off:.1f}"
    elif tz.get("utc_offset_minutes") is not None:
        off = tz["utc_offset_minutes"] / 60.0
        zone_label = f"UTC{'+' if off >= 0 else ''}{off:.1f}"
    else:
        zone_label = "niet opgegeven"
    place_label = "niet opgegeven"
    if lat is not None and lon is not None:
        place_label = f"{lat:.4f}, {lon:.4f}"
    time_display = "niet opgegeven" if not time_val else time_val[:5] if len(time_val or "") >= 5 else time_val
    return {
        "birth_date": date_val or "niet opgegeven",
        "birth_time_local": time_display,
        "place_label": place_label,
        "timezone_label": zone_label,
        "completeness": {
            "has_date": bool(date_val),
            "has_time": bool(time_val),
            "has_location": lat is not None and lon is not None,
            "has_timezone": has_tz,
        },
    }


def _planet_table_tropical(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
    western = engine_json.get("western") or {}
    placements = western.get("placements") or {}
    rows = []
    for bid, body_data in bodies.items():
        if not isinstance(body_data, dict):
            continue
        quality = body_data.get("quality") or {}
        if quality.get("computed") is False or body_data.get("lon_deg") is None:
            rows.append({"body": BODY_LABELS_NL.get(bid, bid), "lon": "n.v.t.", "sign": "-", "house": "-"})
            continue
        lon = body_data.get("lon_deg")
        placement = placements.get(bid) or {}
        sign_code = placement.get("sign") or ""
        sign_nl = sign_code_to_nl(sign_code) if sign_code else "-"
        house = placement.get("house")
        house_str = str(house) if house is not None else "-"
        lon_str = format_degrees(lon)
        rows.append({
            "body": BODY_LABELS_NL.get(bid, bid),
            "lon": lon_str,
            "sign": sign_nl,
            "house": house_str,
        })
    return rows


def _planet_table_sidereal(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
    vedic = engine_json.get("vedic") or {}
    ayanamsha_block = vedic.get("ayanamsha") or {}
    aya_mode = ayanamsha_block.get("mode") or "Lahiri"
    time_block = engine_json.get("time") or {}
    jd_tt = time_block.get("jd_tt")
    if jd_tt is None:
        return []
    try:
        from .. import sidereal
        sid_mode = sidereal.AYANAMSHA_MODES.get(aya_mode, sidereal.SE_SIDM_LAHIRI)
        aya, _, err = sidereal.ayanamsha_with_nutation(jd_tt, sid_mode)
        if err:
            return []
    except Exception:
        return []
    western = engine_json.get("western") or {}
    placements = western.get("placements") or {}
    rows = []
    for bid, body_data in bodies.items():
        if not isinstance(body_data, dict):
            continue
        lon_trop = body_data.get("lon_deg")
        if lon_trop is None or (body_data.get("quality") or {}).get("computed") is False:
            rows.append({"body": BODY_LABELS_NL.get(bid, bid), "lon": "n.v.t.", "sign": "-", "house": "-"})
            continue
        lon_sid = sidereal.tropical_to_sidereal_deg(lon_trop, aya)
        sign_num = int(lon_sid / 30) % 12
        sign_nl = sign_code_to_nl(SIGN_CODES[sign_num])
        degree_in_sign = lon_sid % 30.0
        house = placements.get(bid, {}).get("house") if isinstance(placements.get(bid), dict) else None
        house_str = str(house) if house is not None else "-"
        rows.append({
            "body": BODY_LABELS_NL.get(bid, bid),
            "lon": format_degrees(lon_sid),
            "sign": sign_nl,
            "house": house_str,
        })
    return rows


def _houses_table(engine_json: dict[str, Any], use_sidereal: bool = False) -> list[dict[str, Any]]:
    western = engine_json.get("western")
    if not western:
        return []
    houses_block = western.get("houses") or {}
    cusps = houses_block.get("cusps_deg")
    if not cusps or len(cusps) < 12:
        return []
    sign_codes = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    rows = []
    for i, cusp in enumerate(cusps[:12]):
        deg = cusp
        if use_sidereal:
            try:
                from .. import sidereal
                vedic = engine_json.get("vedic") or {}
                aya = (vedic.get("ayanamsha") or {}).get("mode") or "Lahiri"
                jd_tt = (engine_json.get("time") or {}).get("jd_tt")
                if jd_tt is not None:
                    sid_mode = sidereal.AYANAMSHA_MODES.get(aya, sidereal.SE_SIDM_LAHIRI)
                    aya_deg, _, _ = sidereal.ayanamsha_with_nutation(jd_tt, sid_mode)
                    deg = sidereal.tropical_to_sidereal_deg(cusp, aya_deg)
            except Exception:
                pass
        sign_num = int(deg / 30) % 12
        rows.append({
            "house": i + 1,
            "cusp": format_degrees(deg),
            "sign": sign_code_to_nl(sign_codes[sign_num]),
        })
    return rows


def _aspect_table(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    western = engine_json.get("western")
    if not western:
        return []
    aspects_list = western.get("aspects") or []
    rows = []
    for a in aspects_list:
        orb = a.get("orb_deg") or a.get("orb_degrees") or 0.0
        applying = a.get("applying", False)
        body_a = a.get("a", "")
        body_b = a.get("b", "")
        label_a = BODY_LABELS_NL.get(body_a, body_a)
        label_b = BODY_LABELS_NL.get(body_b, body_b)
        aspect_symbols = {"conjunction": "☌", "sextile": "⚹", "square": "□", "trine": "△", "opposition": "☍"}
        sym = aspect_symbols.get(a.get("type", ""), a.get("type", ""))
        pair = f"{label_a} {sym} {label_b}"
        orb_str = format_degrees(orb)
        if applying:
            orb_str += " (applicerend)"
        else:
            orb_str += " (separerend)"
        rows.append({
            "pair": pair,
            "orb": orb_str,
            "applying": applying,
        })
    return rows


def _planet_lons_for_wheel(engine_json: dict[str, Any], sidereal: bool = False) -> dict[str, float]:
    bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
    out = {}
    aya_deg = 0.0
    if sidereal:
        try:
            from .. import sidereal as sid
            vedic = engine_json.get("vedic") or {}
            aya_mode = (vedic.get("ayanamsha") or {}).get("mode") or "Lahiri"
            jd_tt = (engine_json.get("time") or {}).get("jd_tt")
            if jd_tt is not None:
                sm = sid.AYANAMSHA_MODES.get(aya_mode, sid.SE_SIDM_LAHIRI)
                aya_deg, _, _ = sid.ayanamsha_with_nutation(jd_tt, sm)
        except Exception:
            pass
    for bid, b in bodies.items():
        if not isinstance(b, dict):
            continue
        lon = b.get("lon_deg")
        if lon is not None and (b.get("quality") or {}).get("computed", True):
            if sidereal:
                lon = sid.tropical_to_sidereal_deg(lon, aya_deg)
            lbl = BODY_2LETTER.get(bid, bid[:2])
            out[lbl] = lon
    return out


def _cusps_and_asc(engine_json: dict[str, Any], sidereal: bool = False) -> tuple[Optional[list[float]], Optional[float]]:
    western = engine_json.get("western")
    if not western:
        return None, None
    houses = western.get("houses") or {}
    angles = houses.get("angles") or {}
    cusps = houses.get("cusps_deg")
    asc = angles.get("asc_deg") or angles.get("angles_asc_deg")
    if sidereal and (cusps or asc is not None):
        try:
            from .. import sidereal as sid
            vedic = engine_json.get("vedic") or {}
            aya_mode = (vedic.get("ayanamsha") or {}).get("mode") or "Lahiri"
            jd_tt = (engine_json.get("time") or {}).get("jd_tt")
            if jd_tt is not None:
                sm = sid.AYANAMSHA_MODES.get(aya_mode, sid.SE_SIDM_LAHIRI)
                aya_deg, _, _ = sid.ayanamsha_with_nutation(jd_tt, sm)
                if cusps:
                    cusps = [sid.tropical_to_sidereal_deg(c, aya_deg) for c in cusps]
                if asc is not None:
                    asc = sid.tropical_to_sidereal_deg(asc, aya_deg)
        except Exception:
            pass
    return (list(cusps) if cusps else None), asc


def _panchanga_cards(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    vedic = engine_json.get("vedic") or {}
    panchanga = vedic.get("panchanga")
    if not panchanga:
        return []
    tithi = (panchanga.get("tithi") or {}).get("index")
    nakshatra = (panchanga.get("nakshatra") or {}).get("index")
    yoga = (panchanga.get("yoga") or {}).get("index")
    vaara = panchanga.get("vaara")
    k = panchanga.get("karana") or {}
    k_indices = k.get("indices") or []
    cards = []
    if vaara:
        cards.append({"label": "Vaara", "value": vaara})
    if tithi is not None:
        cards.append({"label": "Tithi", "value": str(tithi)})
    if nakshatra is not None:
        cards.append({"label": "Nakshatra", "value": str(nakshatra)})
    if yoga is not None:
        cards.append({"label": "Yoga", "value": str(yoga)})
    if k_indices:
        cards.append({"label": "Karana", "value": ", ".join(str(x) for x in k_indices)})
    return cards


def _end_times(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    vedic = engine_json.get("vedic") or {}
    panchanga = vedic.get("panchanga")
    if not panchanga:
        return []
    items = []
    for key, label in [("tithi", "Tithi eindigt"), ("nakshatra", "Nakshatra eindigt"), ("yoga", "Yoga eindigt")]:
        block = panchanga.get(key)
        if isinstance(block, dict):
            end_local = block.get("ends_at_local")
            items.append({
                "label": label,
                "value": end_local if end_local else "eindtijd niet berekend",
            })
    return items


def _pillars_table(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    chinese = engine_json.get("chinese") or {}
    bazi = chinese.get("bazi_pillars") or {}
    if not bazi:
        return []
    rows = []
    for key in ["year", "month", "day", "hour"]:
        p = bazi.get(key)
        if isinstance(p, dict):
            stem = p.get("stem", "")
            branch = p.get("branch", "")
            rows.append({"pillar": key, "stem": stem, "branch": branch})
    return rows


def _solar_terms_timeline(engine_json: dict[str, Any]) -> list[dict[str, Any]]:
    chinese = engine_json.get("chinese") or {}
    terms = chinese.get("solar_terms")
    if not terms or not isinstance(terms, dict):
        return []
    items = []
    for k, v in sorted(terms.items(), key=lambda x: (int(x[0]) if x[0].isdigit() else 0)):
        items.append({"index": k, "time_utc": v})
    return items


def _western_available(engine_json: dict[str, Any]) -> bool:
    western = engine_json.get("western")
    if western is None:
        return False
    houses = (western or {}).get("houses") or {}
    cusps = houses.get("cusps_deg")
    return cusps is not None and len(cusps) >= 12


def _western_tropical_status(engine_json: dict[str, Any]) -> dict[str, Any]:
    has_loc = _completeness(engine_json).get("has_location", False)
    has_tz = _completeness(engine_json).get("has_timezone", False)
    has_time = _completeness(engine_json).get("has_time", False)
    requires = ["date", "time"]
    if has_loc:
        requires.append("latlon")
    if has_tz:
        requires.append("timezone")
    available = bool(engine_json.get("western")) and has_loc and has_tz and has_time
    diag = normalize_diagnostics(engine_json)
    conf = diag.get("confidence_overall", "high")
    return {"confidence": conf, "requires": requires}


def _completeness(engine_json: dict[str, Any]) -> dict[str, bool]:
    return _input_summary(engine_json).get("completeness", {})


def build_view_model(
    engine_json: dict[str, Any],
    *,
    locale: str = "nl-NL",
    base_url: str = "",
) -> dict[str, Any]:
    """
    Build ViewModel from engine output.
    """
    meta = engine_json.get("meta") or {}
    generated = meta.get("generated_at_utc") or ""
    diag = normalize_diagnostics(engine_json)
    completeness = _input_summary(engine_json).get("completeness", {})
    methods = []

    # Western tropical
    wt_available = engine_json.get("western") is not None
    wt_status = _western_tropical_status(engine_json)
    planet_lons_wt = _planet_lons_for_wheel(engine_json, sidereal=False)
    cusps_wt, asc_wt = _cusps_and_asc(engine_json, sidereal=False)
    wheel_url_wt = f"{base_url}/api/render/wheel.svg?method=western_tropical" if base_url else "/api/render/wheel.svg?method=western_tropical"
    methods.append({
        "id": "western_tropical",
        "label_nl": "Westers (tropisch)",
        "available": wt_available,
        "status": wt_status,
        "sections": {
            "planet_table": _planet_table_tropical(engine_json),
            "aspect_table": _aspect_table(engine_json),
            "houses_table": _houses_table(engine_json, use_sidereal=False),
            "wheel": {"svg_url": wheel_url_wt, "planet_lons": planet_lons_wt, "cusps": cusps_wt, "asc_deg": asc_wt},
        },
    })

    # Western sidereal
    bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
    ws_available = bool(bodies)
    vedic = engine_json.get("vedic") or {}
    aya = vedic.get("ayanamsha") or {}
    aya_err = False
    try:
        from .. import sidereal
        jd_tt = (engine_json.get("time") or {}).get("jd_tt")
        if jd_tt is not None:
            _, _, aya_err = sidereal.ayanamsha_with_nutation(jd_tt, sidereal.SE_SIDM_LAHIRI)
    except Exception:
        aya_err = True
    ws_available = ws_available and not aya_err
    planet_lons_ws = _planet_lons_for_wheel(engine_json, sidereal=True)
    cusps_ws, asc_ws = _cusps_and_asc(engine_json, sidereal=True)
    wheel_url_ws = f"{base_url}/api/render/wheel.svg?method=western_sidereal" if base_url else "/api/render/wheel.svg?method=western_sidereal"
    methods.append({
        "id": "western_sidereal",
        "label_nl": "Westers (sidereaal)",
        "available": ws_available,
        "status": {"confidence": diag.get("confidence_overall", "high"), "requires": ["date", "time"]},
        "sections": {
            "planet_table": _planet_table_sidereal(engine_json),
            "houses_table": _houses_table(engine_json, use_sidereal=True),
            "aspect_table": [],
            "wheel": {"svg_url": wheel_url_ws, "planet_lons": planet_lons_ws, "cusps": cusps_ws, "asc_deg": asc_ws},
        },
    })

    # Vedic Panchanga
    vp_available = engine_json.get("vedic") is not None
    methods.append({
        "id": "vedic_panchanga",
        "label_nl": "Vedisch (Panchanga)",
        "available": vp_available,
        "status": {"confidence": diag.get("confidence_overall", "high"), "requires": ["date", "time"]},
        "sections": {
            "panchanga_cards": _panchanga_cards(engine_json),
            "end_times": _end_times(engine_json),
        },
    })

    # Chinese Ganzhi/BaZi
    ch_available = engine_json.get("chinese") is not None
    methods.append({
        "id": "chinese_ganzhi_bazi",
        "label_nl": "Chinees (Ganzhi/BaZi)",
        "available": ch_available,
        "status": {"confidence": "medium" if "CNY_LEAP_RULES_SIMPLIFIED" in diag.get("codes", []) else "high", "requires": ["date", "time", "timezone"]},
        "sections": {
            "pillars_table": _pillars_table(engine_json),
            "solar_terms_timeline": _solar_terms_timeline(engine_json),
        },
    })

    # Human Design
    hd_block = engine_json.get("human_design") or {}
    hd_available = bool(hd_block) and hd_block.get("type") is not None
    methods.append({
        "id": "human_design",
        "label_nl": "Human Design",
        "available": hd_available,
        "status": {
            "confidence": (hd_block.get("status") or {}).get("confidence", "high"),
            "requires": (hd_block.get("status") or {}).get("requires", ["date", "time"]),
        },
        "sections": _human_design_sections(engine_json),
    })

    # Maya
    maya_block = engine_json.get("maya") or {}
    maya_available = bool(maya_block) and maya_block.get("kin") is not None
    methods.append({
        "id": "maya",
        "label_nl": "Maya (Tzolkin / Haab)",
        "available": maya_available,
        "status": {
            "confidence": (maya_block.get("status") or {}).get("confidence", "high"),
            "requires": (maya_block.get("status") or {}).get("requires", ["date"]),
        },
        "sections": _maya_sections(engine_json),
    })

    return {
        "locale": locale,
        "generated_at_utc": generated,
        "input_summary": _input_summary(engine_json),
        "diagnostics": diag,
        "methods": methods,
    }


def _human_design_sections(engine_json: dict[str, Any]) -> dict[str, Any]:
    hd = engine_json.get("human_design") or {}
    if not isinstance(hd, dict) or not hd.get("type"):
        return {"summary_cards": [], "channels_table": [], "personality_table": [], "design_table": []}
    summary_cards = [
        {"label": "Type", "value": hd.get("type") or "-"},
        {"label": "Strategie", "value": (hd.get("strategy") or {}).get("text", "-")},
        {"label": "Authoriteit", "value": hd.get("authority") or "-"},
        {"label": "Profiel", "value": (hd.get("profile") or {}).get("value") or "-"},
        {"label": "Incarnation Cross", "value": (hd.get("incarnation_cross") or {}).get("name_short", "-")},
    ]
    channels_table = []
    for ch in hd.get("channels") or []:
        gates = ch.get("gates") or [None, None]
        channels_table.append({
            "channel": ch.get("name") or "-",
            "gates": f"{gates[0]} - {gates[1]}",
            "circuit": ch.get("circuit") or "-",
            "theme": ch.get("theme") or "-",
        })
    personality_table = []
    for body, data in (hd.get("personality") or {}).items():
        personality_table.append({
            "body": body,
            "gate": data.get("gate"),
            "line": data.get("line"),
            "lon": data.get("lon_deg"),
        })
    design_table = []
    for body, data in (hd.get("design") or {}).items():
        design_table.append({
            "body": body,
            "gate": data.get("gate"),
            "line": data.get("line"),
            "lon": data.get("lon_deg"),
        })
    centers_block = hd.get("centers") or {}
    return {
        "summary_cards": summary_cards,
        "channels_table": channels_table,
        "personality_table": personality_table,
        "design_table": design_table,
        "centers": {
            "defined": centers_block.get("defined") or [],
            "undefined": centers_block.get("undefined") or [],
            "all": centers_block.get("all") or [],
        },
        "active_gates": hd.get("active_gates") or [],
        "gate_sources": hd.get("gate_sources") or {},
    }


def _maya_sections(engine_json: dict[str, Any]) -> dict[str, Any]:
    maya = engine_json.get("maya") or {}
    if not isinstance(maya, dict) or not maya.get("kin"):
        return {"summary_cards": [], "wavespell": None, "personal_year_cycles": []}
    sign = maya.get("sign") or {}
    tone = maya.get("tone") or {}
    summary_cards = [
        {"label": "Kin", "value": str(maya.get("kin") or "-")},
        {"label": "Tzolkin", "value": maya.get("tzolkin", {}).get("label", "-")},
        {"label": "Haab", "value": maya.get("haab", {}).get("label", "-")},
        {"label": "Long Count", "value": maya.get("long_count", {}).get("label", "-")},
        {"label": "Day sign", "value": sign.get("yucatec") or "-"},
        {"label": "Galactic tone", "value": tone.get("name_en") or "-"},
    ]
    return {
        "summary_cards": summary_cards,
        "sign": sign,
        "tone": tone,
        "wavespell": maya.get("wavespell") or {},
        "harmonic": maya.get("harmonic") or {},
        "personal_year_cycles": maya.get("personal_year_cycles") or [],
        "long_count": maya.get("long_count") or {},
        "tzolkin": maya.get("tzolkin") or {},
        "haab": maya.get("haab") or {},
    }
