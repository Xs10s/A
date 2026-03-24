"""
SVG/PNG chart generation for western horoscope.

The chart is a simple circular zodiac:
- Outer ring: 12 signs (30° each)
- Optional house cusps
- Planet positions by ecliptic longitude

All layout is deterministic.
"""
from __future__ import annotations

import math
from io import BytesIO
from typing import Any, Dict, List, Tuple, Optional


def _polar_to_cart(cx: float, cy: float, r: float, angle_deg: float) -> Tuple[float, float]:
    # Chart: 0° Aries at left (9 o'clock), increase clockwise.
    theta = math.radians(180.0 - angle_deg)
    x = cx + r * math.cos(theta)
    y = cy + r * math.sin(theta)
    return x, y


def build_svg(horoscoop: Dict[str, Any], width: int = 800, height: int = 800) -> str:
    western = horoscoop.get("western") or {}
    bodies = (horoscoop.get("astronomy") or {}).get("bodies") or {}
    houses = (western.get("houses") or {}).get("cusps_deg") or []

    cx, cy = width / 2.0, height / 2.0
    r_outer = min(width, height) * 0.45
    r_inner = r_outer * 0.8
    r_planets = r_inner * 0.9

    svg_parts: List[str] = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    svg_parts.append('<style>text{font-family:sans-serif;font-size:10px;}</style>')

    # Outer circle
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" stroke="#000" stroke-width="2" fill="none"/>'
    )

    # Zodiac signs (30° segments)
    sign_labels = [
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
    for i in range(12):
        start_deg = i * 30.0
        x1, y1 = _polar_to_cart(cx, cy, r_outer, start_deg)
        svg_parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x1}" y2="{y1}" stroke="#ccc" stroke-width="1"/>'
        )
        label_angle = start_deg + 15.0
        lx, ly = _polar_to_cart(cx, cy, r_outer * 0.7, label_angle)
        svg_parts.append(
            f'<text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="middle">{sign_labels[i]}</text>'
        )

    # Inner circle for houses
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" stroke="#888" stroke-width="1" fill="none"/>'
    )

    # Houses (if present)
    if houses:
        for idx, cusp in enumerate(houses):
            xh, yh = _polar_to_cart(cx, cy, r_inner, cusp)
            svg_parts.append(
                f'<line x1="{cx}" y1="{cy}" x2="{xh}" y2="{yh}" stroke="#444" stroke-width="1"/>'
            )
            label_angle = cusp
            lx, ly = _polar_to_cart(cx, cy, r_inner * 0.9, label_angle)
            svg_parts.append(
                f'<text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="middle">{idx+1}</text>'
            )

    # Planets
    for name, body in bodies.items():
        if not isinstance(body, dict):
            continue
        lon = body.get("lon_deg")
        if lon is None:
            continue
        xp, yp = _polar_to_cart(cx, cy, r_planets, lon)
        svg_parts.append(
            f'<circle cx="{xp}" cy="{yp}" r="5" fill="#0077cc" stroke="#000" stroke-width="1"/>'
        )
        svg_parts.append(
            f'<text x="{xp}" y="{yp-8}" text-anchor="middle" dominant-baseline="central">{name}</text>'
        )

    svg_parts.append("</svg>")
    return "".join(svg_parts)


def build_png(horoscoop: Dict[str, Any], width: int = 800, height: int = 800) -> Optional[bytes]:
    """
    Optional PNG rendering via cairosvg; returns None if cairosvg not available.
    """
    try:
        import cairosvg  # type: ignore
    except Exception:
        return None
    svg = build_svg(horoscoop, width=width, height=height)
    out = BytesIO()
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out)
    return out.getvalue()

