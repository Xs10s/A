"""
Layer A – Astronomy: time scales only.
Pure physics: JD, Delta-T, TT/UT1, ERA, GMST, LST.
Source: IERS Conventions TN36 Ch.5; ERFA/SOFA; spec sectie "Tijdschalen en Julian Day".
All angles normalized to [0, 360) deg or [0, 2π) rad as documented.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional, Tuple

# Constants from IERS / IAU
# TT − TAI = 32.184 s (constant)
TT_TAI_SECONDS = 32.184
# JD of 2000-01-01 12:00 TT
JD_J2000 = 2451545.0
# Tu = JD_UT1 − 2451545.0 for ERA
# ERA formula coefficients (IERS TN36 Eq. 5.14)
ERA_COEF_D0 = 0.779_057_273_2640
ERA_COEF_D1 = 1.002_737_811_911_354_48

# IAU 2006 GMST: GMST = ERA + polynomial in t (centuries from J2000.0 UT1)
# IERS TN36 Eq. 5.32: GMST = ERA + 0.014506 + 4612.156534*t + ... (in arcsec, then convert)
# Polynomial coefficients in seconds of time (1 sec time = 15 arcsec)
# GMST(h) = ERA(rad)*240/π/3600 + (polynomial in t) in seconds; then to rad.
# Simplified: GMST = ERA + dERA where dERA is the equation of the equinoxes part.
# IAU 2006: GMST in radians = ERA(UT1) + (0.014506 + 4612.15739966*t + 1.39667721*t^2 + ...)*π/648000
# with t = (JD_UT1 - 2451545.0)/36525.0 (Julian centuries).
GMST_COEF_T0 = 0.014506  # arcsec
GMST_COEF_T1 = 4612.156534
GMST_COEF_T2 = 1.39667721
GMST_COEF_T3 = -0.00009344
GMST_COEF_T4 = 0.00001882
# Arcsec to rad: / 648000 * π = π/648000
ARCSEC_TO_RAD = math.pi / 648000.0


def jd_from_datetime(dt: datetime, scale: str = "utc") -> float:
    """
    Julian Day number (fractional) from datetime.
    Assumes dt is in UTC if tzinfo set; otherwise caller must ensure correct interpretation.
    Scale: 'utc' | 'ut1' | 'tt'. For UTC input we return JD(UTC).
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    epoch = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    delta = dt - epoch
    jd = JD_J2000 + delta.total_seconds() / 86400.0
    return jd


def _delta_t_se(jd_ut1: float) -> Optional[float]:
    """Delta-T from Swiss Ephemeris if available. SE returns days; we return seconds."""
    try:
        import swisseph as swe
        dt_days = swe.deltat(jd_ut1)
        return dt_days * 86400.0
    except Exception:
        return None


def delta_t(jd_ut1: float, source: str = "internal") -> float:
    """
    Delta-T = TT − UT1 in seconds (legacy; use delta_t_seconds for source metadata).
    """
    sec, _ = delta_t_seconds(jd_ut1)
    return sec


def delta_t_seconds(jd_ut1: float) -> Tuple[float, str]:
    """
    Delta-T = TT − UT1 in seconds, plus source label for diagnostics.
    Returns (seconds, source) where source is "swiss_ephemeris" | "approximation" | "internal".
    SE (swe.deltat) is default when available; otherwise fallback approximation, labeled.
    """
    se_val = _delta_t_se(jd_ut1)
    if se_val is not None:
        return (se_val, "swiss_ephemeris")
    t = (jd_ut1 - JD_J2000) / 36525.0
    approx = 64.0 + 0.32 * (jd_ut1 - 2451545.0) / 365.25
    return (approx, "approximation")


def tt_from_ut(jd_ut1: float, delta_t_sec: Optional[float] = None) -> float:
    """
    TT (Terrestrial Time) Julian Day from UT1 Julian Day.
    JD_TT = JD_UT1 + ΔT_seconds / 86400.
    """
    if delta_t_sec is None:
        delta_t_sec, _ = delta_t_seconds(jd_ut1)
    return jd_ut1 + delta_t_sec / 86400.0


def ut1_from_utc(jd_utc: float, ut1_utc_seconds: Optional[float] = None) -> float:
    """
    UT1 Julian Day from UTC Julian Day.
    UT1 = UTC + (UT1−UTC). If ut1_utc_seconds is None, uses 0 (caller should set EOP_MISSING).
    """
    if ut1_utc_seconds is None:
        ut1_utc_seconds = 0.0
    return jd_utc + ut1_utc_seconds / 86400.0


def normalize_angle_rad(rad: float) -> float:
    """Normalize angle to [0, 2π). Unit: rad."""
    r = rad % (2.0 * math.pi)
    if r < 0:
        r += 2.0 * math.pi
    return r


def normalize_angle_deg(deg: float) -> float:
    """Normalize angle to [0, 360). Unit: deg."""
    d = deg % 360.0
    if d < 0:
        d += 360.0
    return d


def era(jd_ut1: float) -> float:
    """
    Earth Rotation Angle (ERA) in radians, [0, 2π).
    ERA(Tu) = 2π(0.7790572732640 + 1.00273781191135448 * Tu) mod 2π
    where Tu = JD_UT1 − 2451545.0.
    Source: IERS Conventions TN36 Eq. 5.14.
    """
    tu = jd_ut1 - JD_J2000
    era_cycles = ERA_COEF_D0 + ERA_COEF_D1 * tu
    return normalize_angle_rad(2.0 * math.pi * (era_cycles % 1.0))


def gmst_rad(jd_ut1: float) -> float:
    """
    Greenwich Mean Sidereal Time in radians, [0, 2π).
    IAU 2006: GMST = ERA(UT1) + polynomial in t (Julian centuries from J2000.0).
    IERS TN36 Eq. 5.32; polynomial in arcseconds converted to radians.
    """
    t = (jd_ut1 - JD_J2000) / 36525.0
    poly_arcsec = (
        GMST_COEF_T0
        + GMST_COEF_T1 * t
        + GMST_COEF_T2 * t * t
        + GMST_COEF_T3 * t * t * t
        + GMST_COEF_T4 * t * t * t * t
    )
    era_rad = era(jd_ut1)
    gmst = era_rad + poly_arcsec * ARCSEC_TO_RAD
    return normalize_angle_rad(gmst)


def gmst_deg(jd_ut1: float) -> float:
    """GMST in degrees [0, 360)."""
    return normalize_angle_deg(math.degrees(gmst_rad(jd_ut1)))


def lst_rad(jd_ut1: float, longitude_deg: float) -> float:
    """
    Local Sidereal Time in radians, [0, 2π).
    LST = GMST + λ_geo (east positive).
    """
    gmst = gmst_rad(jd_ut1)
    lam = math.radians(longitude_deg)
    return normalize_angle_rad(gmst + lam)


def lst_deg(jd_ut1: float, longitude_deg: float) -> float:
    """LST in degrees [0, 360)."""
    return normalize_angle_deg(math.degrees(lst_rad(jd_ut1, longitude_deg)))


def lst_hours(jd_ut1: float, longitude_deg: float) -> float:
    """LST in hours [0, 24). 15 deg = 1 hour."""
    return lst_deg(jd_ut1, longitude_deg) / 15.0
