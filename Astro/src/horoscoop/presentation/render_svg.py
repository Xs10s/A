"""
Deterministic SVG wheel renderer.
0° Aries at top; 12 sign divisions; optional house cusps, ASC marker; planets + 2-letter labels.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def _pol2xy(cx: float, cy: float, r: float, deg: float) -> Tuple[float, float]:
    """0° = Aries at 3 o'clock; rotate so 0° at top (12 o'clock)."""
    a = math.radians(deg - 90.0)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def render_wheel_svg(
    planet_lons_deg: Dict[str, float],
    house_cusps_deg: Optional[List[float]] = None,
    asc_deg: Optional[float] = None,
    size: int = 900,
    margin: int = 40,
) -> str:
    """
    Produce deterministic SVG wheel.
    - Outer + inner ring
    - 12 zodiac divisions (30° each)
    - House cusps if provided
    - ASC marker dot if provided
    - Planets as points + 2-letter labels
    """
    cx = cy = size / 2
    r_outer = (size / 2) - margin
    r_inner = r_outer * 0.82
    r_planets = r_outer * 0.73

    def line(deg: float, r0: float, r1: float, stroke: str = "#333") -> str:
        x0, y0 = _pol2xy(cx, cy, r0, deg)
        x1, y1 = _pol2xy(cx, cy, r1, deg)
        return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="1"/>'

    parts: List[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
    )
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="white" stroke="#222" stroke-width="2"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="#222" stroke-width="1"/>')

    # 12 zodiac divisions
    for k in range(12):
        parts.append(line(k * 30.0, r_inner, r_outer, stroke="#888"))

    # House cusps
    if house_cusps_deg:
        for cusp in house_cusps_deg:
            parts.append(line(cusp, r_inner * 0.95, r_outer, stroke="#444"))

    # ASC marker
    if asc_deg is not None:
        x, y = _pol2xy(cx, cy, r_outer * 0.98, asc_deg)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#111"/>')

    # Planets
    for name, lon in planet_lons_deg.items():
        x, y = _pol2xy(cx, cy, r_planets, lon)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#000"/>')
        lx, ly = _pol2xy(cx, cy, r_planets * 0.92, lon)
        label = str(name)[:2] if name else "??"
        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="14" text-anchor="middle">{label}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def render_wheel_from_engine(
    engine_json: dict[str, Any],
    method_id: str = "western_tropical",
) -> str:
    """
    Build SVG from engine JSON and method_id.
    western_tropical: tropical longitudes, houses if available.
    western_sidereal: sidereal longitudes.
    """
    from .view_model import build_view_model

    vm = build_view_model(engine_json)
    method = None
    for m in vm.get("methods", []):
        if m.get("id") == method_id:
            method = m
            break
    if not method:
        return render_wheel_svg({})

    sections = method.get("sections") or {}
    wheel = sections.get("wheel") or {}
    planet_lons = wheel.get("planet_lons")
    if not planet_lons:
        bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
        from .formatters import BODY_2LETTER
        try:
            from .. import sidereal
            vedic = engine_json.get("vedic") or {}
            aya_mode = (vedic.get("ayanamsha") or {}).get("mode") or "Lahiri"
            jd_tt = (engine_json.get("time") or {}).get("jd_tt")
            aya_deg = 0.0
            if method_id == "western_sidereal" and jd_tt is not None:
                sm = sidereal.AYANAMSHA_MODES.get(aya_mode, sidereal.SE_SIDM_LAHIRI)
                aya_deg, _, _ = sidereal.ayanamsha_with_nutation(jd_tt, sm)
            planet_lons = {}
            for bid, b in bodies.items():
                if isinstance(b, dict) and b.get("lon_deg") is not None:
                    lon = b["lon_deg"]
                    if method_id == "western_sidereal":
                        lon = sidereal.tropical_to_sidereal_deg(lon, aya_deg)
                    lbl = BODY_2LETTER.get(bid, bid[:2])
                    planet_lons[lbl] = lon
        except Exception:
            planet_lons = {}
    cusps = wheel.get("cusps")
    asc = wheel.get("asc_deg")
    return render_wheel_svg(
        planet_lons_deg=planet_lons or {},
        house_cusps_deg=cusps,
        asc_deg=asc,
    )
