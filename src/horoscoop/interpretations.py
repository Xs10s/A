"""
Interpretations layer (NL/EN) built on top of the deterministic engine output.

Goal:
- Provide extended meaning text for computed values (aspects, houses, planets, pillars, tithi, etc.)
- Work without external KB infrastructure (seed knowledgebase tables in knowledgebase.py)
"""

from __future__ import annotations

from typing import Any, Optional

from .knowledgebase import (
    aspect_meaning,
    branch_meaning,
    house_meaning,
    karana_meaning,
    nakshatra_meaning,
    pillar_meaning,
    planet_meaning,
    sign_meaning,
    solar_term_meaning,
    stem_meaning,
    tithi_meaning,
    vaara_meaning,
    yoga_meaning,
    normalize_locale,
)


SIGN_CODES: list[str] = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _sign_from_lon_deg(lon_deg: float) -> str:
    idx = int(lon_deg / 30.0) % 12
    return SIGN_CODES[idx]


def _extended_planet_paragraph(
    locale: Optional[str],
    *,
    planet: str,
    sign: Optional[str],
    house: Optional[int],
) -> str:
    lang = normalize_locale(locale)
    p_txt = planet_meaning(locale, planet)
    s_txt = sign_meaning(locale, sign)
    h_txt = house_meaning(locale, house)
    if lang == "nl":
        house_part = f" In huis {house}: {h_txt}" if house is not None else f" {h_txt}"
        sign_part = f" Met het teken {sign}: {s_txt}" if sign else ""
        return (
            f"{p_txt}{sign_part}{house_part} "
            "Samen geeft dit een duidelijke kleur aan hoe jij energie omzet in keuzes, relaties en groei."
        )
    house_part = f" In house {house}: {h_txt}" if house is not None else f" {h_txt}"
    sign_part = f" With the sign {sign}: {s_txt}" if sign else ""
    return (
        f"{p_txt}{sign_part}{house_part} "
        "Together, this describes how you translate energy into decisions, relationships, and growth."
    )


def _extended_aspect_paragraph(
    locale: Optional[str],
    *,
    a: str,
    b: str,
    aspect_type: str,
    applying: bool,
    orb_deg: Optional[float] = None,
) -> str:
    lang = normalize_locale(locale)
    base = aspect_meaning(locale, aspect_type, applying=applying)
    orb_part = f" (orb {orb_deg:.2f}°)" if isinstance(orb_deg, (int, float)) else ""
    if lang == "nl":
        return (
            f"Aspect: {a} {aspect_type} {b}{orb_part}. {base} "
            "Als je dit bewust inzet, wordt het makkelijker om spanning te benutten of steun te ontvangen."
        )
    return (
        f"Aspect: {a} {aspect_type} {b}{orb_part}. {base} "
        "When you actively work with it, tension becomes usable and support becomes easier to receive."
    )


def build_interpretations(engine_json: dict[str, Any], *, locale: str = "nl-NL") -> dict[str, Any]:
    """
    Build structured extended interpretations per method.

    Returns a dict with keys:
      - western_tropical
      - western_sidereal
      - vedic_panchanga
      - chinese_ganzhi_bazi
    """
    _ = engine_json  # engine_json is expected to contain all blocks per schema
    lang = normalize_locale(locale)

    western = engine_json.get("western") or {}
    western_blocks = western if isinstance(western, dict) else {}
    placements = western_blocks.get("placements") or {}
    aspects = western_blocks.get("aspects") or []
    houses = western_blocks.get("houses") or {}
    angles = houses.get("angles") or {}
    asc_deg = angles.get("asc_deg")

    western_tropical: dict[str, Any] = {"summary": "", "planets": [], "aspects": [], "houses": [], "asc": None}

    if isinstance(placements, dict) and placements:
        western_tropical["planets"] = [
            {
                "planet": planet,
                "sign": (p.get("sign") if isinstance(p, dict) else None),
                "house": (p.get("house") if isinstance(p, dict) else None),
                "text": _extended_planet_paragraph(
                    locale,
                    planet=planet,
                    sign=(p.get("sign") if isinstance(p, dict) else None),
                    house=(p.get("house") if isinstance(p, dict) else None),
                ),
            }
            for planet, p in placements.items()
            if isinstance(p, dict)
        ]

    # Ascendant interpretation (house 1)
    if isinstance(asc_deg, (int, float)):
        asc_sign = _sign_from_lon_deg(float(asc_deg))
        western_tropical["asc"] = {
            "sign": asc_sign,
            "house": 1,
            "text": _extended_planet_paragraph(locale, planet="Asc", sign=asc_sign, house=1),
        }

    # Houses: include all for completeness
    western_tropical["houses"] = [
        {"house": i, "text": house_meaning(locale, i)} for i in range(1, 13)
    ]

    # Aspects: all aspects found (sorted by orb ascending)
    if isinstance(aspects, list) and aspects:
        filtered = []
        for a in aspects:
            if not isinstance(a, dict):
                continue
            try:
                orb = a.get("orb_deg") if a.get("orb_deg") is not None else a.get("orb_degrees")
                orb_f = float(orb) if orb is not None else None
            except Exception:
                orb_f = None
            filtered.append(
                (
                    a.get("type") or "",
                    orb_f if orb_f is not None else 999.0,
                    bool(a.get("applying", False)),
                    a.get("a") or "",
                    a.get("b") or "",
                    a.get("orb_deg") if "orb_deg" in a else a.get("orb_degrees"),
                )
            )

        filtered.sort(key=lambda x: x[1])
        western_tropical["aspects"] = [
            {
                "type": t,
                "a": aa,
                "b": bb,
                "applying": app,
                "orb_deg": orb,
                "text": _extended_aspect_paragraph(
                    locale,
                    a=aa,
                    b=bb,
                    aspect_type=t,
                    applying=app,
                    orb_deg=orb,
                ),
            }
            for t, orb, app, aa, bb, _orb_raw in filtered
        ]

    western_tropical["summary"] = (
        "Westers overzicht (tropisch): planeten + tekens + huizen + kernaspecten laten zien waar jouw energie naartoe stroomt."
        if lang == "nl"
        else "Western overview (tropical): planets + signs + houses + core aspects show where your energy flows."
    )

    # Sidereal: for now, provide sign meanings based on sidereal conversion of planet longitudes.
    # House meanings are kept identical (house cusps are not recomputed here).
    western_sidereal: dict[str, Any] = {"summary": "", "planets": [], "aspects": [], "houses": [], "asc": None}
    vedic = engine_json.get("vedic") or {}
    time_block = engine_json.get("time") or {}
    jd_tt = time_block.get("jd_tt")
    aya_mode = (vedic.get("ayanamsha") or {}).get("mode") if isinstance(vedic, dict) else None
    asc_deg_sidereal = None

    try:
        from . import sidereal as sid

        if jd_tt is not None:
            sm = sid.AYANAMSHA_MODES.get(aya_mode, sid.SE_SIDM_LAHIRI)
            aya_deg, _, _ = sid.ayanamsha_with_nutation(float(jd_tt), sm)
        else:
            aya_deg = 0.0

        # planets sign: compute from tropical lon_deg
        astronomy_bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
        for planet, p in placements.items() if isinstance(placements, dict) else []:
            if planet not in astronomy_bodies:
                continue
            body_data = astronomy_bodies.get(planet)
            if not isinstance(body_data, dict):
                continue
            lon_trop = body_data.get("lon_deg")
            if lon_trop is None:
                continue
            lon_sid = sid.tropical_to_sidereal_deg(float(lon_trop), float(aya_deg))
            sign_sid = _sign_from_lon_deg(lon_sid)
            house_num = None
            house_num = p.get("house") if isinstance(p, dict) else None
            western_sidereal["planets"].append(
                {
                    "planet": planet,
                    "sign": sign_sid,
                    "house": house_num,
                    "text": _extended_planet_paragraph(locale, planet=planet, sign=sign_sid, house=house_num),
                    "note": "Sidereaal teken; huisnummer is (voor nu) niet sidereaal herberekend.",
                }
            )

        if isinstance(asc_deg, (int, float)):
            from . import sidereal as sid2
            if jd_tt is not None:
                # approximate asc sidereal sign by converting asc degree with same ayanamsha delta
                # This is a pragmatic approximation for UI text purposes.
                asc_sid = sid2.tropical_to_sidereal_deg(float(asc_deg), float(aya_deg))
                asc_sign_sid = _sign_from_lon_deg(asc_sid)
                western_sidereal["asc"] = {
                    "sign": asc_sign_sid,
                    "house": 1,
                    "text": _extended_planet_paragraph(locale, planet="Asc", sign=asc_sign_sid, house=1),
                    "note": "Ascendant teken is sidereaal benaderd met de ayanamsha van dit moment.",
                }
    except Exception:
        # If sidereal conversion fails, keep it empty rather than breaking the UI.
        pass

    # Reuse western aspects for sidereal method (aspect geometry is still defined by angular separation).
    western_sidereal["aspects"] = western_tropical.get("aspects") or []
    western_sidereal["houses"] = [{"house": i, "text": house_meaning(locale, i)} for i in range(1, 13)]
    western_sidereal["summary"] = (
        "Westers overzicht (sidereaal): tekens worden vastgelegd op vaste sterren via ayanamsa."
        if lang == "nl"
        else "Western overview (sidereal): signs are anchored to fixed stars via ayanamsa."
    )

    # Vedic interpretations
    vedic = engine_json.get("vedic") or {}
    vedic_panchanga = vedic.get("panchanga") if isinstance(vedic, dict) else None
    panchanga_out: dict[str, Any] = {"summary": "", "vaara": None, "tithi": None, "nakshatra": None, "yoga": None, "karana": None}

    if isinstance(vedic_panchanga, dict):
        vaara = vedic_panchanga.get("vaara")
        tithi = vedic_panchanga.get("tithi") or {}
        nakshatra = vedic_panchanga.get("nakshatra") or {}
        yoga = vedic_panchanga.get("yoga") or {}
        karana = vedic_panchanga.get("karana") or {}
        karana_indices = karana.get("indices") if isinstance(karana, dict) else None

        if vaara:
            base = vaara_meaning(locale, vaara)
            panchanga_out["vaara"] = {"value": vaara, "text": base}

        if isinstance(tithi, dict) and tithi.get("index") is not None:
            idx = tithi.get("index")
            base = tithi_meaning(locale, idx)
            panchanga_out["tithi"] = {"value": idx, "text": base}

        if isinstance(nakshatra, dict) and nakshatra.get("index") is not None:
            idx = nakshatra.get("index")
            base = nakshatra_meaning(locale, idx)
            panchanga_out["nakshatra"] = {"value": idx, "text": base}

        if isinstance(yoga, dict) and yoga.get("index") is not None:
            idx = yoga.get("index")
            base = yoga_meaning(locale, idx)
            panchanga_out["yoga"] = {"value": idx, "text": base}

        if isinstance(karana_indices, list) and karana_indices:
            # show both karanas; first one gets a base paragraph, second gets an extra sentence
            k0 = karana_indices[0]
            base = karana_meaning(locale, k0)
            panchanga_out["karana"] = {
                "value": karana_indices,
                "text": base,
                "note": "Karana bestaat hier uit twee opeenvolgende fasen; dit geeft een extra nuance aan de overgang in tijd.",
            }

    panchanga_out["summary"] = (
        "Vedische Panchanga: dit is de 'weerkaart' van de geboortemomentenergie (tijd als kwaliteit)."
        if lang == "nl"
        else "Vedic Panchanga: this is the 'weather map' of the birth-moment energy (time as quality)."
    )

    # Chinese interpretations
    chinese = engine_json.get("chinese") or {}
    bazi = (chinese.get("bazi_pillars") if isinstance(chinese, dict) else None) or {}

    chinese_out: dict[str, Any] = {"summary": "", "pillars": {}, "solar_terms": None}

    if isinstance(bazi, dict) and bazi:
        for kind in ["year", "month", "day", "hour"]:
            p = bazi.get(kind) or {}
            if not isinstance(p, dict):
                continue
            stem = p.get("stem")
            branch = p.get("branch")
            if not stem or not branch:
                continue
            base = pillar_meaning(locale, pillar_kind=kind, stem=str(stem), branch=str(branch))
            # Extended pillar paragraph: mention stem+branch explicitly.
            stem_txt = stem_meaning(locale, str(stem))
            branch_txt = branch_meaning(locale, str(branch))
            if lang == "nl":
                extra = f" De stem ligt in {stem_txt} en de branch in {branch_txt}. Samen vertelt dit hoe die laag jouw basis ondersteunt en richting geeft."
            else:
                extra = f" The stem carries {stem_txt} and the branch {branch_txt}. Together this shows how that layer supports you and guides direction."
            chinese_out["pillars"][kind] = {"value": f"{stem}{branch}", "text": base + extra}

    # Solar terms (jieqi)
    # - If the engine provides timing, show it.
    # - Otherwise still show the full list of meanings (no timing available).
    solar_terms = chinese.get("solar_terms") if isinstance(chinese, dict) else None
    if isinstance(solar_terms, dict) and solar_terms:
        try:
            keys_sorted = sorted([int(k) for k in solar_terms.keys() if str(k).isdigit()])
        except Exception:
            keys_sorted = []
        items = []
        for idx in keys_sorted:
            items.append(
                {
                    "index": idx,
                    "text": solar_term_meaning(locale, idx),
                    "time_utc": solar_terms.get(str(idx)),
                }
            )
        chinese_out["solar_terms"] = {"count": len(keys_sorted), "items": items}
    else:
        items = [
            {"index": idx, "text": solar_term_meaning(locale, idx), "time_utc": None}
            for idx in range(1, 25)
        ]
        chinese_out["solar_terms"] = {
            "count": len(items),
            "items": items,
            "note": "Geen berekende zonne-termen timing beschikbaar voor deze run; je ziet wel de volledige betekenissen.",
        }
    chinese_out["summary"] = (
        "Chinees kader (Ganzhi/BaZi): je energetische patroon wordt gelezen als cycli (jaar/maand/dag/uur)."
        if lang == "nl"
        else "Chinese frame (Ganzhi/BaZi): your energetic pattern is read as cycles (year/month/day/hour)."
    )

    return {
        "western_tropical": western_tropical,
        "western_sidereal": western_sidereal,
        "vedic_panchanga": panchanga_out,
        "chinese_ganzhi_bazi": chinese_out,
    }

