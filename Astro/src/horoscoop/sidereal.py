"""
Layer B – Astrology: sidereal zodiac, ayanāmśa.
Kernrelatie: λ_sid = λ_trop − A(t). SE sidereal modes (Lahiri, Krishnamurti, Raman, etc.).
Source: Spec "Tropisch ↔ sidereaal en ayanāmśa"; SE sidereal modes.
"""
from __future__ import annotations

from typing import Optional, Tuple

# SE sidereal mode constants (sweph.h); partial list
SE_SIDM_FAGAN_BRADLEY = 0
SE_SIDM_LAHIRI = 1
SE_SIDM_DELUCE = 2
SE_SIDM_RAMAN = 3
SE_SIDM_KRISHNAMURTI = 4
SE_SIDM_USER = 255

AYANAMSHA_MODES: dict[str, int] = {
    "Fagan_Bradley": SE_SIDM_FAGAN_BRADLEY,
    "Lahiri": SE_SIDM_LAHIRI,
    "De Luce": SE_SIDM_DELUCE,
    "Raman": SE_SIDM_RAMAN,
    "Krishnamurti": SE_SIDM_KRISHNAMURTI,
    "USER": SE_SIDM_USER,
}


def tropical_to_sidereal_deg(
    lon_tropical_deg: float, ayanamsha_deg: float
) -> float:
    """
    Sidereal longitude from tropical: λ_sid = λ_trop − A(t).
    All in degrees; output normalized [0, 360).
    Source: Spec "Kernrelatie (traditionele definitie): λ_sid = λ_trop − A(t)".
    """
    return (lon_tropical_deg - ayanamsha_deg) % 360.0


def sidereal_to_tropical_deg(
    lon_sidereal_deg: float, ayanamsha_deg: float
) -> float:
    """Tropical from sidereal: λ_trop = λ_sid + A(t). Output [0, 360)."""
    return (lon_sidereal_deg + ayanamsha_deg) % 360.0


def _swe_ayanamsha_available() -> bool:
    try:
        import swisseph  # type: ignore
        return True
    except ImportError:
        return False


def get_ayanamsha_deg(jd_tt: float, sid_mode: int) -> Tuple[float, Optional[str]]:
    """
    Ayanāmśa in degrees at JD(TT) for given SE sidereal mode.
    swe_get_ayanamsa_ut(jd_tt, sid_mode) or swe_get_ayanamsa(jd_tt, sid_mode).
    """
    if not _swe_ayanamsha_available():
        return (0.0, "swisseph not installed")
    import swisseph as swe  # type: ignore
    try:
        aya = swe.get_ayanamsa_ut(jd_tt, sid_mode)
        return (aya, None)
    except Exception as e:
        return (0.0, str(e))


def calc_planet_sidereal_se(
    jd_tt: float, body: int, sid_mode: int, flags: int = 0
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """
    Planet longitude (sidereal) via SE with sidereal flag: returns (lon_deg, lat_deg, error).
    SE: use SEFLG_SIDEREAL and swe_set_sid_mode(sid_mode); then swe_calc.
    """
    if not _swe_ayanamsha_available():
        return (None, None, "swisseph not installed")
    import swisseph as swe  # type: ignore
    try:
        swe.set_sid_mode(sid_mode)
        xx, ret = swe.calc_ut(jd_tt, body, getattr(swe, "SEFLG_SIDEREAL", 0x00010000) | getattr(swe, "SEFLG_SWIEPH", 2))
        if ret < 0:
            return (None, None, "calc error")
        lon = xx[0] % 360.0
        lat = xx[1]
        return (lon, lat, None)
    except Exception as e:
        return (None, None, str(e))


def ayanamsha_with_nutation(jd_tt: float, sid_mode: int) -> Tuple[float, bool, Optional[str]]:
    """
    Ayanāmśa and whether nutation is included (SEFLG_NONUT in *_ex variants).
    Returns (ayanamsha_deg, nutation_included, error).
    """
    aya, err = get_ayanamsha_deg(jd_tt, sid_mode)
    # SE default includes nutation unless SIDBIT_NO_NUTATION / nonut flag
    return (aya, True, err)
