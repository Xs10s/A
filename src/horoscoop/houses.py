"""
Layer B – Astrology: house systems (deterministic formulas / SE API).
Definitions per SE documentation: Placidus, Koch, Regiomontanus, Campanus,
Equal, Whole Sign, Porphyry, Srīpati.
Source: Spec "Huizenalgoritmes (definities + implementatie)"; SE houses.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

from . import time_scales as ts
from . import astronomy as astro

# SE house system codes (sweph.h)
# 'P' Placidus, 'K' Koch, 'O' Porphyry, 'R' Regiomontanus, 'C' Campanus,
# 'E' Equal, 'V' equal from ASC (Vehlow), 'W' Whole Sign, 'X' Meridian, 'B' Alcabitus,
# 'A' equal from MC (Armitage), 'M' Morinus; Sripati often 'S' or custom
SE_PLACIDUS = b"P"
SE_KOCH = b"K"
SE_REGIO = b"R"
SE_CAMPANUS = b"C"
SE_EQUAL = b"E"
SE_VEHLOW = b"V"
SE_WHOLE_SIGN = b"W"
SE_PORPHYRY = b"O"
# Sripati: SE may use different code; spec "Srīpati: start met Porphyry, dan cusp‑midpoints"
SE_SRIPATI = b"S"  # if supported; else compute from Porphyry midpoints

HOUSE_SYSTEM_CODES: dict[str, bytes] = {
    "P": SE_PLACIDUS,
    "K": SE_KOCH,
    "R": SE_REGIO,
    "C": SE_CAMPANUS,
    "E": SE_EQUAL,
    "W": SE_WHOLE_SIGN,
    "O": SE_PORPHYRY,
    "S": SE_SRIPATI,
}


def _swe_houses_available() -> bool:
    try:
        import swisseph  # type: ignore
        return True
    except ImportError:
        return False


def calc_houses_se(
    jd_ut: float,
    lat_deg: float,
    lon_deg: float,
    hsys: bytes,
) -> Tuple[Optional[Sequence[float]], Optional[Sequence[float]], Optional[str]]:
    """
    Houses via SE: swe_houses(jd_ut, lat, lon, hsys).
    Returns (cusps_deg[13], ascmc_deg[], error). cusps[0] unused; cusps[1..12] = cusps 1-12.
    ascmc: ASC, MC, ARMC, Vertex, Equatorial Ascendant, etc. (SE order).
    Source: SE API swe_houses(); spec house system definitions.
    """
    if not _swe_houses_available():
        return (None, None, "swisseph not installed")
    import swisseph as swe  # type: ignore
    try:
        cusps, ascmc = swe.houses(jd_ut, lat_deg, lon_deg, hsys)
        cusps_list = list(cusps) if cusps is not None else []
        ascmc_list = list(ascmc) if ascmc is not None else []
        return (cusps_list, ascmc_list, None)
    except Exception as e:
        return (None, None, str(e))


def houses_placidus(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Placidus: cusps via divisions of semidiurnal/seminocturnal arcs.
    11th cusp = 2/3 of semidiurnal arc, 12th = 1/3; 2nd = 2/3 of seminocturnal, 3rd = 1/3.
    Implementation: SE swe_houses(..., 'P').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_PLACIDUS)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_koch(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Koch/GOH: cusps as horizon lines at different times; 11/12 via time for MC degree from horizon to culmination, divided in thirds.
    Implementation: SE swe_houses(..., 'K').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_KOCH)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_regiomontanus(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Regiomontanus: equator divided in 12 equal parts; great circles through these divisions and N/S horizon; intersections with ecliptic = cusps.
    Implementation: SE swe_houses(..., 'R').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_REGIO)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_campanus(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Campanus: prime vertical divided in 12 parts; great circles through divisions and N/S horizon; intersections with ecliptic = cusps.
    Implementation: SE swe_houses(..., 'C').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_CAMPANUS)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_equal(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Equal: 30° segments from ASC or MC+90°. SE 'E' = equal from ASC.
    Implementation: SE swe_houses(..., 'E').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_EQUAL)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_whole_sign(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Whole Sign: 1st house starts at beginning of sign containing ASC; 30° per house.
    Implementation: SE swe_houses(..., 'W').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_WHOLE_SIGN)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_porphyry(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Porphyry: each quadrant divided into three equal parts on the ecliptic.
    Implementation: SE swe_houses(..., 'O').
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_PORPHYRY)
    if err:
        return (None, None, None, err)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (cusps, asc, mc, None)


def houses_sripati(
    jd_ut: float, lat_deg: float, lon_deg: float
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Srīpati: start with Porphyry, then cusp midpoints (H1′ etc.). SE midpoint formulas.
    Implementation: SE swe_houses(..., 'S') if supported; else compute from Porphyry.
    """
    cusps, ascmc, err = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_SRIPATI)
    if not err and cusps and len(cusps) >= 13:
        asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
        mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
        return (cusps, asc, mc, None)
    # Fallback: Porphyry then midpoint formula (spec: "cusp-midpoints")
    cusps, ascmc, err2 = calc_houses_se(jd_ut, lat_deg, lon_deg, SE_PORPHYRY)
    if err2 or not cusps or len(cusps) < 13:
        return (None, None, None, err or err2 or "no cusps")
    c = list(cusps)
    sri = [0.0] * 13
    for i in range(1, 12):
        sri[i] = ts.normalize_angle_deg((c[i] + c[i + 1]) / 2.0)
    sri[12] = ts.normalize_angle_deg((c[12] + c[1] + 360.0) / 2.0)
    asc = ascmc[0] if ascmc and len(ascmc) > 0 else None
    mc = ascmc[1] if ascmc and len(ascmc) > 1 else None
    return (sri, asc, mc, None)


def calc_houses(
    jd_ut: float,
    lat_deg: float,
    lon_deg: float,
    system: str,
) -> Tuple[Optional[Sequence[float]], Optional[float], Optional[float], Optional[str]]:
    """
    Single entry: compute houses for given system code (P,K,R,C,E,W,O,S).
    Returns (cusps_deg, asc_deg, mc_deg, error).
    """
    dispatch = {
        "P": houses_placidus,
        "K": houses_koch,
        "R": houses_regiomontanus,
        "C": houses_campanus,
        "E": houses_equal,
        "W": houses_whole_sign,
        "O": houses_porphyry,
        "S": houses_sripati,
    }
    fn = dispatch.get(system.upper())
    if not fn:
        return (None, None, None, f"unknown house system: {system}")
    return fn(jd_ut, lat_deg, lon_deg)


def house_from_cusps(lon_deg: float, cusps_deg: Sequence[float]) -> int:
    """
    House number (1-12) for ecliptic longitude given cusps[1..12].
    Assumes cusps in degrees [0,360); longitude normalized. Handles zodiac wraparound.
    """
    lon = lon_deg % 360.0
    if len(cusps_deg) < 13:
        return 1
    c1 = cusps_deg[1]
    if lon < c1:
        lon += 360.0
    for i in range(1, 13):
        c1 = cusps_deg[i]
        c2 = cusps_deg[i + 1] if i < 12 else cusps_deg[1] + 360.0
        if c2 < c1:
            c2 += 360.0
        if c1 <= lon < c2:
            return i
    return 12
