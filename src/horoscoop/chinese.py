"""
Layer B – Astrology: Chinese systems.
Solar terms (24 節氣): Sun longitude = k×15°; Lìchūn = 315°.
Sexagenary cycle (Ganzhi): stem/branch from JD_noon.
BaZi pillars: year (Lìchūn or CNY boundary), month (jieqi), day, hour (double hours).
Source: Spec "Chinese systemen"; YT Liu.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Optional, Sequence, Tuple

from . import astronomy as astro
from . import time_scales as ts

# Lìchūn = 315° (J1)
LICHUN_LONGITUDE_DEG = 315.0
DONGZHI_LONGITUDE_DEG = 270.0  # Winter solstice
SOLAR_TERM_STEP_DEG = 15.0
SOLAR_TERM_TOLERANCE_DAY = 1.0 / 86400.0  # ~1 second

STEMS = ["Jiǎ", "Yǐ", "Bǐng", "Dīng", "Wù", "Jǐ", "Gēng", "Xīn", "Rén", "Guǐ"]
BRANCHES = ["Zǐ", "Chǒu", "Yín", "Mǎo", "Chén", "Sì", "Wǔ", "Wèi", "Shēn", "Yǒu", "Xū", "Hài"]

SOLAR_TERM_NAMES: dict[int, str] = {
    1: "Lìchūn", 2: "Yǔshuǐ", 3: "Jīngzhé", 4: "Chūnfēn", 5: "Qīngmíng", 6: "Gǔyǔ",
    7: "Lìxià", 8: "Xiǎomǎn", 9: "Mángzhòng", 10: "Xiàzhì", 11: "Xiǎoshǔ", 12: "Dàshǔ",
    13: "Lìqiū", 14: "Chǔshǔ", 15: "Báilù", 16: "Qiūfēn", 17: "Hánlù", 18: "Shuāngjiàng",
    19: "Lìdōng", 20: "Xiǎoxuě", 21: "Dàxuě", 22: "Dōngzhì", 23: "Xiǎohán", 24: "Dàhán",
}


def solar_term_longitude_to_index(lon_deg: float) -> int:
    """Solar term index 1–24 from Sun longitude. J1 = 315°."""
    lon = lon_deg % 360.0
    k = round((lon - LICHUN_LONGITUDE_DEG) / SOLAR_TERM_STEP_DEG) % 24
    return 1 + k


def _sun_longitude_at_jd_ut(jd_ut: float) -> Optional[float]:
    """Apparent geocentric solar longitude at JD(UT). Ephemeris in TT."""
    dt_sec, _ = ts.delta_t_seconds(jd_ut)
    jd_tt = ts.tt_from_ut(jd_ut, dt_sec)
    lon, err = astro.solar_longitude_geocentric_deg(jd_tt)
    return None if err else lon


def _normalize_lon_diff(lon: float, target: float) -> float:
    """Difference in longitude for root-finding; handles wrap."""
    d = (lon - target) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def solar_term_time_utc(
    jd_start: float,
    target_longitude_deg: float,
    tolerance_days: float = SOLAR_TERM_TOLERANCE_DAY,
    max_bisect: int = 50,
) -> Optional[float]:
    """
    Find JD(UT) when apparent geocentric solar longitude equals target_longitude_deg.
    Sun longitude evaluated in TT; returns JD in UT. Bracket search + bisection.
    """
    dt_sec, _ = ts.delta_t_seconds(jd_start)
    jd_tt0 = ts.tt_from_ut(jd_start, dt_sec)
    lon0, err = astro.solar_longitude_geocentric_deg(jd_tt0)
    if err:
        return None
    diff0 = _normalize_lon_diff(lon0, target_longitude_deg)
    step = 0.5 if diff0 < 0 else -0.5
    jd_lo, jd_hi = jd_start, jd_start + step
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(30):
        dt_hi, _ = ts.delta_t_seconds(jd_hi)
        lon_hi, e = astro.solar_longitude_geocentric_deg(ts.tt_from_ut(jd_hi, dt_hi))
        if e:
            return None
        d_hi = _normalize_lon_diff(lon_hi, target_longitude_deg)
        if diff0 * d_hi <= 0:
            break
        jd_lo, jd_hi = jd_hi, jd_hi + step
    else:
        return None
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(max_bisect):
        jd_mid = (jd_lo + jd_hi) / 2.0
        if jd_hi - jd_lo < tolerance_days:
            return jd_mid
        dt_mid, _ = ts.delta_t_seconds(jd_mid)
        lon_mid, e = astro.solar_longitude_geocentric_deg(ts.tt_from_ut(jd_mid, dt_mid))
        if e:
            return None
        d_mid = _normalize_lon_diff(lon_mid, target_longitude_deg)
        if d_mid <= 0:
            jd_lo = jd_mid
        else:
            jd_hi = jd_mid
    return (jd_lo + jd_hi) / 2.0


def jd_ut_to_iso_utc(jd_ut: float) -> str:
    """Convert JD(UT) to ISO-8601 UTC string."""
    from datetime import datetime, timezone, timedelta
    day = int(jd_ut)
    frac = jd_ut - day
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta_d = day - 2451545
    delta_s = (delta_d + frac) * 86400.0
    dt = epoch + timedelta(seconds=delta_s)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def compute_solar_terms_for_year(
    year: int,
    utc_offset_hours: float = 8.0,
) -> list[dict[str, Any]]:
    """
    Compute all 24 solar terms for a Gregorian year. Returns list of dicts with
    index, name, longitude_deg, time_utc (ISO), time_local (ISO if offset provided).
    """
    # Approximate JD for start of year (Jan 1 00:00 UTC) and end (Dec 31)
    jd_jan1 = 2451545.0 + (datetime(year, 1, 1, tzinfo=timezone.utc) - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).total_seconds() / 86400.0
    terms = []
    for i in range(1, 25):
        target = (LICHUN_LONGITUDE_DEG + (i - 1) * SOLAR_TERM_STEP_DEG) % 360.0
        jd_start = jd_jan1 + (i - 1) * 15.0
        jd_ut = solar_term_time_utc(jd_start, target)
        if jd_ut is None:
            terms.append({"index": i, "name": SOLAR_TERM_NAMES.get(i, ""), "longitude_deg": target, "time_utc": None, "time_local": None})
        else:
            time_utc = jd_ut_to_iso_utc(jd_ut)
            from datetime import datetime, timezone, timedelta
            day = int(jd_ut)
            frac = jd_ut - day
            epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            delta_s = (day - 2451545 + frac) * 86400.0
            dt_utc = epoch + timedelta(seconds=delta_s)
            dt_local = dt_utc.replace(tzinfo=timezone.utc) + timedelta(hours=utc_offset_hours)
            time_local = dt_local.strftime("%Y-%m-%dT%H:%M:%S")
            terms.append({"index": i, "name": SOLAR_TERM_NAMES.get(i, ""), "longitude_deg": target, "time_utc": time_utc, "time_local": time_local})
    return terms


def lichun_jd_ut_for_year(year: int) -> Optional[float]:
    """JD(UT) of Lìchūn (315°) for the given Gregorian year (the one that falls in that calendar year)."""
    jd_jan1 = 2451545.0 + (datetime(year, 1, 1, tzinfo=timezone.utc) - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).total_seconds() / 86400.0
    return solar_term_time_utc(jd_jan1 - 30, LICHUN_LONGITUDE_DEG)


def ganzhi_index_from_jd_noon(jd_noon: float) -> int:
    """Sexagenary index 1–60 from JD at local noon. S = 1 + mod(JD_noon − 11, 60)."""
    return 1 + int((jd_noon - 11) % 60)


def stem_branch_from_sexagenary_index(index_60: int) -> Tuple[str, str]:
    """(stem_name, branch_name) from index 1–60."""
    s = (index_60 - 1) % 60
    return (STEMS[s % 10], BRANCHES[s % 12])


def stem_branch_from_jd_noon(jd_noon: float) -> Tuple[int, str, str]:
    """(index_60, stem, branch) for day at local noon."""
    idx = ganzhi_index_from_jd_noon(jd_noon)
    stem, branch = stem_branch_from_sexagenary_index(idx)
    return (idx, stem, branch)


def hour_branch_from_local_hour(local_hour: float) -> int:
    """
    Double hours: Zi 23:00–01:00 = 0, Chou 01:00–03:00 = 1, ...
    local_hour in [0, 24).
    """
    h = local_hour % 24.0
    return int((h + 1) / 2) % 12


def hour_branch_from_utc_hour(utc_hour: float, utc_offset_hours: float = 8.0) -> int:
    """Branch index from UTC hour and offset."""
    local = (utc_hour + utc_offset_hours) % 24.0
    return hour_branch_from_local_hour(local)


def bazi_pillar_hour_from_day_stem_branch(
    day_index_60: int,
    local_hour: float,
) -> Tuple[str, str]:
    """
    Hour pillar (stem, branch) from day pillar and local civil hour.
    Standard: 甲己日 甲子時 (Jia day → Jia Zi hour). Day stem 0,5 → Zi branch gets stem 0.
    """
    hb = hour_branch_from_local_hour(local_hour)
    day_s = (day_index_60 - 1) % 10
    # Standard BaZi: stem for Zi hour = (day_stem % 5) * 2
    start_stem = (day_s % 5) * 2
    hour_stem = (start_stem + hb) % 10
    return (STEMS[hour_stem], BRANCHES[hb])


def bazi_pillar_hour(
    year_stem: int, year_branch: int,
    day_index_60: int,
    local_hour: float,
) -> Tuple[str, str]:
    """Hour pillar from day index and local hour (0–24)."""
    return bazi_pillar_hour_from_day_stem_branch(day_index_60, local_hour)


def _jd_ut_to_gregorian_year(jd_ut: float) -> int:
    """Approximate Gregorian year at JD(UT)."""
    from datetime import datetime, timezone, timedelta
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta_s = (jd_ut - 2451545.0) * 86400.0
    dt = epoch + timedelta(seconds=delta_s)
    return dt.year


def _jd_ut_to_local_ymd(jd_ut: float, utc_offset_hours: float) -> Tuple[int, int, int]:
    """Gregorian (year, month, day) in civil time for the given offset from UTC."""
    from datetime import datetime, timezone, timedelta
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta_s = (jd_ut - 2451545.0) * 86400.0
    dt_utc = epoch + timedelta(seconds=delta_s)
    dt_local = dt_utc + timedelta(hours=utc_offset_hours)
    return (dt_local.year, dt_local.month, dt_local.day)


def sexagenary_year_pillar_from_chinese_year(chinese_year: int) -> Tuple[int, str, str]:
    """
    Stem-branch of the Chinese solar year (Lìchūn to Lìchūn), not the day pillar of any date.
    chinese_year is the Gregorian calendar year in which that year's Lìchūn falls (standard labeling).
    Stem/branch: (year - 4) mod 10 / mod 12 with 1984 → 甲子.
    """
    s = (chinese_year - 4) % 10
    b = (chinese_year - 4) % 12
    stem = STEMS[s]
    branch = BRANCHES[b]
    for idx in range(1, 61):
        if (idx - 1) % 10 == s and (idx - 1) % 12 == b:
            return (idx, stem, branch)
    raise RuntimeError("sexagenary year pillar: unreachable")


def _chinese_solar_year_gregorian_fallback(jd_ut: float, utc_offset_hours: float) -> int:
    """
    When Lìchūn JD is unavailable (no ephemeris), approximate the Chinese year using
    local calendar date: Lìchūn is usually Feb 3–5; Feb 4 cut-off matches common tables for most years.
    """
    y, m, d = _jd_ut_to_local_ymd(jd_ut, utc_offset_hours)
    if (m, d) < (2, 4):
        return y - 1
    return y


def year_pillar_licheng(
    jd_ut: float,
    utc_offset_hours: float,
    lichun_this_year_jd: Optional[float],
    lichun_prev_year_jd: Optional[float],
) -> Tuple[int, str, str]:
    """
    Year pillar by Lìchūn: stem and branch of the sexagenary year (年柱), not the day pillar
    of the Lìchūn day (which would often show e.g. Yín / Tiger while the year is Chén / Dragon).
    """
    _ = lichun_prev_year_jd  # Kept for API compatibility with engine callers.
    gy = _jd_ut_to_gregorian_year(jd_ut)
    if lichun_this_year_jd is not None:
        chinese_year = gy if jd_ut >= lichun_this_year_jd else gy - 1
    else:
        chinese_year = _chinese_solar_year_gregorian_fallback(jd_ut, utc_offset_hours)
    return sexagenary_year_pillar_from_chinese_year(chinese_year)


def month_pillar_from_solar_term_and_year_stem(
    solar_term_index: int,
    year_stem_index: int,
) -> Tuple[str, str]:
    """
    Month pillar: 12 months by major solar terms. Branch = (solar_term_index - 1) // 2 (major terms 1,3,5...).
    Stem from year stem: 甲年 丙寅月 (Jia year → Bing Yin month). Standard: month_stem = (year_stem + 2 + month_branch*2) % 10.
    """
    month_branch = ((solar_term_index - 1) // 2) % 12
    year_s = (year_stem_index - 1) % 10
    month_stem = (year_s + 2 + month_branch * 2) % 10
    return (STEMS[month_stem], BRANCHES[month_branch])


def month_pillar_from_solar_term(jd_noon_ut: float, solar_term_index: int) -> Tuple[str, str]:
    """Legacy: month pillar without year stem; use placeholder year stem."""
    month_branch = (solar_term_index - 1) % 12
    month_stem = (2 + month_branch * 2) % 10
    return (STEMS[month_stem], BRANCHES[month_branch])


def day_pillar_jd_noon(
    jd_ut: float,
    day_boundary: str,
    utc_offset_hours: float,
) -> Tuple[int, str, str]:
    """
    Day pillar from JD(UT). day_boundary: "local_midnight" | "utc+8_midnight".
    Local midnight: civil day starts at 00:00 in the given offset.
    UTC+8 midnight: civil day starts at 16:00 previous UTC day (00:00 UTC+8).
    Returns (index_60, stem, branch) for the civil day.
    """
    if day_boundary == "utc+8_midnight":
        offset = 8.0
        jd_local_noon = int(jd_ut - offset / 24.0) + 0.5
    else:
        offset = utc_offset_hours
        jd_local_noon = int(jd_ut - offset / 24.0) + 0.5
    return stem_branch_from_jd_noon(jd_local_noon)


def find_new_moon_jd_ut(jd_start: float) -> Optional[float]:
    """Find JD(UT) of new moon (Moon-Sun longitude = 0 mod 360) near jd_start. Bisection."""
    dt_sec, _ = ts.delta_t_seconds(jd_start)
    jd_tt = ts.tt_from_ut(jd_start, dt_sec)
    xs, e1 = astro.calc_planet_geocentric(jd_tt, astro.SE_SUN)
    xm, e2 = astro.calc_planet_geocentric(jd_tt, astro.SE_MOON)
    if e1 or e2 or not xs or not xm:
        return None
    diff0 = (xm[0] - xs[0]) % 360.0
    if diff0 > 180.0:
        diff0 -= 360.0
    step = 0.5 if diff0 < 0 else -0.5
    jd_lo, jd_hi = jd_start, jd_start + step
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(30):
        dt_hi, _ = ts.delta_t_seconds(jd_hi)
        jd_tt_hi = ts.tt_from_ut(jd_hi, dt_hi)
        xs_hi, _ = astro.calc_planet_geocentric(jd_tt_hi, astro.SE_SUN)
        xm_hi, _ = astro.calc_planet_geocentric(jd_tt_hi, astro.SE_MOON)
        if not xs_hi or not xm_hi:
            return None
        d_hi = (xm_hi[0] - xs_hi[0]) % 360.0
        if d_hi > 180.0:
            d_hi -= 360.0
        if diff0 * d_hi <= 0:
            break
        jd_lo, jd_hi = jd_hi, jd_hi + step
    else:
        return None
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(50):
        jd_mid = (jd_lo + jd_hi) / 2.0
        if jd_hi - jd_lo < 1e-6:
            return jd_mid
        dt_mid, _ = ts.delta_t_seconds(jd_mid)
        jd_tt_m = ts.tt_from_ut(jd_mid, dt_mid)
        xs_m, _ = astro.calc_planet_geocentric(jd_tt_m, astro.SE_SUN)
        xm_m, _ = astro.calc_planet_geocentric(jd_tt_m, astro.SE_MOON)
        if not xs_m or not xm_m:
            return None
        d_m = (xm_m[0] - xs_m[0]) % 360.0
        if d_m > 180.0:
            d_m -= 360.0
        if d_m <= 0:
            jd_lo = jd_mid
        else:
            jd_hi = jd_mid
    return (jd_lo + jd_hi) / 2.0


def dongzhi_jd_ut_for_year(year: int) -> Optional[float]:
    """Winter solstice (270°) for Gregorian year."""
    jd_jan1 = 2451545.0 + (datetime(year, 1, 1, tzinfo=timezone.utc) - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).total_seconds() / 86400.0
    return solar_term_time_utc(jd_jan1 + 350, DONGZHI_LONGITUDE_DEG)


def cny_jd_ut_simplified(year: int) -> Optional[float]:
    """
    Chinese New Year (simplified): second new moon after winter solstice of previous Gregorian year.
    Confidence medium; diagnostics: CNY_LEAP_RULES_SIMPLIFIED.
    """
    dongzhi_prev = dongzhi_jd_ut_for_year(year - 1)
    if dongzhi_prev is None:
        return None
    nm1 = find_new_moon_jd_ut(dongzhi_prev + 1)
    if nm1 is None:
        return None
    nm2 = find_new_moon_jd_ut(nm1 + 25)
    return nm2


def cny_date_simplified(year: int) -> Optional[str]:
    """CNY date as YYYY-MM-DD in UTC+8 for the given Gregorian year (the CNY that falls in that year)."""
    jd = cny_jd_ut_simplified(year)
    if jd is None:
        return None
    return jd_ut_to_iso_utc(jd)[:10]
