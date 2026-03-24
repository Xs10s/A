"""
Layer B – Astrology: Vedic / Pañcāṅga.
Tithi (12° steps, 1–30), nakṣatra (27 × 13°20′), yoga (27, Sun+Moon nirayana), karaṇa (60, 6°).
Sunrise-based day; tithi at sunrise requires sunrise time. SE swe_rise_trans for sunrise.
Source: Spec "Vedische Pañcāṅga"; VedicDateTime (tithi=12°, nakṣatra=13°20′, yoga sum, karaṇa=6°).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence, Tuple

# 13°20' = 13 + 20/60
NAKSHATRA_WIDTH_DEG = 13.0 + 20.0 / 60.0
TITHI_WIDTH_DEG = 12.0
KARANA_WIDTH_DEG = 6.0
YOGA_WIDTH_DEG = NAKSHATRA_WIDTH_DEG


def tithi_index_from_moon_sun_longitude(moon_lon_deg: float, sun_lon_deg: float) -> int:
    """
    Tithi index 1–30 from (ecliptical) Moon and Sun longitudes.
    Tithi = 1 + floor((λ_Moon − λ_Sun) / 12°) mod 30.
    Source: Spec "Tithi: voltooid wanneer Maan 12° in (ecliptische) lengte relatief aan de Zon aflegt".
    """
    diff = (moon_lon_deg - sun_lon_deg) % 360.0
    idx = 1 + int(diff / TITHI_WIDTH_DEG) % 30
    return idx


def nakshatra_index_from_longitude_deg(lon_nirayana_deg: float) -> int:
    """
    Nakṣatra index 1–27 from sidereal (nirayana) longitude.
    27 segments of 13°20′; segment i covers [ (i-1)*13°20′, i*13°20′ ).
    Source: Spec "Nakṣatra: 27 segmenten van 13°20′; (sidereale/nirayana) maanslengte".
    """
    lon = lon_nirayana_deg % 360.0
    idx = 1 + int(lon / NAKSHATRA_WIDTH_DEG) % 27
    return idx


def yoga_index_from_sun_moon_longitude(sun_nirayana_deg: float, moon_nirayana_deg: float) -> int:
    """
    Yoga index 1–27 from sum of nirayana longitudes of Sun and Moon.
    Sum = (λ_Sun + λ_Moon) mod 360; 27 segments of 13°20′.
    Source: Spec "Yoga: 27 segmenten van 13°20′; gebaseerd op som van nirayana lengtes van Zon en Maan".
    """
    total = (sun_nirayana_deg + moon_nirayana_deg) % 360.0
    idx = 1 + int(total / YOGA_WIDTH_DEG) % 27
    return idx


def karana_index_from_moon_sun_longitude(moon_lon_deg: float, sun_lon_deg: float) -> int:
    """
    Karaṇa index: half-tithi, 6° steps. 60 per synodic month.
    karana = 1 + floor((λ_Moon − λ_Sun) / 6°) mod 60.
    Source: Spec "Karaṇa: half‑tithi; 6° relatieve lengte (60 karaṇa per synodische maand)".
    """
    diff = (moon_lon_deg - sun_lon_deg) % 360.0
    idx = 1 + int(diff / KARANA_WIDTH_DEG) % 60
    return idx


def karana_indices_current_tithi(moon_lon_deg: float, sun_lon_deg: float) -> Tuple[int, int]:
    """
    Current tithi spans two karanas (odd tithi: first half, even: second half).
    Returns (karana_1, karana_2) for the current tithi (1-based).
    """
    k = karana_index_from_moon_sun_longitude(moon_lon_deg, sun_lon_deg)
    # In 60-karana scheme, each tithi has 2 karanas; k gives current half.
    k1 = ((k - 1) // 2) * 2 + 1
    k2 = k1 + 1
    if k2 > 60:
        k2 = 1
    return (k1, k2)


def vaara_from_jd(jd_ut: float) -> int:
    """
    Weekday 0–6 (0 = Sunday) from JD. JD 0 was Monday; (JD+1) mod 7 = 0 for Sunday.
    vaara: 0=Sunday, 1=Monday, ...
    """
    return int((jd_ut + 1) % 7)


def vaara_name(vaara_index: int) -> str:
    """Weekday name for index 0–6."""
    names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return names[vaara_index % 7]


# Sunrise: delegate to astronomy.sunrise_sunset_ut; method = astronomical_upper_limb or hindu_rising
def sunrise_jd_ut(
    jd_ut: float,
    lon_deg: float,
    lat_deg: float,
    height_m: float = 0.0,
) -> Tuple[Optional[float], Optional[str]]:
    """
    Sunrise JD(UT) for given date and location. Astronomical = upper limb.
    For "tithi at sunrise" and tithi end time (inverse interpolation around sunrise).
    """
    try:
        from . import astronomy as astro
        jd_rise, _, err = astro.sunrise_sunset_ut(jd_ut, lon_deg, lat_deg, height_m)
        return (jd_rise, err)
    except Exception as e:
        return (None, str(e))


def _moon_sun_diff_at_jd_ut(jd_ut: float) -> Optional[float]:
    """(Moon - Sun) longitude in degrees at JD(UT). Ephemeris in TT."""
    from . import astronomy as astro
    from . import time_scales as ts
    dt_sec, _ = ts.delta_t_seconds(jd_ut)
    jd_tt = ts.tt_from_ut(jd_ut, dt_sec)
    xs, e1 = astro.calc_planet_geocentric(jd_tt, astro.SE_SUN)
    xm, e2 = astro.calc_planet_geocentric(jd_tt, astro.SE_MOON)
    if e1 or e2 or not xs or not xm:
        return None
    return (xm[0] - xs[0]) % 360.0


def _moon_sidereal_at_jd_ut(jd_ut: float, ayanamsha_deg: float) -> Optional[float]:
    """Moon sidereal longitude at JD(UT)."""
    from . import astronomy as astro
    from . import time_scales as ts
    from . import sidereal
    dt_sec, _ = ts.delta_t_seconds(jd_ut)
    jd_tt = ts.tt_from_ut(jd_ut, dt_sec)
    xm, err = astro.calc_planet_geocentric(jd_tt, astro.SE_MOON)
    if err or not xm:
        return None
    return sidereal.tropical_to_sidereal_deg(xm[0], ayanamsha_deg)


def _sun_moon_sum_sidereal_at_jd_ut(jd_ut: float, ayanamsha_deg: float) -> Optional[float]:
    """Sun + Moon sidereal longitude at JD(UT)."""
    from . import astronomy as astro
    from . import time_scales as ts
    from . import sidereal
    dt_sec, _ = ts.delta_t_seconds(jd_ut)
    jd_tt = ts.tt_from_ut(jd_ut, dt_sec)
    xs, e1 = astro.calc_planet_geocentric(jd_tt, astro.SE_SUN)
    xm, e2 = astro.calc_planet_geocentric(jd_tt, astro.SE_MOON)
    if e1 or e2 or not xs or not xm:
        return None
    s_sid = sidereal.tropical_to_sidereal_deg(xs[0], ayanamsha_deg)
    m_sid = sidereal.tropical_to_sidereal_deg(xm[0], ayanamsha_deg)
    return (s_sid + m_sid) % 360.0


def _find_root_jd_ut(
    jd_start: float,
    target_value: float,
    eval_fn: Callable[[float], Optional[float]],
    step_days: float = 0.1,
    tolerance_days: float = 1e-6,
    max_bisect: int = 50,
    forward_only: bool = False,
) -> Optional[float]:
    """Bracket then bisect: find jd_ut where eval_fn(jd_ut) crosses target_value (mod 360).
    If forward_only=True, only search jd >= jd_start (for end-times).
    """
    v0 = eval_fn(jd_start)
    if v0 is None:
        return None
    d0 = (v0 - target_value) % 360.0
    if d0 > 180.0:
        d0 -= 360.0
    if forward_only:
        step = abs(step_days)
    else:
        step = step_days if d0 < 0 else -step_days
    jd_lo, jd_hi = jd_start, jd_start + step
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(60):
        v_hi = eval_fn(jd_hi)
        if v_hi is None:
            return None
        d_hi = (v_hi - target_value) % 360.0
        if d_hi > 180.0:
            d_hi -= 360.0
        if d0 * d_hi <= 0:
            break
        jd_lo, jd_hi = jd_hi, jd_hi + step
    else:
        return None
    if jd_lo > jd_hi:
        jd_lo, jd_hi = jd_hi, jd_lo
    for _ in range(max_bisect):
        if jd_hi - jd_lo < tolerance_days:
            return (jd_lo + jd_hi) / 2.0
        jd_mid = (jd_lo + jd_hi) / 2.0
        v_m = eval_fn(jd_mid)
        if v_m is None:
            return None
        d_m = (v_m - target_value) % 360.0
        if d_m > 180.0:
            d_m -= 360.0
        if d_m <= 0:
            jd_lo = jd_mid
        else:
            jd_hi = jd_mid
    return (jd_lo + jd_hi) / 2.0


def tithi_end_jd_ut(
    jd_eval_ut: float,
    current_tithi: int,
    tolerance_days: float = 1.0 / 86400.0,
) -> Optional[float]:
    """
    JD(UT) when current tithi ends (next 12° boundary). Target = current_tithi * 12° (next boundary).
    """
    target_deg = (current_tithi * TITHI_WIDTH_DEG) % 360.0
    if current_tithi >= 30:
        target_deg = 0.0
    return _find_root_jd_ut(
        jd_eval_ut, target_deg, _moon_sun_diff_at_jd_ut,
        step_days=0.1, tolerance_days=tolerance_days, forward_only=True,
    )


def nakshatra_end_jd_ut(
    jd_eval_ut: float,
    current_nakshatra: int,
    ayanamsha_deg: float,
    tolerance_days: float = 1.0 / 86400.0,
) -> Optional[float]:
    """JD(UT) when current nakshatra ends (next 13°20' boundary)."""
    target_deg = (current_nakshatra * NAKSHATRA_WIDTH_DEG) % 360.0
    def eval_fn(jd: float) -> Optional[float]:
        return _moon_sidereal_at_jd_ut(jd, ayanamsha_deg)
    return _find_root_jd_ut(
        jd_eval_ut, target_deg, eval_fn,
        step_days=0.1, tolerance_days=tolerance_days, forward_only=True,
    )


def yoga_end_jd_ut(
    jd_eval_ut: float,
    current_yoga: int,
    ayanamsha_deg: float,
    tolerance_days: float = 1.0 / 86400.0,
) -> Optional[float]:
    """JD(UT) when current yoga ends (next 13°20' boundary of Sun+Moon sum)."""
    target_deg = (current_yoga * YOGA_WIDTH_DEG) % 360.0
    def eval_fn(jd: float) -> Optional[float]:
        return _sun_moon_sum_sidereal_at_jd_ut(jd, ayanamsha_deg)
    return _find_root_jd_ut(
        jd_eval_ut, target_deg, eval_fn,
        step_days=0.1, tolerance_days=tolerance_days, forward_only=True,
    )


def jd_ut_to_iso_utc(jd_ut: float) -> str:
    """JD(UT) to ISO-8601 UTC."""
    from datetime import datetime, timezone, timedelta
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta_s = (jd_ut - 2451545.0) * 86400.0
    dt = epoch + timedelta(seconds=delta_s)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def jd_ut_to_iso_local(jd_ut: float, utc_offset_hours: float) -> str:
    """JD(UT) to ISO-8601 local time with given UTC offset (e.g. 5.5 for IST)."""
    from datetime import datetime, timezone, timedelta
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    utc_dt = epoch + timedelta(seconds=(jd_ut - 2451545.0) * 86400.0)
    tz = timezone(timedelta(hours=utc_offset_hours))
    return utc_dt.astimezone(tz).isoformat(timespec="seconds")


def tithi_end_time_local(
    jd_sunrise_ut: float,
    moon_lon_at_rise: float,
    sun_lon_at_rise: float,
    sample_interval_days: float = 1.0 / 24.0,
    interpolate: str = "linear",
) -> Optional[float]:
    """
    Tithi end JD(UT) via root-finding. Uses current tithi at rise and finds next 12° boundary.
    """
    tithi = tithi_index_from_moon_sun_longitude(moon_lon_at_rise, sun_lon_at_rise)
    return tithi_end_jd_ut(jd_sunrise_ut, tithi)
