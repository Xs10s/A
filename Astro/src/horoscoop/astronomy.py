"""
Layer A – Astronomy: coordinates, ephemeris, sunrise/sunset.
Pure physics. SE = Swiss Ephemeris (swe_calc, swe_houses, swe_rise_trans).
Source: Spec "Coördinaten, referentiekaders"; "Efemeriden: JPL DE, SE"; SE API.
"""
from __future__ import annotations

import math
from typing import Any, Optional, Sequence, Tuple

# Obliquity of the ecliptic (mean/true of date): use SE or ERFA in production.
# Formula: x = cos β cos λ, y = cos β sin λ, z = sin β
# Rotate by ε about x: x'=x, y'=y cos ε − z sin ε, z'=y sin ε + z cos ε
# α = atan2(y', x'), δ = arcsin(z')


def ecliptic_to_equatorial_rad(
    lon_rad: float, lat_rad: float, obliquity_rad: float
) -> Tuple[float, float]:
    """
    Ecliptic (λ, β) to equatorial (α, δ). All radians.
    Rotate about x by obliquity ε:
      x = cos β cos λ, y = cos β sin λ, z = sin β
      x' = x, y' = y cos ε − z sin ε, z' = y sin ε + z cos ε
      α = atan2(y', x'), δ = arcsin(z')
    Source: Spec "Ecliptisch ↔ equatoriaal (fundamentele rotatie)".
    """
    x = math.cos(lat_rad) * math.cos(lon_rad)
    y = math.cos(lat_rad) * math.sin(lon_rad)
    z = math.sin(lat_rad)
    yp = y * math.cos(obliquity_rad) - z * math.sin(obliquity_rad)
    zp = y * math.sin(obliquity_rad) + z * math.cos(obliquity_rad)
    alpha = math.atan2(yp, x)
    delta = math.asin(zp)
    return (alpha, delta)


def equatorial_to_ecliptic_rad(
    alpha_rad: float, delta_rad: float, obliquity_rad: float
) -> Tuple[float, float]:
    """
    Equatorial (α, δ) to ecliptic (λ, β). Inverse rotation by −ε.
    x = cos δ cos α, y = cos δ sin α, z = sin δ
    Rotate by −ε: x'=x, y'=y cos ε + z sin ε, z'=−y sin ε + z cos ε
    λ = atan2(y', x'), β = arcsin(z')
    """
    x = math.cos(delta_rad) * math.cos(alpha_rad)
    y = math.cos(delta_rad) * math.sin(alpha_rad)
    z = math.sin(delta_rad)
    yp = y * math.cos(obliquity_rad) + z * math.sin(obliquity_rad)
    zp = -y * math.sin(obliquity_rad) + z * math.cos(obliquity_rad)
    lon = math.atan2(yp, x)
    lat = math.asin(zp)
    return (lon, lat)


def ecliptic_to_equatorial_deg(
    lon_deg: float, lat_deg: float, obliquity_deg: float
) -> Tuple[float, float]:
    """Ecliptic to equatorial; inputs/output in degrees."""
    a, d = ecliptic_to_equatorial_rad(
        math.radians(lon_deg), math.radians(lat_deg), math.radians(obliquity_deg)
    )
    return (math.degrees(a), math.degrees(d))


def equatorial_to_ecliptic_deg(
    alpha_deg: float, delta_deg: float, obliquity_deg: float
) -> Tuple[float, float]:
    """Equatorial to ecliptic; inputs/output in degrees."""
    lon, lat = equatorial_to_ecliptic_rad(
        math.radians(alpha_deg), math.radians(delta_deg), math.radians(obliquity_deg)
    )
    return (math.degrees(lon), math.degrees(lat))


def obliquity_mean_j2000_deg() -> float:
    """Mean obliquity of the ecliptic at J2000.0 (degrees). IAU ~23.43928°."""
    return 23.439_291_11


# -----------------------------------------------------------------------------
# Ephemeris: delegate to Swiss Ephemeris. Layer A only (raw positions).
# -----------------------------------------------------------------------------

# SE planet body codes (sweplanets.h)
SE_SUN = 0
SE_MOON = 1
SE_MERCURY = 2
SE_VENUS = 3
SE_MARS = 4
SE_JUPITER = 5
SE_SATURN = 6
SE_URANUS = 7
SE_NEPTUNE = 8
SE_PLUTO = 9
SE_TRUE_NODE = 10
SE_MEAN_NODE = 11

# Flags: SEFLG_EPHEM, SEFLG_TOPOCTR, SEFLG_SIDEREAL, SEFLG_TRUEPOS, etc.
SEFLG_JPLEPH = 1
SEFLG_SWIEPH = 2
SEFLG_TOPOCTR = 0x00040000
SEFLG_SIDEREAL = 0x00010000
SEFLG_TRUEPOS = 0x00000004
SEFLG_NONUT = 0x00080000


def _swe_calc_available() -> bool:
    try:
        import swisseph  # type: ignore
        return True
    except ImportError:
        return False


def calc_planet_geocentric(
    jd_tt: float,
    body: int,
    flags: int = 0,
) -> Tuple[Sequence[float], Optional[str]]:
    """
    Planet position (geocentric) at JD(TT). Returns (xx, ret_err).
    xx = [longitude, latitude, distance, speed_longitude, speed_latitude, speed_dist] in deg, deg, au, deg/day, etc.
    Use swe_calc(jd_tt, body, flags). Flags: ephemeris, true/apparent, nutation, etc.
    Source: SE API swe_calc() (TT) or swe_calc_ut() (UT + internal Delta-T).
    """
    if not _swe_calc_available():
        return ([], "swisseph not installed")
    import swisseph as swe  # type: ignore
    fl = flags | SEFLG_JPLEPH
    try:
        # TT (ephemeris time): swe.calc(jd_tt, ...); UT: swe.calc_ut(jd_ut, ...)
        xx, ret = swe.calc(jd_tt, body, fl)
        if ret < 0:
            return (list(xx) if xx is not None else [], swe.get_planet_name(body) or "error")
        return (list(xx), None)
    except Exception as e:
        return ([], str(e))


def calc_planet_topocentric(
    jd_tt: float,
    body: int,
    lon_deg: float,
    lat_deg: float,
    height_m: float,
    flags: int = 0,
) -> Tuple[Sequence[float], Optional[str]]:
    """
    Topocentric position: swe_set_topo(lon, lat, height_m) then swe_calc with SEFLG_TOPOCTR.
    Source: Spec "Topocentrisch vs geocentrisch (parallax en observatorlocatie)".
    """
    if not _swe_calc_available():
        return ([], "swisseph not installed")
    import swisseph as swe  # type: ignore
    swe.set_topo(lon_deg, lat_deg, height_m)
    fl = flags | SEFLG_JPLEPH | SEFLG_TOPOCTR
    try:
        xx, ret = swe.calc(jd_tt, body, fl)
        if ret < 0:
            return (list(xx) if xx is not None else [], "error")
        return (list(xx), None)
    except Exception as e:
        return ([], str(e))


def sunrise_sunset_ut(
    jd_ut: float,
    lon_deg: float,
    lat_deg: float,
    height_m: float = 0.0,
    rs_flag: int = 0,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Sunrise and sunset JD(UT). rs_flag: 0 = rise, 1 = set; SE also supports Hindu rising.
    Returns (jd_rise_ut, jd_set_ut, error). Astronomical sunrise = upper limb.
    Source: Spec "Sunrise/sunset (voor Pañcāṅga): swe_rise_trans()".
    """
    if not _swe_calc_available():
        return (None, None, "swisseph not installed")
    import swisseph as swe  # type: ignore
    try:
        # swe_rise_trans(jd_ut, body, "":geographic, lon, lat, height, rs_flag, flags)
        # body SE_SUN; rs_flag SE_CALC_RISE, SE_CALC_SET
        jd_rise, ret_rise = swe.rise_trans(jd_ut, SE_SUN, lon_deg, lat_deg, height_m, swe.CALC_RISE)
        jd_set, ret_set = swe.rise_trans(jd_ut, SE_SUN, lon_deg, lat_deg, height_m, swe.CALC_SET)
        if ret_rise < 0:
            return (None, None, "rise error")
        if ret_set < 0:
            return (jd_rise, None, "set error")
        return (jd_rise, jd_set, None)
    except Exception as e:
        return (None, None, str(e))


def solar_longitude_geocentric_deg(jd_tt: float) -> Tuple[float, Optional[str]]:
    """
    Apparent geocentric ecliptic longitude of the Sun (deg). For solar terms: λ⊙ = k*15°.
    Source: swe_calc Sun; used for Chinese solar terms.
    """
    xx, err = calc_planet_geocentric(jd_tt, SE_SUN)
    if err or not xx:
        return (0.0, err)
    lon = xx[0]  # longitude in degrees
    if lon < 0:
        lon += 360.0
    return (lon % 360.0, None)


def moon_phase_angle_deg(jd_tt: float) -> Tuple[float, Optional[str]]:
    """
    Moon-Sun elongation (phase angle) in degrees. 0 = new, 90 = first quarter, 180 = full.
    Computed from Sun and Moon longitudes.
    """
    xs, err_s = calc_planet_geocentric(jd_tt, SE_SUN)
    xm, err_m = calc_planet_geocentric(jd_tt, SE_MOON)
    if err_s or err_m or not xs or not xm:
        return (0.0, err_s or err_m)
    d = abs(xm[0] - xs[0])
    if d > 180:
        d = 360.0 - d
    return (d, None)
