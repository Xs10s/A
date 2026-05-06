"""
Orchestration: Layer A → B → D. No mixing; deterministic; traceable.
Input: BirthInput → Output: HoroscoopOutput (JSON-serializable).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from . import astronomy as astro
from . import aspects
from . import chinese
from . import eop
from . import houses
from . import models
from . import sidereal
from . import time_scales as ts
from . import vedic


# Defaults
DEFAULT_HOUSE_SYSTEM = "P"
DEFAULT_AYANAMSHA = "Lahiri"
SCHEMA_VERSION = "1.0.0"


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _build_time_block(
    jd_utc: Optional[float],
    jd_ut1: Optional[float],
    jd_tt: Optional[float],
    delta_t_sec: Optional[float],
    delta_t_source: Optional[str],
    ut1_utc_sec: Optional[float],
    ut1_utc_source: Optional[str],
    datetime_utc: Optional[str],
    datetime_local: Optional[str],
    requires: list[models.Requires],
    confidence: models.Confidence,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "datetime_utc": datetime_utc,
        "datetime_local": datetime_local,
        "jd_ut1": jd_ut1,
        "jd_tt": jd_tt,
        "jd": {"ut1": jd_ut1, "tt": jd_tt},
        "jd_tdb": None,
        "delta_t_seconds": delta_t_sec,
        "delta_t_source": delta_t_source,
        "ut1_utc_seconds": ut1_utc_sec,
        "ut1_utc_source": ut1_utc_source,
        "status": {
            "computed": jd_tt is not None,
            "requires": [r.value for r in requires],
            "confidence": confidence.value,
            "assumptions": [],
            "warnings": warnings,
        },
    }


BODY_IDS: list[tuple[int, str]] = [
    (astro.SE_SUN, "Sun"),
    (astro.SE_MOON, "Moon"),
    (astro.SE_MERCURY, "Mercury"),
    (astro.SE_VENUS, "Venus"),
    (astro.SE_MARS, "Mars"),
    (astro.SE_JUPITER, "Jupiter"),
    (astro.SE_SATURN, "Saturn"),
]


def _build_astronomy_block(
    jd_tt: float,
    lat: Optional[float],
    lon: Optional[float],
    height_m: Optional[float],
    body_list: list[tuple[int, str]],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    topo = lat is not None and lon is not None
    for body, bid in body_list:
        if topo and height_m is not None:
            xx, err = astro.calc_planet_topocentric(jd_tt, body, lon, lat, height_m)
        else:
            xx, err = astro.calc_planet_geocentric(jd_tt, body)
        if err or not xx:
            out[bid] = {"error": err, "frame": "ecliptic_true_of_date", "mode": "geocentric" if not topo else "topocentric", "zodiac": "tropical", "lon_deg": None, "lat_deg": None, "quality": {"computed": False, "confidence": "unavailable"}}
        else:
            out[bid] = {
                "frame": "ecliptic_true_of_date",
                "mode": "geocentric" if not topo else "topocentric",
                "zodiac": "tropical",
                "lon_deg": xx[0],
                "lat_deg": xx[1],
                "dist_au": xx[2] if len(xx) > 2 else None,
                "speed_lon_deg_per_day": xx[3] if len(xx) > 3 else None,
                "flags": {},
                "quality": {"computed": True, "confidence": "high", "assumptions": []},
            }
    return out


def _build_western_block(
    jd_ut: float,
    lat_deg: float,
    lon_deg: float,
    house_system: str,
    body_lons: dict[str, float],
    body_speeds: Optional[dict[str, float]] = None,
    aspect_defs: Optional[list[tuple[float, str]]] = None,
    orb_resolver: Optional[Any] = None,
) -> dict[str, Any]:
    from . import db_orbs
    cusps, asc, mc, err = houses.calc_houses(jd_ut, lat_deg, lon_deg, house_system)
    if err:
        return {
            "houses": {"system": house_system, "cusps_deg": None, "angles": {"asc_deg": None, "mc_deg": None}, "status": {"computed": False, "warnings": [err]}},
            "aspects": [],
            "placements": {},
        }
    if cusps and len(cusps) >= 13:
        cusps_list = list(cusps)[1:13]
    elif cusps and len(cusps) >= 12:
        cusps_list = list(cusps)[:12]
    else:
        cusps_list = None
    placements: dict[str, Any] = {}
    for bid, lon in body_lons.items():
        sign_num = int(lon / 30) % 12
        sign_codes = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        degree_in_sign = lon % 30.0
        house_num = houses.house_from_cusps(lon, cusps) if cusps else None
        placements[bid] = {"sign": sign_codes[sign_num], "degree_in_sign": degree_in_sign, "house": house_num, "retrograde": False}
    resolver = orb_resolver if orb_resolver is not None else db_orbs.DefaultOrbResolver()
    def orb_fn(name: str, a: str, b: str) -> float:
        return resolver.get_orb(name, a, b) if hasattr(resolver, "get_orb") else 8.0
    aspect_list: list[dict[str, Any]] = []
    body_ids = list(body_lons.keys())
    speeds = body_speeds or {}
    for i in range(len(body_ids)):
        for j in range(i + 1, len(body_ids)):
            a, b = body_ids[i], body_ids[j]
            sp_a = speeds.get(a)
            sp_b = speeds.get(b)
            found = aspects.find_aspects(
                body_lons[a],
                body_lons[b],
                aspects=aspect_defs,
                orb_deg=8.0,
                speed1_deg_per_day=sp_a,
                speed2_deg_per_day=sp_b,
                orb_resolver=orb_fn,
                body_a=a,
                body_b=b,
            )
            for name, exact, orb, applying in found:
                aspect_list.append({
                    "a": a, "b": b, "type": name,
                    "exact_angle_deg": exact,
                    "orb_degrees": orb,
                    "orb_deg": orb,
                    "applying": applying,
                })
    return {
        "houses": {
            "system": house_system,
            "cusps_deg": cusps_list,
            "angles": {"asc_deg": asc, "mc_deg": mc},
            "status": {"computed": True, "requires": ["date", "time", "latlon"], "confidence": "high", "assumptions": [], "warnings": []},
        },
        "aspects": aspect_list,
        "placements": placements,
    }


def _build_vedic_block(
    jd_ut: float,
    jd_tt: float,
    lat_deg: Optional[float],
    lon_deg: Optional[float],
    height_m: float,
    utc_offset_hours: float,
    ayanamsha_mode: str,
    at_mode: str = "instant",
    sunrise_method: str = "astronomical_upper_limb",
    compute_end_times: bool = True,
) -> dict[str, Any]:
    # Sunrise-based: need location; evaluate at sunrise JD
    if at_mode == "sunrise":
        if lat_deg is None or lon_deg is None:
            return {
                "at_mode": "sunrise",
                "ayanamsha": {"mode": ayanamsha_mode, "nutation_included": None},
                "panchanga": None,
                "sunrise_time_utc": None,
                "sunrise_time_local": None,
                "status": {
                    "computed": False,
                    "requires": ["date", "time", "location"],
                    "confidence": "unavailable",
                    "assumptions": [],
                    "warnings": ["VEDIC_SUNRISE_REQUIRES_LOCATION"],
                },
                "diagnostics": ["VEDIC_SUNRISE_REQUIRES_LOCATION"],
            }
        jd_day = int(jd_ut) + 0.5
        jd_rise_ut, rise_err = vedic.sunrise_jd_ut(jd_day, lon_deg, lat_deg, height_m)
        if jd_rise_ut is None or rise_err:
            return {
                "at_mode": "sunrise",
                "ayanamsha": {"mode": ayanamsha_mode, "nutation_included": None},
                "panchanga": None,
                "sunrise_time_utc": None,
                "sunrise_time_local": None,
                "status": {
                    "computed": False,
                    "requires": ["date", "time", "location"],
                    "confidence": "unavailable",
                    "assumptions": [],
                    "warnings": [rise_err or "sunrise not available"],
                },
                "diagnostics": ["VEDIC_SUNRISE_UNAVAILABLE"],
            }
        jd_eval_ut = jd_rise_ut
        delta_t_sec, _ = ts.delta_t_seconds(jd_rise_ut)
        jd_eval_tt = ts.tt_from_ut(jd_rise_ut, delta_t_sec)
        sunrise_utc_str = vedic.jd_ut_to_iso_utc(jd_rise_ut)
        sunrise_local_str = vedic.jd_ut_to_iso_local(jd_rise_ut, utc_offset_hours)
    else:
        jd_eval_ut = jd_ut
        jd_eval_tt = jd_tt
        sunrise_utc_str = None
        sunrise_local_str = None

    sid_mode = sidereal.AYANAMSHA_MODES.get(ayanamsha_mode, sidereal.SE_SIDM_LAHIRI)
    aya, nut, err_aya = sidereal.ayanamsha_with_nutation(jd_eval_tt, sid_mode)
    xs, _ = astro.calc_planet_geocentric(jd_eval_tt, astro.SE_SUN)
    xm, _ = astro.calc_planet_geocentric(jd_eval_tt, astro.SE_MOON)
    sun_trop = xs[0] if xs else 0.0
    moon_trop = xm[0] if xm else 0.0
    sun_sid = sidereal.tropical_to_sidereal_deg(sun_trop, aya)
    moon_sid = sidereal.tropical_to_sidereal_deg(moon_trop, aya)
    tithi = vedic.tithi_index_from_moon_sun_longitude(moon_trop, sun_trop)
    nakshatra = vedic.nakshatra_index_from_longitude_deg(moon_sid)
    yoga = vedic.yoga_index_from_sun_moon_longitude(sun_sid, moon_sid)
    k1, k2 = vedic.karana_indices_current_tithi(moon_trop, sun_trop)
    vaara_idx = vedic.vaara_from_jd(jd_eval_ut)
    vaara = vedic.vaara_name(vaara_idx)

    tithi_ends_utc = None
    tithi_ends_local = None
    nakshatra_ends_utc = None
    nakshatra_ends_local = None
    yoga_ends_utc = None
    yoga_ends_local = None
    if compute_end_times:
        jd_tithi_end = vedic.tithi_end_jd_ut(jd_eval_ut, tithi)
        if jd_tithi_end is not None:
            tithi_ends_utc = vedic.jd_ut_to_iso_utc(jd_tithi_end)
            tithi_ends_local = vedic.jd_ut_to_iso_local(jd_tithi_end, utc_offset_hours)
        jd_nak_end = vedic.nakshatra_end_jd_ut(jd_eval_ut, nakshatra, aya)
        if jd_nak_end is not None:
            nakshatra_ends_utc = vedic.jd_ut_to_iso_utc(jd_nak_end)
            nakshatra_ends_local = vedic.jd_ut_to_iso_local(jd_nak_end, utc_offset_hours)
        jd_yoga_end = vedic.yoga_end_jd_ut(jd_eval_ut, yoga, aya)
        if jd_yoga_end is not None:
            yoga_ends_utc = vedic.jd_ut_to_iso_utc(jd_yoga_end)
            yoga_ends_local = vedic.jd_ut_to_iso_local(jd_yoga_end, utc_offset_hours)

    return {
        "at_mode": at_mode,
        "ayanamsha": {"mode": ayanamsha_mode, "nutation_included": nut},
        "panchanga": {
            "vaara": vaara,
            "tithi": {
                "index": tithi,
                "ends_at_utc": tithi_ends_utc,
                "ends_at_local": tithi_ends_local,
            },
            "nakshatra": {
                "index": nakshatra,
                "ends_at_utc": nakshatra_ends_utc,
                "ends_at_local": nakshatra_ends_local,
            },
            "yoga": {
                "index": yoga,
                "ends_at_utc": yoga_ends_utc,
                "ends_at_local": yoga_ends_local,
            },
            "karana": {"indices": [k1, k2]},
            "sunrise_method": sunrise_method,
            "status": {
                "computed": True,
                "requires": ["date", "time"] + (["location"] if at_mode == "sunrise" else []),
                "confidence": "high",
                "assumptions": [],
                "warnings": [],
            },
        },
        "sunrise_time_utc": sunrise_utc_str,
        "sunrise_time_local": sunrise_local_str,
        "diagnostics": [],
    }


def _build_chinese_block(
    jd_ut: float,
    jd_tt: float,
    utc_offset_hours: float,
    year_boundary: str = "lichun",
    day_boundary: str = "utc+8_midnight",
    timezone_for_calendar: Optional[str] = None,
    include_solar_terms: bool = False,
    gregorian_year: Optional[int] = None,
) -> dict[str, Any]:
    from datetime import datetime, timezone, timedelta
    diagnostics: list[str] = []
    lon_sun, _ = astro.solar_longitude_geocentric_deg(jd_tt)
    term_idx = chinese.solar_term_longitude_to_index(lon_sun)
    cal_offset = 8.0 if day_boundary == "utc+8_midnight" else utc_offset_hours
    jd_noon_local = int(jd_ut - cal_offset / 24.0) + 0.5
    day_idx, day_stem, day_branch = chinese.day_pillar_jd_noon(jd_ut, day_boundary, utc_offset_hours)
    utc_hour = (jd_ut % 1.0) * 24.0
    hour_local = (utc_hour + cal_offset) % 24.0
    year_idx, year_stem, year_branch = (0, "", "")
    lichun_this = None
    lichun_prev = None
    if year_boundary == "lichun":
        gy = gregorian_year or chinese._jd_ut_to_gregorian_year(jd_ut)
        lichun_this = chinese.lichun_jd_ut_for_year(gy)
        lichun_prev = chinese.lichun_jd_ut_for_year(gy - 1)
        year_idx, year_stem, year_branch = chinese.year_pillar_licheng(jd_ut, cal_offset, lichun_this, lichun_prev)
    else:
        cny_jd = chinese.cny_jd_ut_simplified(gregorian_year or chinese._jd_ut_to_gregorian_year(jd_ut))
        if cny_jd is not None:
            diagnostics.append("CNY_LEAP_RULES_SIMPLIFIED")
            jd_noon_cny = int(cny_jd + 0.5 - 8.0 / 24.0)
            year_idx = chinese.ganzhi_index_from_jd_noon(jd_noon_cny)
            year_stem, year_branch = chinese.stem_branch_from_sexagenary_index(year_idx)
        else:
            year_idx = chinese.ganzhi_index_from_jd_noon(jd_noon_local)
            year_stem, year_branch = chinese.stem_branch_from_sexagenary_index(year_idx)
    month_stem, month_branch = chinese.month_pillar_from_solar_term_and_year_stem(term_idx, year_idx)
    hour_stem, hour_branch = chinese.bazi_pillar_hour_from_day_stem_branch(day_idx, hour_local)
    solar_terms_data = None
    if include_solar_terms and gregorian_year:
        solar_terms_data = {str(t["index"]): t["time_utc"] for t in chinese.compute_solar_terms_for_year(gregorian_year, cal_offset)}
    return {
        "boundary_settings": {"year": year_boundary, "day": day_boundary, "timezone_for_calendar": timezone_for_calendar or "Asia/Shanghai"},
        "boundary_year": year_boundary,
        "solar_terms": solar_terms_data,
        "ganzhi": {"day": {"stem": day_stem, "branch": day_branch, "index_60": day_idx}},
        "bazi_pillars": {
            "year": {"stem": year_stem, "branch": year_branch, "index_60": year_idx},
            "month": {"stem": month_stem, "branch": month_branch},
            "day": {"stem": day_stem, "branch": day_branch, "index_60": day_idx},
            "hour": {"stem": hour_stem, "branch": hour_branch},
        },
        "calendar_day_definition": "utc+8" if day_boundary == "utc+8_midnight" else "local_midnight",
        "diagnostics": diagnostics,
        "status": {"computed": True, "requires": ["date", "time"], "confidence": "medium" if "CNY_LEAP_RULES_SIMPLIFIED" in diagnostics else "high", "assumptions": [], "warnings": diagnostics},
    }


def _resolve_tz(
    timezone_iana: Optional[str],
    utc_offset_hours: Optional[float],
    utc_offset_minutes: Optional[float],
) -> Optional[object]:
    """Resolve timezone: prefer IANA, else explicit offset. Returns tzinfo or None."""
    if timezone_iana:
        try:
            import zoneinfo
            return zoneinfo.ZoneInfo(timezone_iana)
        except Exception:
            pass
    if utc_offset_minutes is not None:
        from datetime import timedelta
        return timezone(timedelta(minutes=utc_offset_minutes))
    if utc_offset_hours is not None:
        from datetime import timedelta
        return timezone(timedelta(hours=utc_offset_hours))
    return None


def compute(
    birth_date: str,
    birth_time_local: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    elevation_m: Optional[float] = None,
    timezone_iana: Optional[str] = None,
    utc_offset_hours: Optional[float] = None,
    utc_offset_minutes: Optional[float] = None,
    house_system: str = DEFAULT_HOUSE_SYSTEM,
    ayanamsha_mode: str = DEFAULT_AYANAMSHA,
    chinese_year_boundary: str = "lichun",
    chinese_day_boundary: str = "utc+8_midnight",
    chinese_timezone_for_calendar: Optional[str] = None,
    chinese_include_solar_terms: bool = False,
    vedic_at: str = "instant",
    vedic_sunrise_method: str = "astronomical_upper_limb",
    western_orb_profile: str = "default",
    western_db_path: Optional[str] = None,
    western_extended_aspects: bool = False,
) -> dict[str, Any]:
    """
    Single entry: compute full horoscoop. Returns dict suitable for JSON (horoscoop.json contract).
    Timezone: prefer timezone_iana, else utc_offset_minutes, else utc_offset_hours.
    If datetime is naive and no timezone provided: time treated as unknown (NO_TIMEZONE), no houses.
    """
    from datetime import timedelta

    diagnostics_codes: list[str] = []
    requires = [models.Requires.DATE]
    time_warnings: list[str] = []
    used_default_time = False
    tz = _resolve_tz(timezone_iana, utc_offset_hours, utc_offset_minutes)

    if not birth_time_local:
        requires.append(models.Requires.TIME)
        birth_time_local = "12:00:00"
        used_default_time = True
        diagnostics_codes.append("NO_BIRTHTIME")
        diagnostics_codes.append("USED_DEFAULT_TIME")

    try:
        dt = datetime.fromisoformat(f"{birth_date}T{birth_time_local}")
    except Exception:
        dt = datetime.fromisoformat(f"{birth_date}T12:00:00")
        used_default_time = True
        if "USED_DEFAULT_TIME" not in diagnostics_codes:
            diagnostics_codes.append("USED_DEFAULT_TIME")

    time_known = True
    if dt.tzinfo is None and tz is None:
        time_known = False
        diagnostics_codes.append("NO_TIMEZONE")
        time_warnings.append("NO_TIMEZONE: naive datetime and no timezone; time unresolved")
        dt = dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo is None and tz is not None:
        dt = dt.replace(tzinfo=tz)

    dt_utc = dt.astimezone(timezone.utc)
    jd_utc = ts.jd_from_datetime(dt_utc, "utc")

    ut1_utc_sec = eop.get_ut1_minus_utc_seconds(dt_utc)
    ut1_utc_source = "eop"
    if ut1_utc_sec is None:
        ut1_utc_sec = 0.0
        ut1_utc_source = "assumed_zero"
        diagnostics_codes.append("EOP_MISSING")
        time_warnings.append("EOP_MISSING: UT1=UTC assumed; confidence estimated")

    jd_ut1 = ts.ut1_from_utc(jd_utc, ut1_utc_sec)
    delta_t_sec, delta_t_source = ts.delta_t_seconds(jd_ut1)
    if delta_t_source == "approximation":
        diagnostics_codes.append("DELTAT_MODEL")

    jd_tt = ts.tt_from_ut(jd_ut1, delta_t_sec)
    datetime_utc_str = dt_utc.isoformat(timespec="seconds").replace("+00:00", "Z")
    datetime_local_str = (dt.astimezone(tz).isoformat(timespec="seconds") if tz is not None and time_known else None)

    confidence = models.Confidence.ESTIMATED
    if time_known and not used_default_time and "EOP_MISSING" not in diagnostics_codes:
        confidence = models.Confidence.HIGH
    elif not time_known:
        confidence = models.Confidence.UNAVAILABLE

    time_block = _build_time_block(
        jd_utc, jd_ut1, jd_tt,
        delta_t_sec, delta_t_source,
        ut1_utc_sec, ut1_utc_source,
        datetime_utc_str, datetime_local_str,
        requires, confidence, time_warnings,
    )

    astronomy_block = _build_astronomy_block(jd_tt, lat, lon, elevation_m or 0.0, BODY_IDS)
    body_lons = {k: v["lon_deg"] for k, v in astronomy_block.items() if isinstance(v, dict) and v.get("lon_deg") is not None}
    body_speeds = {k: v.get("speed_lon_deg_per_day") for k, v in astronomy_block.items() if isinstance(v, dict) and v.get("lon_deg") is not None}
    body_speeds = {k: v for k, v in body_speeds.items() if v is not None}

    from . import db_orbs
    orb_resolver = db_orbs.create_orb_resolver(db_path=western_db_path, orb_profile=western_orb_profile)
    aspect_defs = aspects.EXTENDED_ASPECT_DEFS if western_extended_aspects else aspects.ASPECT_DEFS

    western_block: Optional[dict[str, Any]] = None
    if time_known and lat is not None and lon is not None and body_lons:
        western_block = _build_western_block(
            jd_ut1, lat, lon, house_system, body_lons,
            body_speeds=body_speeds or None,
            aspect_defs=aspect_defs,
            orb_resolver=orb_resolver,
        )

    utc_off = (utc_offset_minutes / 60.0) if utc_offset_minutes is not None else (utc_offset_hours if utc_offset_hours is not None else 8.0)
    vedic_block = _build_vedic_block(
        jd_ut1,
        jd_tt,
        lat,
        lon,
        elevation_m or 0.0,
        utc_off,
        ayanamsha_mode,
        at_mode=vedic_at,
        sunrise_method=vedic_sunrise_method,
        compute_end_times=True,
    )
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td
    epoch = _dt(2000, 1, 1, 12, 0, 0, tzinfo=_tz.utc)
    delta_s = (jd_ut1 - 2451545.0) * 86400.0
    gregorian_year = (epoch + _td(seconds=delta_s)).year
    chinese_block = _build_chinese_block(
        jd_ut1, jd_tt, utc_off,
        year_boundary=chinese_year_boundary,
        day_boundary=chinese_day_boundary,
        timezone_for_calendar=chinese_timezone_for_calendar,
        include_solar_terms=chinese_include_solar_terms,
        gregorian_year=gregorian_year,
    )

    return {
        "meta": {
            "version": SCHEMA_VERSION,
            "generated_at_utc": _iso_utc_now(),
            "engine": {"ephemeris_engine": "Swiss Ephemeris", "house_engine": "SE", "tz_engine": "system", "code_hash": None, "license_mode": None},
        },
        "input": {
            "birth": {
                "date": birth_date,
                "time_local": birth_time_local,
                "place": {"lat": lat, "lon": lon, "elevation_m": elevation_m},
                "timezone": {"iana": timezone_iana, "utc_offset_hours": utc_offset_hours, "utc_offset_minutes": utc_offset_minutes},
            },
        },
        "time": time_block,
        "astronomy": {"bodies": astronomy_block},
        "western": western_block,
        "vedic": vedic_block,
        "chinese": chinese_block,
        "diagnostics": {"codes": diagnostics_codes, "delta_t_source": delta_t_source, "ut1_utc_source": ut1_utc_source},
    }
