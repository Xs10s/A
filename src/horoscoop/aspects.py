"""
Layer B – Astrology: aspects and orb logic.
Angular separation, orb handling (config-driven: orb_base, luminary_bonus, etc.).
Applying/separating from relative longitude speed.
Source: Spec "Aspecten en orb-logica": d = min(|λ1−λ2|, 360°−|λ1−λ2|); |d−a| ≤ orbeff.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence, Tuple

# Standard aspects: exact angle (deg), name
ASPECT_DEFS: list[Tuple[float, str]] = [
    (0.0, "conjunction"),
    (60.0, "sextile"),
    (90.0, "square"),
    (120.0, "trine"),
    (180.0, "opposition"),
]

# Extended set (optional in config)
EXTENDED_ASPECT_DEFS: list[Tuple[float, str]] = [
    (0.0, "conjunction"),
    (45.0, "semi-square"),
    (60.0, "sextile"),
    (90.0, "square"),
    (120.0, "trine"),
    (135.0, "sesquiquadrate"),
    (150.0, "quincunx"),
    (180.0, "opposition"),
]


def angular_separation_deg(lon1_deg: float, lon2_deg: float) -> float:
    """
    Angular distance in degrees [0, 180].
    d = min(|λ1 − λ2|, 360° − |λ1 − λ2|).
    Source: Spec "Hoekafstand tussen twee lengtegraden".
    """
    d = abs((lon1_deg % 360.0) - (lon2_deg % 360.0))
    if d > 180.0:
        d = 360.0 - d
    return d


def aspect_exact_angle(aspect_name: str) -> Optional[float]:
    """Exact angle in degrees for named aspect."""
    for angle, name in ASPECT_DEFS:
        if name == aspect_name:
            return angle
    return None


def is_aspect_in_orb(
    lon1_deg: float,
    lon2_deg: float,
    exact_angle_deg: float,
    orb_deg: float,
) -> Tuple[bool, float]:
    """
    Aspect present if |d − a| ≤ orb. Returns (in_orb, actual_orb).
    actual_orb = |d − exact_angle| (signed convention: positive = separating if needed elsewhere).
    """
    d = angular_separation_deg(lon1_deg, lon2_deg)
    actual_orb = abs(d - exact_angle_deg)
    if actual_orb > 180.0:
        actual_orb = 360.0 - actual_orb
    return (actual_orb <= orb_deg, actual_orb)


def effective_orb(
    orb_base_deg: float,
    body1: str,
    body2: str,
    delta: Callable[[str, str, str], float],
    context: str = "default",
) -> float:
    """
    orb_eff = orb_base(aspect) + Δ(body1, body2, context).
    Δ can model luminary_bonus, angle_bonus, exactness weight. From kb_weight_rule + kb_property_def.
    Source: Spec "Orb‑management als formule (config‑gedreven)".
    """
    return orb_base_deg + delta(body1, body2, context)


def _rate_of_separation_deg_per_day(
    lon_a_deg: float,
    lon_b_deg: float,
    speed_a_deg_per_day: float,
    speed_b_deg_per_day: float,
) -> float:
    """
    Rate of change of angular separation d (0..180) in deg/day.
    delta_raw = (lon_b - lon_a) mod 360; d = min(delta_raw, 360 - delta_raw).
    dd/dt = (speed_b - speed_a) when delta_raw in (0,180); else -(speed_b - speed_a).
    """
    delta_raw = (lon_b_deg - lon_a_deg) % 360.0
    diff_speed = speed_b_deg_per_day - speed_a_deg_per_day
    if 0 < delta_raw < 180.0:
        return diff_speed
    if delta_raw > 180.0:
        return -diff_speed
    return 0.0  # 0 or 180: degenerate


def find_aspects(
    lon1_deg: float,
    lon2_deg: float,
    aspects: Optional[Sequence[Tuple[float, str]]] = None,
    orb_deg: float = 8.0,
    speed1_deg_per_day: Optional[float] = None,
    speed2_deg_per_day: Optional[float] = None,
    orb_resolver: Optional[Callable[[str, str, str], float]] = None,
    body_a: str = "A",
    body_b: str = "B",
) -> list[Tuple[str, float, float, bool]]:
    """
    Find all aspects between two longitudes.
    Returns list of (aspect_name, exact_angle_deg, orb_degrees, applying).
    Applying: True if aspect is moving toward exact (based on relative longitude speed).
    If orb_resolver(aspect_type, body_a, body_b) is provided, orb_deg per aspect is taken from it.
    """
    if aspects is None:
        aspects = ASPECT_DEFS
    result = []
    d = angular_separation_deg(lon1_deg, lon2_deg)
    dd_dt: Optional[float] = None
    if speed1_deg_per_day is not None and speed2_deg_per_day is not None:
        dd_dt = _rate_of_separation_deg_per_day(
            lon1_deg, lon2_deg, speed1_deg_per_day, speed2_deg_per_day
        )
    for exact, name in aspects:
        actual_orb = min(abs(d - exact), 360.0 - abs(d - exact))
        allowed = orb_deg
        if orb_resolver is not None:
            allowed = orb_resolver(name, body_a, body_b)
        if actual_orb <= allowed:
            applying = False
            if dd_dt is not None:
                applying = (d < exact and dd_dt > 0) or (d > exact and dd_dt < 0)
            result.append((name, exact, actual_orb, applying))
    return result
