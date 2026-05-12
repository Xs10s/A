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


ASPECT_TO_FORMULA: dict[str, str] = {
    "conjunction": "CON",
    "sextile": "SEX",
    "square": "SQU",
    "trine": "TRI",
    "opposition": "OPP",
}

FORMULA_TO_ASPECT: dict[str, str] = {v: k for k, v in ASPECT_TO_FORMULA.items()}

SUPPORTED_PLANETS: set[str] = {
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
}


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


def _formula_error_result(formula: str, summary: str, details: str) -> dict[str, Any]:
    return {
        "formula": formula,
        "title": "Formule niet beschikbaar",
        "summary": summary,
        "explanation": details,
        "keywords": ["fout", "formule"],
        "confidence": "geen",
        "sourceData": {"error": summary},
    }


def _point_source_data(planet: str, placement: dict[str, Any]) -> dict[str, Any]:
    return {
        "planet": planet,
        "sign": placement.get("sign"),
        "house": placement.get("house"),
        "degreeInSign": placement.get("degree_in_sign"),
        "retrograde": placement.get("retrograde"),
    }


def _parse_formula(formula: str) -> list[str]:
    if not isinstance(formula, str) or not formula.strip():
        raise ValueError("Lege formule.")
    parts = [p.strip().upper() for p in formula.split("|")]
    if not parts or any(not p for p in parts):
        raise ValueError("Ongeldige formule.")
    return parts


def _normalize_planet_token(token: str) -> Optional[str]:
    upper = token.upper()
    for planet in SUPPORTED_PLANETS:
        if planet.upper() == upper:
            return planet
    return None


def _find_aspect_entry(
    aspects: list[dict[str, Any]], left_planet: str, aspect_code: str, right_planet: str
) -> Optional[dict[str, Any]]:
    aspect_name = FORMULA_TO_ASPECT.get(aspect_code)
    if not aspect_name:
        return None

    matches: list[dict[str, Any]] = []
    for item in aspects:
        if not isinstance(item, dict):
            continue
        a = item.get("a")
        b = item.get("b")
        t = item.get("type")
        if t != aspect_name:
            continue
        if (a == left_planet and b == right_planet) or (a == right_planet and b == left_planet):
            matches.append(item)
    if not matches:
        return None
    return min(matches, key=lambda x: float(x.get("orb_deg", x.get("orb_degrees", 999.0))))


def interpret_western_formula(formula: str, western_block: dict[str, Any], *, locale: str = "nl-NL") -> dict[str, Any]:
    _ = locale  # Formula output is intentionally Dutch per product requirement.
    placements = western_block.get("placements") if isinstance(western_block, dict) else {}
    aspects = western_block.get("aspects") if isinstance(western_block, dict) else []
    placements = placements if isinstance(placements, dict) else {}
    aspects = aspects if isinstance(aspects, list) else []

    if not placements:
        return _formula_error_result(
            formula,
            "Nog geen horoscoopdata beschikbaar.",
            "Er zijn nog geen Westerse plaatsingen beschikbaar om deze formule te interpreteren.",
        )

    try:
        parts = _parse_formula(formula)
    except ValueError as exc:
        return _formula_error_result(formula, str(exc), "Controleer het formaat, bijvoorbeeld: SUN | SIGN.")

    left_planet = _normalize_planet_token(parts[0])
    if left_planet is None:
        return _formula_error_result(
            formula,
            f"Ongeldig hemellichaam: {parts[0]}",
            "Gebruik een bekend hemellichaam zoals SUN, MOON, MERCURY, VENUS, MARS, JUPITER of SATURN.",
        )
    left_placement = placements.get(left_planet)
    if not isinstance(left_placement, dict):
        return _formula_error_result(
            formula,
            "Nog geen horoscoopdata beschikbaar.",
            f"Voor {left_planet} is nog geen plaatsing beschikbaar in de chartdata.",
        )

    if len(parts) == 2:
        relation = parts[1]
        if relation == "SIGN":
            sign = left_placement.get("sign")
            house = left_placement.get("house")
            return {
                "formula": formula,
                "title": f"{left_planet} in teken",
                "summary": f"{left_planet} staat in {sign}.",
                "explanation": (
                    f"{left_planet} staat in {sign}. Dit laat zien via welke tekenkwaliteit deze planeet "
                    "zich in jouw chart uitdrukt."
                ),
                "keywords": [left_planet, str(sign), "teken"],
                "confidence": "hoog",
                "sourceData": _point_source_data(left_planet, left_placement) | {"house": house},
            }
        if relation == "HOUSE":
            house = left_placement.get("house")
            return {
                "formula": formula,
                "title": f"{left_planet} in huis",
                "summary": f"{left_planet} werkt primair via huis {house}.",
                "explanation": (
                    f"{left_planet} staat in huis {house}. Dat maakt dit levensgebied de hoofdplek waar "
                    "de energie van deze planeet zichtbaar wordt."
                ),
                "keywords": [left_planet, f"huis {house}", "plaatsing"],
                "confidence": "hoog",
                "sourceData": _point_source_data(left_planet, left_placement),
            }
        if relation == "FULL":
            sign = left_placement.get("sign")
            house = left_placement.get("house")
            degree = left_placement.get("degree_in_sign")
            degree_txt = f"{float(degree):.2f}°" if isinstance(degree, (int, float)) else "onbekende graad"
            return {
                "formula": formula,
                "title": f"{left_planet} volledige plaatsing",
                "summary": f"{left_planet} staat in {sign}, huis {house}.",
                "explanation": (
                    f"{left_planet} staat op {degree_txt} in {sign}, in huis {house}. "
                    "Deze combinatie verbindt planeetfunctie, tekenstijl en levensgebied in één inzicht."
                ),
                "keywords": [left_planet, str(sign), f"huis {house}", "full"],
                "confidence": "hoog",
                "sourceData": _point_source_data(left_planet, left_placement),
            }
        if relation.isdigit():
            house_number = int(relation)
            if house_number < 1 or house_number > 12:
                return _formula_error_result(
                    formula,
                    f"Ongeldig huisnummer: {house_number}",
                    "Gebruik een huisnummer tussen 1 en 12.",
                )
            actual_house = left_placement.get("house")
            return {
                "formula": formula,
                "title": f"{left_planet} t.o.v. huis {house_number}",
                "summary": f"{left_planet} gelezen op huisrelatie {house_number}.",
                "explanation": (
                    f"Deze formule bekijkt {left_planet} relationeel op huis {house_number}. "
                    f"De feitelijke plaatsing in de chart is huis {actual_house}."
                ),
                "keywords": [left_planet, f"huis {house_number}", "relationeel"],
                "confidence": "relationeel",
                "sourceData": _point_source_data(left_planet, left_placement)
                | {"targetHouse": house_number, "actualHouse": actual_house},
            }
        return _formula_error_result(
            formula,
            "Deze formule wordt nog niet ondersteund.",
            "Ondersteunde tweedelige formules: PLANET | SIGN, HOUSE, FULL of huisnummer 1-12.",
        )

    if len(parts) == 3:
        relation = parts[1]
        right = parts[2]

        if relation in FORMULA_TO_ASPECT:
            right_planet = _normalize_planet_token(right)
            if right_planet is None:
                return _formula_error_result(
                    formula,
                    f"Ongeldig hemellichaam: {right}",
                    "Gebruik een bekend tweede hemellichaam voor aspectformules.",
                )
            entry = _find_aspect_entry(aspects, left_planet, relation, right_planet)
            if entry is None:
                return _formula_error_result(
                    formula,
                    "Deze relatie is niet actief binnen de ingestelde orb.",
                    "Er is geen actief aspect gevonden voor deze combinatie binnen de huidige orb-instellingen.",
                )
            orb = entry.get("orb_deg", entry.get("orb_degrees"))
            return {
                "formula": formula,
                "title": f"{left_planet} {relation} {right_planet}",
                "summary": f"{left_planet} staat in {relation} met {right_planet}.",
                "explanation": (
                    f"{left_planet} en {right_planet} vormen een actief aspect ({relation}) met orb {float(orb):.2f}°. "
                    "Deze relatie is direct herleidbaar naar de berekende aspecten in de chart."
                ),
                "keywords": [left_planet, right_planet, relation, "aspect"],
                "confidence": "hoog",
                "sourceData": {
                    "left": _point_source_data(left_planet, left_placement),
                    "right": _point_source_data(right_planet, placements.get(right_planet, {})),
                    "aspect": {
                        "type": entry.get("type"),
                        "orb": orb,
                        "applying": entry.get("applying"),
                        "exactAngle": entry.get("exact_angle_deg"),
                    },
                },
            }

        if relation == "SIGN" and right == "HOUSE":
            sign = left_placement.get("sign")
            house = left_placement.get("house")
            return {
                "formula": formula,
                "title": f"{left_planet} teken-huis combinatie",
                "summary": f"{left_planet} combineert teken {sign} met huis {house}.",
                "explanation": (
                    f"{left_planet} staat in {sign} en huis {house}. Volgens data × relatie × data "
                    "ontstaat inzicht door de combinatie van planeetfunctie, tekenstijl en levensgebied."
                ),
                "keywords": [left_planet, str(sign), f"huis {house}", "combinatie"],
                "confidence": "hoog",
                "sourceData": _point_source_data(left_planet, left_placement),
            }

        return _formula_error_result(
            formula,
            "Deze formule wordt nog niet ondersteund.",
            "Ondersteunde driedelige formules: PLANET | ASPECT | PLANET en PLANET | SIGN | HOUSE.",
        )

    return _formula_error_result(
        formula,
        "Deze formule wordt nog niet ondersteund.",
        "Gebruik een formule met twee of drie delen gescheiden door '|'.",
    )


def build_western_formula_interpretations(
    western_block: dict[str, Any], *, locale: str = "nl-NL"
) -> dict[str, Any]:
    placements = western_block.get("placements") if isinstance(western_block, dict) else {}
    aspects = western_block.get("aspects") if isinstance(western_block, dict) else []
    placements = placements if isinstance(placements, dict) else {}
    aspects = aspects if isinstance(aspects, list) else []

    if not placements:
        return {
            "sections": {
                "placements": [
                    _formula_error_result(
                        "AUTO | PLACEMENTS",
                        "Nog geen horoscoopdata beschikbaar.",
                        "Er zijn nog geen Westerse plaatsingen beschikbaar voor interpretatie.",
                    )
                ],
                "aspects": [],
                "deepInsights": [],
            }
        }

    placement_formulas = [f"{planet.upper()} | FULL" for planet in placements.keys()]
    aspect_formulas: list[str] = []
    for item in aspects[:12]:
        if not isinstance(item, dict):
            continue
        code = ASPECT_TO_FORMULA.get(str(item.get("type")))
        a = item.get("a")
        b = item.get("b")
        if code and a and b:
            aspect_formulas.append(f"{str(a).upper()} | {code} | {str(b).upper()}")

    deep_formulas: list[str] = []
    if "Sun" in placements:
        deep_formulas.append("SUN | SIGN")
    if "Moon" in placements:
        deep_formulas.append("MOON | HOUSE")
    if placement_formulas:
        first_planet = next(iter(placements.keys()))
        deep_formulas.append(f"{first_planet.upper()} | SIGN | HOUSE")
    if aspect_formulas:
        deep_formulas.append(aspect_formulas[0])

    return {
        "sections": {
            "placements": [interpret_western_formula(f, western_block, locale=locale) for f in placement_formulas],
            "aspects": [interpret_western_formula(f, western_block, locale=locale) for f in aspect_formulas],
            "deepInsights": [interpret_western_formula(f, western_block, locale=locale) for f in deep_formulas],
        }
    }


def build_interpretations(engine_json: dict[str, Any], *, locale: str = "nl-NL") -> dict[str, Any]:
    """
    Build structured extended interpretations per method.

    Returns a dict with keys:
      - western_tropical
      - western_sidereal
      - vedic_panchanga
      - chinese_ganzhi_bazi
      - human_design
      - maya
      - method_explanations: per-method bundles with headline + personal_layer blocks
        (see horoscoop.method_explanations). Keys mirror the methods above plus _meta.version.
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
    western_tropical["formula_interpretations"] = build_western_formula_interpretations(
        western_blocks, locale=locale
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

    # Human Design narrative
    hd_block = engine_json.get("human_design") or {}
    human_design_out: dict[str, Any] = {"summary": "", "type": None, "authority": None,
                                         "profile": None, "centers": None,
                                         "channels": [], "incarnation_cross": None}
    if isinstance(hd_block, dict) and hd_block.get("type"):
        type_str = hd_block.get("type")
        auth = hd_block.get("authority")
        prof = (hd_block.get("profile") or {}).get("value")
        cross = (hd_block.get("incarnation_cross") or {}).get("name_short")
        if lang == "nl":
            human_design_out["summary"] = (
                f"Je bent een {type_str} met {auth}-authoriteit en profiel {prof}. "
                f"Het thema-kruis is: {cross}. Strategie en authoriteit blijven leidend "
                "voor besluiten; het bodygraph laat zien welke energieën consistent en welke "
                "open zijn."
            )
        else:
            human_design_out["summary"] = (
                f"You are a {type_str} with {auth} authority and profile {prof}. "
                f"The theme cross is: {cross}. Strategy and authority guide decisions; "
                "the bodygraph shows which energies are consistent and which are open."
            )
        human_design_out["type"] = type_str
        human_design_out["authority"] = auth
        human_design_out["profile"] = hd_block.get("profile")
        human_design_out["centers"] = hd_block.get("centers")
        human_design_out["channels"] = hd_block.get("channels")
        human_design_out["incarnation_cross"] = hd_block.get("incarnation_cross")
        human_design_out["strategy"] = hd_block.get("strategy")

    # Maya narrative
    maya_block = engine_json.get("maya") or {}
    maya_out: dict[str, Any] = {"summary": "", "kin": None, "tone": None, "sign": None,
                                "wavespell": None, "haab": None, "long_count": None}
    if isinstance(maya_block, dict) and maya_block.get("kin"):
        sign_meta = maya_block.get("sign") or {}
        tone_meta = maya_block.get("tone") or {}
        kw = sign_meta.get("kw_nl") if lang == "nl" else sign_meta.get("kw_en")
        tone_kw = tone_meta.get("kw_nl") if lang == "nl" else tone_meta.get("kw_en")
        if lang == "nl":
            maya_out["summary"] = (
                f"Je Maya-kin is {maya_block.get('kin')} ({tone_meta.get('name_nl')} "
                f"{sign_meta.get('nl')}). Kernkwaliteit: {kw}. Tooneffect: {tone_kw}. "
                "De wavespell en het kasteel laten zien in welk groter ritme je leeft."
            )
        else:
            maya_out["summary"] = (
                f"Your Maya kin is {maya_block.get('kin')} ({tone_meta.get('name_en')} "
                f"{sign_meta.get('en')}). Core quality: {kw}. Tone effect: {tone_kw}. "
                "The wavespell and castle show the broader rhythm you live in."
            )
        maya_out["kin"] = maya_block.get("kin")
        maya_out["tone"] = maya_block.get("tone")
        maya_out["sign"] = maya_block.get("sign")
        maya_out["wavespell"] = maya_block.get("wavespell")
        maya_out["haab"] = maya_block.get("haab")
        maya_out["long_count"] = maya_block.get("long_count")

    from .method_explanations import build_method_explanations

    method_explanations = build_method_explanations(engine_json, locale=locale)

    return {
        "western_tropical": western_tropical,
        "western_sidereal": western_sidereal,
        "vedic_panchanga": panchanga_out,
        "chinese_ganzhi_bazi": chinese_out,
        "human_design": human_design_out,
        "maya": maya_out,
        "method_explanations": method_explanations,
    }

