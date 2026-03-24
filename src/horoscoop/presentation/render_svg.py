"""
Deterministic SVG wheel renderer.
0° Aries at top; 12 sign divisions; optional house cusps, ASC marker; planets + 2-letter labels.
Panchanga and BaZi banners for non-wheel methods.
"""
from __future__ import annotations

import math
from html import escape
from typing import Any, Dict, List, Optional, Tuple

STEM_META: Dict[str, Dict[str, str]] = {
    "Jiǎ": {"hanzi": "甲", "name_ascii": "Jia", "yin_yang": "Yang", "element_en": "Wood", "element_nl": "Hout"},
    "Yǐ": {"hanzi": "乙", "name_ascii": "Yi", "yin_yang": "Yin", "element_en": "Wood", "element_nl": "Hout"},
    "Bǐng": {"hanzi": "丙", "name_ascii": "Bing", "yin_yang": "Yang", "element_en": "Fire", "element_nl": "Vuur"},
    "Dīng": {"hanzi": "丁", "name_ascii": "Ding", "yin_yang": "Yin", "element_en": "Fire", "element_nl": "Vuur"},
    "Wù": {"hanzi": "戊", "name_ascii": "Wu", "yin_yang": "Yang", "element_en": "Earth", "element_nl": "Aarde"},
    "Jǐ": {"hanzi": "己", "name_ascii": "Ji", "yin_yang": "Yin", "element_en": "Earth", "element_nl": "Aarde"},
    "Gēng": {"hanzi": "庚", "name_ascii": "Geng", "yin_yang": "Yang", "element_en": "Metal", "element_nl": "Metaal"},
    "Xīn": {"hanzi": "辛", "name_ascii": "Xin", "yin_yang": "Yin", "element_en": "Metal", "element_nl": "Metaal"},
    "Rén": {"hanzi": "壬", "name_ascii": "Ren", "yin_yang": "Yang", "element_en": "Water", "element_nl": "Water"},
    "Guǐ": {"hanzi": "癸", "name_ascii": "Gui", "yin_yang": "Yin", "element_en": "Water", "element_nl": "Water"},
}

BRANCH_META: Dict[str, Dict[str, str]] = {
    "Zǐ": {"hanzi": "子", "name_ascii": "Zi", "animal_en": "Rat", "animal_nl": "Rat", "yin_yang": "Yang", "element_en": "Water", "element_nl": "Water"},
    "Chǒu": {"hanzi": "丑", "name_ascii": "Chou", "animal_en": "Ox", "animal_nl": "Os", "yin_yang": "Yin", "element_en": "Earth", "element_nl": "Aarde"},
    "Yín": {"hanzi": "寅", "name_ascii": "Yin", "animal_en": "Tiger", "animal_nl": "Tijger", "yin_yang": "Yang", "element_en": "Wood", "element_nl": "Hout"},
    "Mǎo": {"hanzi": "卯", "name_ascii": "Mao", "animal_en": "Rabbit", "animal_nl": "Konijn", "yin_yang": "Yin", "element_en": "Wood", "element_nl": "Hout"},
    "Chén": {"hanzi": "辰", "name_ascii": "Chen", "animal_en": "Dragon", "animal_nl": "Draak", "yin_yang": "Yang", "element_en": "Earth", "element_nl": "Aarde"},
    "Sì": {"hanzi": "巳", "name_ascii": "Si", "animal_en": "Snake", "animal_nl": "Slang", "yin_yang": "Yin", "element_en": "Fire", "element_nl": "Vuur"},
    "Wǔ": {"hanzi": "午", "name_ascii": "Wu", "animal_en": "Horse", "animal_nl": "Paard", "yin_yang": "Yang", "element_en": "Fire", "element_nl": "Vuur"},
    "Wèi": {"hanzi": "未", "name_ascii": "Wei", "animal_en": "Goat", "animal_nl": "Geit", "yin_yang": "Yin", "element_en": "Earth", "element_nl": "Aarde"},
    "Shēn": {"hanzi": "申", "name_ascii": "Shen", "animal_en": "Monkey", "animal_nl": "Aap", "yin_yang": "Yang", "element_en": "Metal", "element_nl": "Metaal"},
    "Yǒu": {"hanzi": "酉", "name_ascii": "You", "animal_en": "Rooster", "animal_nl": "Haan", "yin_yang": "Yin", "element_en": "Metal", "element_nl": "Metaal"},
    "Xū": {"hanzi": "戌", "name_ascii": "Xu", "animal_en": "Dog", "animal_nl": "Hond", "yin_yang": "Yang", "element_en": "Earth", "element_nl": "Aarde"},
    "Hài": {"hanzi": "亥", "name_ascii": "Hai", "animal_en": "Pig", "animal_nl": "Varken", "yin_yang": "Yin", "element_en": "Water", "element_nl": "Water"},
}

HIDDEN_STEMS_BY_BRANCH: Dict[str, List[str]] = {
    "Zǐ": ["Guǐ"],
    "Chǒu": ["Jǐ", "Guǐ", "Xīn"],
    "Yín": ["Jiǎ", "Bǐng", "Wù"],
    "Mǎo": ["Yǐ"],
    "Chén": ["Wù", "Yǐ", "Guǐ"],
    "Sì": ["Bǐng", "Wù", "Gēng"],
    "Wǔ": ["Dīng", "Jǐ"],
    "Wèi": ["Jǐ", "Yǐ", "Dīng"],
    "Shēn": ["Gēng", "Rén", "Wù"],
    "Yǒu": ["Xīn"],
    "Xū": ["Wù", "Xīn", "Dīng"],
    "Hài": ["Rén", "Jiǎ"],
}

VAARA_BY_ENGLISH: Dict[str, Tuple[str, str]] = {
    "sunday": ("Ravivara", "रविवार"),
    "monday": ("Somavara", "सोमवार"),
    "tuesday": ("Mangalavara", "मंगलवार"),
    "wednesday": ("Budhavara", "बुधवार"),
    "thursday": ("Guruvara", "गुरुवार"),
    "friday": ("Shukravara", "शुक्रवार"),
    "saturday": ("Shanivara", "शनिवार"),
}

TITHI_NAMES: Dict[int, Tuple[str, str]] = {
    1: ("Pratipada", "प्रतिपदा"), 2: ("Dvitiya", "द्वितीया"), 3: ("Tritiya", "तृतीया"), 4: ("Chaturthi", "चतुर्थी"),
    5: ("Panchami", "पञ्चमी"), 6: ("Shashthi", "षष्ठी"), 7: ("Saptami", "सप्तमी"), 8: ("Ashtami", "अष्टमी"),
    9: ("Navami", "नवमी"), 10: ("Dashami", "दशमी"), 11: ("Ekadashi", "एकादशी"), 12: ("Dvadashi", "द्वादशी"),
    13: ("Trayodashi", "त्रयोदशी"), 14: ("Chaturdashi", "चतुर्दशी"), 15: ("Purnima/Amavasya", "पूर्णिमा/अमावस्या"),
    16: ("Pratipada", "प्रतिपदा"), 17: ("Dvitiya", "द्वितीया"), 18: ("Tritiya", "तृतीया"), 19: ("Chaturthi", "चतुर्थी"),
    20: ("Panchami", "पञ्चमी"), 21: ("Shashthi", "षष्ठी"), 22: ("Saptami", "सप्तमी"), 23: ("Ashtami", "अष्टमी"),
    24: ("Navami", "नवमी"), 25: ("Dashami", "दशमी"), 26: ("Ekadashi", "एकादशी"), 27: ("Dvadashi", "द्वादशी"),
    28: ("Trayodashi", "त्रयोदशी"), 29: ("Chaturdashi", "चतुर्दशी"), 30: ("Purnima/Amavasya", "पूर्णिमा/अमावस्या"),
}

VEDIC_LABELS: Dict[str, Tuple[str, str]] = {
    "Vaara": ("Vara", "वार"),
    "Tithi": ("Tithi", "तिथि"),
    "Nakṣatra": ("Nakshatra", "नक्षत्र"),
    "Yoga": ("Yoga", "योग"),
    "Karaṇa": ("Karana", "करण"),
}

NAKSHATRA_NAMES: Dict[int, Tuple[str, str]] = {
    1: ("Ashwini", "अश्विनी"), 2: ("Bharani", "भरणी"), 3: ("Krittika", "कृत्तिका"), 4: ("Rohini", "रोहिणी"),
    5: ("Mrigashira", "मृगशीर्ष"), 6: ("Ardra", "आर्द्रा"), 7: ("Punarvasu", "पुनर्वसु"), 8: ("Pushya", "पुष्य"),
    9: ("Ashlesha", "आश्लेषा"), 10: ("Magha", "मघा"), 11: ("Purva Phalguni", "पूर्व फाल्गुनी"), 12: ("Uttara Phalguni", "उत्तर फाल्गुनी"),
    13: ("Hasta", "हस्त"), 14: ("Chitra", "चित्रा"), 15: ("Swati", "स्वाती"), 16: ("Vishakha", "विशाखा"),
    17: ("Anuradha", "अनुराधा"), 18: ("Jyeshtha", "ज्येष्ठा"), 19: ("Mula", "मूल"), 20: ("Purva Ashadha", "पूर्वाषाढा"),
    21: ("Uttara Ashadha", "उत्तराषाढा"), 22: ("Shravana", "श्रवण"), 23: ("Dhanishtha", "धनिष्ठा"), 24: ("Shatabhisha", "शतभिषा"),
    25: ("Purva Bhadrapada", "पूर्व भाद्रपदा"), 26: ("Uttara Bhadrapada", "उत्तर भाद्रपदा"), 27: ("Revati", "रेवती"),
}

YOGA_NAMES: Dict[int, Tuple[str, str]] = {
    1: ("Vishkambha", "विष्कम्भ"), 2: ("Priti", "प्रीति"), 3: ("Ayushman", "आयुष्मान"), 4: ("Saubhagya", "सौभाग्य"),
    5: ("Shobhana", "शोभन"), 6: ("Atiganda", "अतिगण्ड"), 7: ("Sukarma", "सुकर्मा"), 8: ("Dhriti", "धृति"),
    9: ("Shula", "शूल"), 10: ("Ganda", "गण्ड"), 11: ("Vriddhi", "वृद्धि"), 12: ("Dhruva", "ध्रुव"),
    13: ("Vyaghata", "व्याघात"), 14: ("Harshana", "हर्षण"), 15: ("Vajra", "वज्र"), 16: ("Siddhi", "सिद्धि"),
    17: ("Vyatipata", "व्यतीपात"), 18: ("Variyana", "वरीयान"), 19: ("Parigha", "परिघ"), 20: ("Shiva", "शिव"),
    21: ("Siddha", "सिद्ध"), 22: ("Sadhya", "साध्य"), 23: ("Shubha", "शुभ"), 24: ("Shukla", "शुक्ल"),
    25: ("Brahma", "ब्रह्म"), 26: ("Indra", "इन्द्र"), 27: ("Vaidhriti", "वैधृति"),
}

KARANA_NAMES: Dict[int, Tuple[str, str]] = {
    1: ("Bava", "बव"), 2: ("Balava", "बालव"), 3: ("Kaulava", "कौलव"), 4: ("Taitila", "तैतिल"),
    5: ("Gara", "गर"), 6: ("Vanija", "वणिज"), 7: ("Vishti", "विष्टि"), 8: ("Shakuni", "शकुनि"),
    9: ("Chatushpada", "चतुष्पद"), 10: ("Naga", "नाग"), 11: ("Kimstughna", "किंस्तुघ्न"),
}


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
    """Produce a classic western-style astrological wheel SVG."""
    # Reserve dedicated legend space below the wheel.
    legend_reserved_h = 185.0
    cx = size / 2.0
    cy = (size - legend_reserved_h) / 2.0 + 14.0
    max_r_x = min((size - margin) - cx, cx - margin)
    max_r_y = min((size - margin - legend_reserved_h) - cy, cy - margin)
    r_outer = max(180.0, min(max_r_x, max_r_y))
    r_tick_outer = r_outer * 0.99
    r_tick_inner_minor = r_outer * 0.96
    r_tick_inner_major = r_outer * 0.935
    r_zodiac_outer = r_outer * 0.91
    r_zodiac_inner = r_outer * 0.77
    r_houses_inner = r_outer * 0.60
    r_planets = r_outer * 0.69

    zodiac_glyphs = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
    planet_glyphs = {
        "Su": "☉",
        "Mo": "☽",
        "Me": "☿",
        "Ve": "♀",
        "Ma": "♂",
        "Ju": "♃",
        "Sa": "♄",
    }

    aspect_palette = {
        "conjunction": "#7b4bc9",
        "sextile": "#2f8f8a",
        "square": "#c74646",
        "trine": "#2f5fbf",
        "opposition": "#c74646",
    }

    def text(x: float, y: float, t: str, size_px: int = 12, weight: str = "400") -> str:
        return (
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="{size_px}" '
            f'font-weight="{weight}" text-anchor="middle" dominant-baseline="middle">{escape(t)}</text>'
        )

    def line(deg: float, r0: float, r1: float, stroke: str = "#333") -> str:
        x0, y0 = _pol2xy(cx, cy, r0, deg)
        x1, y1 = _pol2xy(cx, cy, r1, deg)
        return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="1"/>'

    parts: List[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
    )
    parts.append(f'<rect width="{size}" height="{size}" fill="#ffffff"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#ffffff" stroke="#121212" stroke-width="1.6"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac_outer}" fill="none" stroke="#121212" stroke-width="1.0"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac_inner}" fill="none" stroke="#121212" stroke-width="1.0"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_houses_inner}" fill="none" stroke="#121212" stroke-width="1.0"/>')

    # Degree ticks (1° minor, 5° major)
    for deg in range(360):
        is_major = deg % 5 == 0
        parts.append(
            line(
                float(deg),
                r_tick_inner_major if is_major else r_tick_inner_minor,
                r_tick_outer,
                stroke="#1a1a1a",
            )
        )

    # 12 zodiac divisions + glyphs
    for k in range(12):
        parts.append(line(k * 30.0, r_zodiac_inner, r_zodiac_outer, stroke="#888"))
        gx, gy = _pol2xy(cx, cy, (r_zodiac_outer + r_zodiac_inner) / 2.0, k * 30.0 + 15.0)
        parts.append(text(gx, gy, zodiac_glyphs[k], size_px=20, weight="700"))

    # House cusps and numbers
    if house_cusps_deg:
        for i, cusp in enumerate(house_cusps_deg[:12], start=1):
            parts.append(line(cusp, r_houses_inner, r_zodiac_inner, stroke="#444"))
            hx, hy = _pol2xy(cx, cy, r_houses_inner * 0.88, cusp + 12.0)
            parts.append(text(hx, hy, str(i), size_px=11, weight="700"))

    # ASC marker
    if asc_deg is not None:
        x, y = _pol2xy(cx, cy, r_zodiac_outer * 1.02, asc_deg)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#111"/>')
        tx, ty = _pol2xy(cx, cy, r_zodiac_outer * 1.08, asc_deg)
        parts.append(text(tx, ty, "ASC", size_px=10, weight="700"))

    # Planet points + labels
    planet_points: List[Dict[str, float | str]] = []
    for name, lon in planet_lons_deg.items():
        x, y = _pol2xy(cx, cy, r_planets, lon)
        planet_points.append({"x": x, "y": y, "lon": float(lon), "key": str(name)})
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#000"/>')
        lx, ly = _pol2xy(cx, cy, r_planets * 0.93, lon)
        label_key = str(name)[:2] if name else "??"
        glyph = planet_glyphs.get(label_key, label_key)
        parts.append(text(lx, ly, glyph, size_px=13, weight="700"))
        # Keep compact Latin keys in SVG for compatibility/tests.
        ax, ay = _pol2xy(cx, cy, r_planets * 0.985, lon)
        parts.append(text(ax, ay, label_key, size_px=8, weight="400"))

    # Aspect web with classic color coding.
    def _angle_delta(a: float, b: float) -> float:
        d = abs((a - b) % 360.0)
        return min(d, 360.0 - d)

    def _aspect_type(delta: float) -> Optional[str]:
        checks = [
            ("conjunction", 0.0, 8.0),
            ("sextile", 60.0, 4.0),
            ("square", 90.0, 6.0),
            ("trine", 120.0, 6.0),
            ("opposition", 180.0, 8.0),
        ]
        best: Optional[str] = None
        best_err = 999.0
        for name, exact, orb in checks:
            err = abs(delta - exact)
            if err <= orb and err < best_err:
                best = name
                best_err = err
        return best

    for i in range(len(planet_points)):
        p1 = planet_points[i]
        for j in range(i + 1, len(planet_points)):
            p2 = planet_points[j]
            delta = _angle_delta(float(p1["lon"]), float(p2["lon"]))
            a_type = _aspect_type(delta)
            if not a_type:
                continue
            color = aspect_palette.get(a_type, "#555")
            parts.append(
                f'<line x1="{float(p1["x"]):.1f}" y1="{float(p1["y"]):.1f}" x2="{float(p2["x"]):.1f}" y2="{float(p2["y"]):.1f}" '
                f'stroke="{color}" stroke-opacity="0.7" stroke-width="1.1"/>'
            )

    # Clear legend panel.
    lx = margin
    ly = size - legend_reserved_h + 8
    lw = size - (2 * margin)
    lh = legend_reserved_h - 20
    parts.append(f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{lw}" height="{lh}" fill="#ffffff" stroke="#222" stroke-width="1"/>')
    parts.append(
        f'<text x="{lx + 10:.1f}" y="{ly + 18:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700">LEGENDA</text>'
    )
    legend_items = [
        ("☉ ☽ ☿ ♀ ♂ ♃ ♄", "Planeten / Planets", "#111"),
        ("ASC", "Ascendant", "#111"),
        ("Conjunctie / Conjunction", "0°", aspect_palette["conjunction"]),
        ("Sextiel / Sextile", "60°", aspect_palette["sextile"]),
        ("Kwadraat / Square", "90°", aspect_palette["square"]),
        ("Driehoek / Trine", "120°", aspect_palette["trine"]),
        ("Oppositie / Opposition", "180°", aspect_palette["opposition"]),
    ]
    yy = ly + 38
    for left, right, col in legend_items:
        parts.append(f'<line x1="{lx + 10:.1f}" y1="{yy - 4:.1f}" x2="{lx + 28:.1f}" y2="{yy - 4:.1f}" stroke="{col}" stroke-width="2"/>')
        parts.append(
            f'<text x="{lx + 34:.1f}" y="{yy:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#222">{escape(left)}</text>'
        )
        parts.append(
            f'<text x="{lx + 188:.1f}" y="{yy:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#555">{escape(right)}</text>'
        )
        yy += 18

    parts.append("</svg>")
    return "\n".join(parts)


def render_wheel_from_engine(
    engine_json: dict[str, Any],
    method_id: str = "western_tropical",
    *,
    size: int = 900,
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
        size=size,
    )


def _svg_text_banner(
    title: str,
    lines: List[Tuple[str, str]],
    width: int = 900,
    height: int = 240,
    accent: str = "#884dc9",
) -> str:
    """Generic title + key/value rows for Panchanga / BaZi."""
    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#faf8fc" stroke="#e8e0f0" stroke-width="1"/>',
        f'<text x="28" y="42" font-family="Georgia,serif" font-size="20" fill="{accent}">{escape(title)}</text>',
    ]
    y = 78
    for label, value in lines:
        parts.append(
            f'<text x="28" y="{y}" font-family="system-ui,sans-serif" font-size="13" fill="#555">'
            f'<tspan font-weight="600">{escape(label)}</tspan>'
            f' <tspan fill="#222">{escape(value)}</tspan>'
            f"</text>"
        )
        y += 26
    parts.append("</svg>")
    return "\n".join(parts)


def render_panchanga_banner_svg(
    engine_json: dict[str, Any],
    width: int = 900,
    height: int = 260,
    *,
    locale: str = "nl-NL",
) -> str:
    """Vedic dashboard in North-Indian style layout + Panchanga panels."""
    lang = (locale or "nl-NL").lower()
    is_en = lang.startswith("en")

    def tr(nl: str, en: str) -> str:
        return en if is_en else nl

    def title(text: str) -> str:
        return text.upper()

    def vedic_label(label: str) -> str:
        base = VEDIC_LABELS.get(label)
        if not base:
            return title(label)
        roman, devanagari = base
        translated = {
            "Vaara": tr("Weekdag", "Weekday"),
            "Tithi": "Tithi",
            "Nakṣatra": "Nakshatra",
            "Yoga": "Yoga",
            "Karaṇa": "Karana",
        }.get(label, label)
        return f"{devanagari} {roman} - {translated}"

    def vedic_value(label: str, value: str) -> str:
        if label == "Vaara":
            key = str(value).strip().lower()
            if key in VAARA_BY_ENGLISH:
                roman, dev = VAARA_BY_ENGLISH[key]
                return f"{dev} {roman} ({tr('weekdag', 'weekday')}: {value})"
        if label == "Tithi":
            try:
                idx = int(str(value))
                if idx in TITHI_NAMES:
                    roman, dev = TITHI_NAMES[idx]
                    return f"{dev} {roman} ({tr('dag', 'day')} {idx})"
            except Exception:
                pass
        if label == "Nakṣatra":
            try:
                idx = int(str(value))
                if idx in NAKSHATRA_NAMES:
                    roman, dev = NAKSHATRA_NAMES[idx]
                    return f"{dev} {roman} ({tr('index', 'index')} {idx})"
            except Exception:
                pass
        if label == "Yoga":
            try:
                idx = int(str(value))
                if idx in YOGA_NAMES:
                    roman, dev = YOGA_NAMES[idx]
                    return f"{dev} {roman} ({tr('index', 'index')} {idx})"
            except Exception:
                pass
        if label == "Karaṇa":
            raw = str(value).strip()
            if "," in raw:
                out: List[str] = []
                for part in [x.strip() for x in raw.split(",") if x.strip()]:
                    try:
                        idx = int(part)
                        if idx in KARANA_NAMES:
                            roman, dev = KARANA_NAMES[idx]
                            out.append(f"{dev} {roman} ({idx})")
                        else:
                            out.append(part)
                    except Exception:
                        out.append(part)
                if out:
                    return " | ".join(out)
            try:
                idx = int(raw)
                if idx in KARANA_NAMES:
                    roman, dev = KARANA_NAMES[idx]
                    return f"{dev} {roman} ({tr('index', 'index')} {idx})"
            except Exception:
                pass
        return str(value)

    panch = (engine_json.get("vedic") or {}).get("panchanga")
    if not panch or not isinstance(panch, dict):
        return _svg_text_banner("Panchanga", [("Status", tr("niet beschikbaar voor deze invoer", "not available for this input"))], width, height)

    canvas_w = max(width, 1240)
    canvas_h = max(height, 920)
    pad = 16
    top_h = 500
    bot_y = top_h + 12
    bot_h = canvas_h - bot_y - pad

    lines: List[Tuple[str, str]] = []
    v = panch.get("vaara")
    if v:
        lines.append(("Vaara", str(v)))
    tithi = panch.get("tithi") or {}
    if isinstance(tithi, dict) and tithi.get("index") is not None:
        lines.append(("Tithi", str(tithi.get("index"))))
    nak = panch.get("nakshatra") or {}
    if isinstance(nak, dict) and nak.get("index") is not None:
        lines.append(("Nakṣatra", str(nak.get("index"))))
    yoga = panch.get("yoga") or {}
    if isinstance(yoga, dict) and yoga.get("index") is not None:
        lines.append(("Yoga", str(yoga.get("index"))))
    kar = panch.get("karana") or {}
    if isinstance(kar, dict):
        kix = kar.get("indices") or []
        if kix:
            lines.append(("Karaṇa", ", ".join(str(x) for x in kix)))

    if not lines:
        lines.append(("Panchanga", tr("gegevens onvolledig", "incomplete data")))

    # North-Indian styled frame and house structure (matching user reference)
    x0 = pad + 6
    y0 = 44
    w = canvas_w - 2 * (pad + 6)
    h = top_h - y0 - 12
    x1 = x0 + w
    y1 = y0 + h
    cx = x0 + w / 2
    cy = y0 + h / 2

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">',
        f'<rect width="{canvas_w}" height="{canvas_h}" fill="#ffffff"/>',
        f'<rect x="{pad}" y="{pad}" width="{canvas_w - 2*pad}" height="{canvas_h - 2*pad}" fill="#ffffff" stroke="#d7c7eb" stroke-width="1"/>',
        f'<rect x="{pad}" y="{pad}" width="{canvas_w - 2*pad}" height="28" fill="#884dc9"/>',
        f'<text x="{pad + 12}" y="{pad + 20}" font-family="DM Sans,system-ui,sans-serif" font-size="15" font-weight="700" fill="#ffffff">{escape(title(tr("Vedisch dashboard (Panchanga + huizenstructuur)", "Vedic dashboard (Panchanga + house structure)")))}</text>',
    ]

    # Main chart container (straight-line North Indian)
    parts.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fffdfa" stroke="#111" stroke-width="1"/>')

    # Core geometry - straight lines only
    top = (cx, y0 + 20)
    right = (x1 - 20, cy)
    bottom = (cx, y1 - 20)
    left = (x0 + 20, cy)
    c_top = (cx, cy - 92)
    c_right = (cx + 142, cy)
    c_bottom = (cx, cy + 92)
    c_left = (cx - 142, cy)

    # Outer diagonals (corner to corner)
    parts.append(f'<line x1="{x0 + 20:.1f}" y1="{y0 + 20:.1f}" x2="{x1 - 20:.1f}" y2="{y1 - 20:.1f}" stroke="#111" stroke-width="1.5"/>')
    parts.append(f'<line x1="{x0 + 20:.1f}" y1="{y1 - 20:.1f}" x2="{x1 - 20:.1f}" y2="{y0 + 20:.1f}" stroke="#111" stroke-width="1.5"/>')

    # Central diamond
    parts.append(
        f'<polygon points="{c_top[0]:.1f},{c_top[1]:.1f} {c_right[0]:.1f},{c_right[1]:.1f} {c_bottom[0]:.1f},{c_bottom[1]:.1f} {c_left[0]:.1f},{c_left[1]:.1f}" fill="none" stroke="#111" stroke-width="1.5"/>'
    )

    # Straight sector lines
    for a, b in [
        (top, c_left), (top, c_right),
        (right, c_top), (right, c_bottom),
        (bottom, c_left), (bottom, c_right),
        (left, c_top), (left, c_bottom),
    ]:
        parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#111" stroke-width="1.2"/>')

    # Center marker only (no ornamental curve/circle remnants)
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.5" fill="#111"/>')

    # 12 house numbers around the structure
    house_pos = [
        (cx, y0 + 96), (cx - 180, y0 + 132), (cx - 250, cy), (cx - 138, cy + 64),
        (cx - 182, y1 - 122), (cx - 126, y1 - 74), (cx, y1 - 96), (cx + 126, y1 - 74),
        (cx + 182, y1 - 122), (cx + 138, cy + 64), (cx + 250, cy), (cx + 180, y0 + 132),
    ]
    for i, (hx, hy) in enumerate(house_pos, start=1):
        parts.append(f'<text x="{hx:.1f}" y="{hy:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="22" font-weight="700" fill="#c95d5d" text-anchor="middle">{i}</text>')

    # House-topic hints (kept minimal)
    topics = [
        (cx - 242, y0 + 72, tr("Geld", "Money")),
        (cx + 210, y0 + 72, tr("Uitgaven", "Expenses")),
        (cx - 278, cy + 6, tr("Avontuur", "Adventures")),
        (cx + 242, cy + 6, tr("Geluk", "Luck")),
        (cx - 228, y1 - 66, tr("Studie", "Study")),
        (cx + 220, y1 - 66, tr("Religie", "Religion")),
        (cx, y0 + 118, tr("Lichaam", "Body")),
        (cx, cy + 16, tr("Werk", "Work")),
        (cx, y1 - 122, tr("Relatie", "Partnership")),
    ]
    for tx, ty, t in topics:
        parts.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="19" font-weight="700" fill="#2f2f2f" text-anchor="middle">{escape(title(t))}</text>')

    # Vedic planets (graha symbols + Sanskrit/Devanagari), positioned by sidereal longitude
    graha_meta: Dict[str, Tuple[str, str, str]] = {
        "Sun": ("☉", "Surya", "सूर्य"),
        "Moon": ("☽", "Chandra", "चन्द्र"),
        "Mars": ("♂", "Mangala", "मंगल"),
        "Mercury": ("☿", "Budha", "बुध"),
        "Jupiter": ("♃", "Guru", "गुरु"),
        "Venus": ("♀", "Shukra", "शुक्र"),
        "Saturn": ("♄", "Shani", "शनि"),
    }
    try:
        bodies = (engine_json.get("astronomy") or {}).get("bodies") or {}
        vedic = engine_json.get("vedic") or {}
        aya_mode = (vedic.get("ayanamsha") or {}).get("mode") or "Lahiri"
        jd_tt = (engine_json.get("time") or {}).get("jd_tt")
        aya_deg = 0.0
        if jd_tt is not None:
            from .. import sidereal
            sm = sidereal.AYANAMSHA_MODES.get(aya_mode, sidereal.SE_SIDM_LAHIRI)
            aya_deg, _, _ = sidereal.ayanamsha_with_nutation(jd_tt, sm)
        rx = w * 0.28
        ry = h * 0.22
        plotted: List[Tuple[float, float]] = []
        # Priority stacking: Sun/Moon first, then visible classical grahas.
        graha_order = ["Sun", "Moon", "Jupiter", "Venus", "Mercury", "Mars", "Saturn"]
        for key in graha_order:
            if key not in graha_meta:
                continue
            sym, latin, deva = graha_meta[key]
            b = bodies.get(key) or {}
            lon = b.get("lon_deg") if isinstance(b, dict) else None
            if lon is None:
                continue
            try:
                from .. import sidereal
                slon = sidereal.tropical_to_sidereal_deg(float(lon), aya_deg)
            except Exception:
                slon = float(lon)
            ang = math.radians((slon % 360.0) - 90.0)
            gx = cx + rx * math.cos(ang)
            gy = cy + ry * math.sin(ang)
            # Anti-overlap pass 1: radial push from existing labels.
            for _ in range(4):
                moved = False
                for px, py in plotted:
                    dx = gx - px
                    dy = gy - py
                    if (dx * dx + dy * dy) < (44.0 * 44.0):
                        gx += math.cos(ang) * 10.0
                        gy += math.sin(ang) * 10.0
                        moved = True
                if not moved:
                    break
            # Anti-overlap pass 2: slight tangential offset if still close.
            for px, py in plotted:
                dx = gx - px
                dy = gy - py
                if (dx * dx + dy * dy) < (40.0 * 40.0):
                    gx += -math.sin(ang) * 8.0
                    gy += math.cos(ang) * 8.0
            plotted.append((gx, gy))
            parts.append(f'<rect x="{gx - 17:.1f}" y="{gy - 13:.1f}" width="34" height="26" fill="#ffffff" stroke="#d7c7eb" stroke-width="1"/>')
            parts.append(f'<text x="{gx:.1f}" y="{gy - 1:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="13" font-weight="700" fill="#2f2f2f" text-anchor="middle">{escape(sym)}</text>')
            label = f"{deva} {latin}" if not is_en else f"{deva} {latin}"
            parts.append(f'<text x="{gx:.1f}" y="{gy + 12:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="9" fill="#6f6f6f" text-anchor="middle">{escape(label)}</text>')
    except Exception:
        pass

    # Bottom dashboard cards
    card_gap = 10
    card_w = (canvas_w - 2 * pad - 2 * card_gap) / 3.0
    card_y = bot_y
    card_h = 220
    cards = [
        (tr("Panchanga kern", "Panchanga core"), lines[:3]),
        (tr("Aanvullend", "Additional"), lines[3:] or [("—", tr("geen extra waarden", "no extra values"))]),
        (tr("Leeswijzer", "How to read"), [
            (tr("Vaara", "Vaara"), tr("Dagsfeer en ritme", "Day quality and rhythm")),
            (tr("Tithi", "Tithi"), tr("Maansfase-energie", "Lunar phase energy")),
            (tr("Nakshatra", "Nakshatra"), tr("Emotioneel veld", "Emotional field")),
            (tr("Yoga", "Yoga"), tr("Dynamiek zon-maan", "Sun-moon dynamic")),
        ]),
    ]
    for idx, (card_title, rows) in enumerate(cards):
        x = pad + idx * (card_w + card_gap)
        parts.append(f'<rect x="{x:.1f}" y="{card_y}" width="{card_w:.1f}" height="{card_h}" fill="#fbf8ff" stroke="#d7c7eb" stroke-width="1"/>')
        parts.append(f'<rect x="{x:.1f}" y="{card_y}" width="{card_w:.1f}" height="24" fill="#f5eefc"/>')
        parts.append(f'<text x="{x + 10:.1f}" y="{card_y + 17}" font-family="DM Sans,system-ui,sans-serif" font-size="13" font-weight="700" fill="#3a3a3a">{escape(title(card_title))}</text>')
        ry = card_y + 46
        for lbl, val in rows[:7]:
            if idx < 2:
                parts.append(f'<text x="{x + 10:.1f}" y="{ry}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#6f6f6f">{escape(vedic_label(str(lbl)))}:</text>')
                parts.append(f'<text x="{x + 10:.1f}" y="{ry + 15}" font-family="DM Sans,system-ui,sans-serif" font-size="13" fill="#3a3a3a">{escape(vedic_value(str(lbl), str(val)))}</text>')
                ry += 34
            else:
                parts.append(f'<text x="{x + 10:.1f}" y="{ry}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#6f6f6f">{escape(title(lbl))}:</text>')
                parts.append(f'<text x="{x + 126:.1f}" y="{ry}" font-family="DM Sans,system-ui,sans-serif" font-size="12" fill="#3a3a3a">{escape(str(val))}</text>')
                ry += 20

    # Compact legend with shared style
    legend_x = pad + 8
    legend_w = canvas_w - 2 * pad - 16
    legend_h = 128
    legend_y = card_y + card_h + 10
    parts.append(f'<rect x="{legend_x}" y="{legend_y}" width="{legend_w}" height="{legend_h}" fill="#ffffff" stroke="#222" stroke-width="1"/>')
    parts.append(f'<text x="{legend_x + 10}" y="{legend_y + 16}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#111">{escape(title(tr("Legenda - praktische duiding", "Legend - practical interpretation")))}</text>')
    legend_lines = [
        tr("VAARA: weekritme en dagkwaliteit; gebruik dit voor dagplanning.", "VAARA: weekday rhythm and day quality; use this for daily planning."),
        tr("TITHI: maansfase-energie; helpt bij timing van actie versus rust.", "TITHI: lunar phase energy; helps time action versus recovery."),
        tr("NAKSHATRA: emotioneel/mentaal veld; toont hoe je ervaringen verwerkt.", "NAKSHATRA: emotional/mental field; shows how you process experience."),
        tr("YOGA: combinatiekracht zon+maan; duidt algemene flow of frictie.", "YOGA: combined Sun+Moon force; indicates overall flow or friction."),
        tr("KARANA: praktische uitvoeringsmodus; goed voor concrete dagkeuzes.", "KARANA: practical execution mode; useful for concrete daily choices."),
    ]
    ly = legend_y + 36
    for line in legend_lines:
        parts.append(f'<line x1="{legend_x + 10}" y1="{ly - 4}" x2="{legend_x + 24}" y2="{ly - 4}" stroke="#111" stroke-width="1.4"/>')
        parts.append(f'<text x="{legend_x + 30}" y="{ly}" font-family="DM Sans,system-ui,sans-serif" font-size="12" fill="#222">{escape(line)}</text>')
        ly += 18

    parts.append("</svg>")
    return "\n".join(parts)


def render_bazi_banner_svg(
    engine_json: dict[str, Any],
    width: int = 900,
    height: int = 260,
    *,
    locale: str = "nl-NL",
) -> str:
    """Four pillars (Ganzhi) from chinese.bazi_pillars."""
    bazi = (engine_json.get("chinese") or {}).get("bazi_pillars")
    if not bazi or not isinstance(bazi, dict):
        return _svg_text_banner("BaZi · Ganzhi", [("Status", "niet beschikbaar voor deze invoer")], width, height)
    canvas_w = max(width, 1240)
    canvas_h = max(height, 820)
    main_x = 16
    main_y = 16
    main_w = int(canvas_w * 0.72)
    main_h = canvas_h - 32
    side_gap = 12
    side_x = main_x + main_w + side_gap
    side_w = canvas_w - side_x - 16
    side_y = main_y
    side_h = main_h

    lang = (locale or "nl-NL").lower()
    is_en = lang.startswith("en")

    def tr(nl: str, en: str) -> str:
        return en if is_en else nl

    columns = [
        (tr("Uur", "Hour"), "hour"),
        (tr("Dag", "Day"), "day"),
        (tr("Maand", "Month"), "month"),
        (tr("Jaar", "Year"), "year"),
    ]

    def _pillar(key: str) -> Dict[str, str]:
        p = bazi.get(key) or {}
        if not isinstance(p, dict):
            return {"stem": "", "branch": ""}
        return {"stem": str(p.get("stem") or ""), "branch": str(p.get("branch") or "")}

    def _stem_display(stem: str) -> Tuple[str, str, str]:
        meta = STEM_META.get(stem) or {}
        element_nl = meta.get("element_nl", "")
        element_en = meta.get("element_en", "")
        element = element_en if is_en else element_nl
        return (
            meta.get("hanzi", "—"),
            f'{meta.get("name_ascii", stem)} ({meta.get("hanzi", "—")})' if stem else "—",
            f'{meta.get("yin_yang", "")} {element}'.strip() or "—",
        )

    def _branch_display(branch: str) -> Tuple[str, str, str]:
        meta = BRANCH_META.get(branch) or {}
        animal_nl = meta.get("animal_nl", "")
        animal_en = meta.get("animal_en", "")
        element_nl = meta.get("element_nl", "")
        element_en = meta.get("element_en", "")
        animal = animal_en if is_en else animal_nl
        element = element_en if is_en else element_nl
        return (
            meta.get("hanzi", "—"),
            f'{meta.get("name_ascii", branch)} ({meta.get("hanzi", "—")}) - {animal}'.strip() if branch else "—",
            f'{meta.get("yin_yang", "")} {element}'.strip() or "—",
        )

    def _hidden_stems(branch: str) -> str:
        stems = HIDDEN_STEMS_BY_BRANCH.get(branch) or []
        if not stems:
            return "—"
        parts: List[str] = []
        for s in stems:
            stem_meta = STEM_META.get(s) or {}
            hanzi = stem_meta.get("hanzi", "")
            ascii_name = stem_meta.get("name_ascii", s)
            parts.append(f"{ascii_name} ({hanzi})" if hanzi else ascii_name)
        return " | ".join(parts)

    def _stem_element(stem: str) -> str:
        meta = STEM_META.get(stem) or {}
        return str(meta.get("element_nl") or "")

    def _branch_element(branch: str) -> str:
        meta = BRANCH_META.get(branch) or {}
        return str(meta.get("element_nl") or "")

    row_h = 120
    header_h = 44
    row_label_w = 176
    col_w = (main_w - row_label_w) / 4.0
    table_top = main_y + 54

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">',
        f'<rect width="{canvas_w}" height="{canvas_h}" fill="#ffffff"/>',
        f'<rect x="{main_x}" y="{main_y}" width="{main_w}" height="{main_h}" fill="#ffffff" stroke="#d7c7eb" stroke-width="1"/>',
        f'<rect x="{side_x}" y="{side_y}" width="{side_w}" height="{side_h}" fill="#ffffff" stroke="#d7c7eb" stroke-width="1"/>',
        f'<rect x="{main_x}" y="{main_y}" width="{main_w}" height="32" fill="#884dc9"/>',
        f'<rect x="{side_x}" y="{side_y}" width="{side_w}" height="32" fill="#884dc9"/>',
        f'<text x="{main_x + 14}" y="{main_y + 22}" font-family="Lora,Georgia,serif" font-size="15" fill="#ffffff">{escape(tr("BaZi-overzicht (traditionele opzet)", "BaZi overview (traditional layout)"))}</text>',
        f'<text x="{side_x + 12}" y="{side_y + 22}" font-family="Lora,Georgia,serif" font-size="15" fill="#ffffff">{escape(tr("Bestemmingsanalyse", "Destiny analysis"))}</text>',
    ]

    # Header row
    parts.append(f'<rect x="{main_x + row_label_w}" y="{table_top}" width="{main_w - row_label_w}" height="{header_h}" fill="#f5eefc"/>')
    for i, (label, _) in enumerate(columns):
        x = main_x + row_label_w + i * col_w
        parts.append(f'<line x1="{x}" y1="{table_top}" x2="{x}" y2="{table_top + header_h + row_h * 3}" stroke="#c7d0d8" stroke-width="1"/>')
        parts.append(
            f'<text x="{x + col_w / 2:.1f}" y="{table_top + 28}" font-family="DM Sans,system-ui,sans-serif" font-size="13" font-weight="700" text-anchor="middle" fill="#3a3a3a">{escape(label)}</text>'
        )
    parts.append(f'<line x1="{main_x + main_w}" y1="{table_top}" x2="{main_x + main_w}" y2="{table_top + header_h + row_h * 3}" stroke="#c7d0d8" stroke-width="1"/>')

    row_labels = [
        tr("Hemelstam", "Heavenly Stem"),
        tr("Aardetak", "Earthly Branch"),
        tr("Verborgen stammen", "Hidden stems"),
    ]
    for ridx, row_label in enumerate(row_labels):
        y = table_top + header_h + ridx * row_h
        parts.append(f'<rect x="{main_x}" y="{y}" width="{row_label_w}" height="{row_h}" fill="#fbf8ff"/>')
        parts.append(
            f'<text x="{main_x + 12}" y="{y + 26}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#3a3a3a">{escape(row_label)}</text>'
        )
        parts.append(f'<line x1="{main_x}" y1="{y}" x2="{main_x + main_w}" y2="{y}" stroke="#c7d0d8" stroke-width="1"/>')
    parts.append(f'<line x1="{main_x}" y1="{table_top + header_h + row_h * 3}" x2="{main_x + main_w}" y2="{table_top + header_h + row_h * 3}" stroke="#c7d0d8" stroke-width="1"/>')

    for i, (_, key) in enumerate(columns):
        p = _pillar(key)
        stem = p["stem"]
        branch = p["branch"]
        x = main_x + row_label_w + i * col_w

        stem_hanzi, stem_pinyin, stem_meta = _stem_display(stem)
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{table_top + header_h + 42}" font-family="Lora,Georgia,serif" font-size="56" text-anchor="middle" fill="#884dc9">{escape(stem_hanzi)}</text>')
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{table_top + header_h + 66}" font-family="DM Sans,system-ui,sans-serif" font-size="12" text-anchor="middle" fill="#3a3a3a">{escape(stem_pinyin)}</text>')
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{table_top + header_h + 86}" font-family="DM Sans,system-ui,sans-serif" font-size="12" text-anchor="middle" fill="#6f6f6f">{escape(stem_meta)}</text>')

        branch_hanzi, branch_animal, branch_meta = _branch_display(branch)
        by = table_top + header_h + row_h
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{by + 42}" font-family="Lora,Georgia,serif" font-size="56" text-anchor="middle" fill="#c9a24d">{escape(branch_hanzi)}</text>')
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{by + 66}" font-family="DM Sans,system-ui,sans-serif" font-size="12" text-anchor="middle" fill="#3a3a3a">{escape(branch_animal)}</text>')
        parts.append(f'<text x="{x + col_w/2:.1f}" y="{by + 86}" font-family="DM Sans,system-ui,sans-serif" font-size="12" text-anchor="middle" fill="#6f6f6f">{escape(branch_meta)}</text>')

        hy = table_top + header_h + row_h * 2
        hidden = _hidden_stems(branch)
        parts.append(f'<text x="{x + 8}" y="{hy + 30}" font-family="DM Sans,system-ui,sans-serif" font-size="11" fill="#3a3a3a">{escape(hidden)}</text>')

    # Destiny analysis panel
    day = _pillar("day")
    dm_stem = day["stem"]
    dm_hanzi, dm_pinyin, dm_meta = _stem_display(dm_stem)
    parts.append(f'<text x="{side_x + 12}" y="{side_y + 58}" font-family="DM Sans,system-ui,sans-serif" font-size="13" font-weight="700" fill="#3a3a3a">{escape(tr("Dagmeester", "Day Master"))}</text>')
    parts.append(f'<rect x="{side_x + 10}" y="{side_y + 68}" width="{side_w - 20}" height="70" fill="#f5eefc" stroke="#d7c7eb" stroke-width="1"/>')
    parts.append(f'<text x="{side_x + 18}" y="{side_y + 104}" font-family="Lora,Georgia,serif" font-size="34" fill="#884dc9">{escape(dm_hanzi)}</text>')
    parts.append(f'<text x="{side_x + 60}" y="{side_y + 100}" font-family="DM Sans,system-ui,sans-serif" font-size="13" fill="#3a3a3a">{escape(dm_pinyin)}</text>')
    parts.append(f'<text x="{side_x + 60}" y="{side_y + 121}" font-family="DM Sans,system-ui,sans-serif" font-size="12" fill="#6f6f6f">{escape(dm_meta)}</text>')

    # Traits + explicit source pillar
    list_y = side_y + 170
    for label_nl, label_en, key in [
        ("Edelman", "Nobleman", "year"),
        ("Intelligentie", "Intelligence", "month"),
        ("Perzikbloesem", "Peach Blossom", "hour"),
    ]:
        p = _pillar(key)
        branch = p["branch"]
        bmeta = BRANCH_META.get(branch) or {}
        animal = bmeta.get("animal_en", "") if is_en else bmeta.get("animal_nl", "")
        text = f'{bmeta.get("name_ascii", branch or "—")} ({bmeta.get("hanzi", "—")}) {animal}'.strip()
        source = tr(f"bron: {columns[[c[1] for c in columns].index(key)][0]}", f"source: {columns[[c[1] for c in columns].index(key)][0]}")
        parts.append(f'<text x="{side_x + 12}" y="{list_y}" font-family="DM Sans,system-ui,sans-serif" font-size="12" fill="#3a3a3a">{escape(tr(label_nl, label_en))}</text>')
        parts.append(f'<text x="{side_x + 160}" y="{list_y}" font-family="DM Sans,system-ui,sans-serif" font-size="12" fill="#3a3a3a">{escape(text)}</text>')
        parts.append(f'<text x="{side_x + 160}" y="{list_y + 13}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(source)}</text>')
        list_y += 36

    # Determining values (inputs + rules), including birth year -> year animal.
    birth = ((engine_json.get("input") or {}).get("birth") or {})
    birth_date = str(birth.get("date") or "—")
    birth_time = str(birth.get("time_local") or "—")
    birth_year = birth_date[:4] if len(birth_date) >= 4 and birth_date[:4].isdigit() else "—"
    chinese_block = engine_json.get("chinese") or {}
    boundary_settings = chinese_block.get("boundary_settings") or {}
    year_boundary = str(boundary_settings.get("year") or chinese_block.get("boundary_year") or "—")
    day_boundary = str(boundary_settings.get("day") or chinese_block.get("calendar_day_definition") or "—")
    cal_tz = str(boundary_settings.get("timezone_for_calendar") or "—")
    year_pillar = _pillar("year")
    year_branch_meta = BRANCH_META.get(year_pillar.get("branch", "")) or {}
    year_animal = year_branch_meta.get("animal_en", "") if is_en else year_branch_meta.get("animal_nl", "")
    year_branch_label = f'{year_branch_meta.get("name_ascii", year_pillar.get("branch", "—"))} ({year_branch_meta.get("hanzi", "—")})'

    det_title_y = list_y + 6
    parts.append(f'<line x1="{side_x + 10}" y1="{det_title_y - 12}" x2="{side_x + side_w - 10}" y2="{det_title_y - 12}" stroke="#d7c7eb" stroke-width="1"/>')
    parts.append(f'<text x="{side_x + 12}" y="{det_title_y}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#3a3a3a">{escape(tr("Bepalende waarden", "Determining values"))}</text>')

    det_items = [
        (tr("Geboortedatum", "Birth date"), birth_date),
        (tr("Geboortetijd", "Birth time"), birth_time),
        (tr("Geboortejaar", "Birth year"), birth_year),
        (tr("Jaarpilaar", "Year pillar"), f'{year_pillar.get("stem", "—")} / {year_branch_label}'),
        (tr("Jaardier uit geboortejaar", "Year animal from birth year"), year_animal or "—"),
        (tr("Jaarrandregel", "Year boundary rule"), year_boundary),
        (tr("Daggrensregel", "Day boundary rule"), day_boundary),
        (tr("Kalender-tijdzone", "Calendar timezone"), cal_tz),
    ]
    det_y = det_title_y + 16
    for lbl, val in det_items:
        parts.append(f'<text x="{side_x + 12}" y="{det_y}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(lbl)}:</text>')
        parts.append(f'<text x="{side_x + 150}" y="{det_y}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#3a3a3a">{escape(str(val))}</text>')
        det_y += 14

    # Simple rule flow for transparency
    flow_y = det_y + 10
    flow_text = tr(
        "Regelstroom: geboortejaar + jaarrandregel -> jaarpilaar -> jaardier",
        "Rule flow: birth year + year boundary rule -> year pillar -> year animal",
    )
    parts.append(f'<line x1="{side_x + 10}" y1="{flow_y - 12}" x2="{side_x + side_w - 10}" y2="{flow_y - 12}" stroke="#d7c7eb" stroke-width="1"/>')
    parts.append(f'<text x="{side_x + 12}" y="{flow_y}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(flow_text)}</text>')

    # Main panel dashboard blocks below the table.
    p_year = _pillar("year")
    p_month = _pillar("month")
    p_day = _pillar("day")
    p_hour = _pillar("hour")
    all_pillars = [p_year, p_month, p_day, p_hour]
    element_counts = {"Hout": 0, "Vuur": 0, "Aarde": 0, "Metaal": 0, "Water": 0}
    for p in all_pillars:
        se = _stem_element(p.get("stem", ""))
        if se in element_counts:
            element_counts[se] += 1
        be = _branch_element(p.get("branch", ""))
        if be in element_counts:
            element_counts[be] += 1
        for hs in HIDDEN_STEMS_BY_BRANCH.get(p.get("branch", ""), []):
            he = _stem_element(hs)
            if he in element_counts:
                element_counts[he] += 1

    bottom_y = table_top + header_h + row_h * 3 + 16
    block_h = main_y + main_h - bottom_y - 14
    block_w = (main_w - 26) / 2.0
    left_block_x = main_x + 8
    right_block_x = left_block_x + block_w + 10

    parts.append(f'<rect x="{left_block_x}" y="{bottom_y}" width="{block_w:.1f}" height="{block_h}" fill="#fbf8ff" stroke="#d7c7eb" stroke-width="1"/>')
    parts.append(f'<rect x="{right_block_x:.1f}" y="{bottom_y}" width="{block_w:.1f}" height="{block_h}" fill="#fffdfa" stroke="#e7d9be" stroke-width="1"/>')

    # Left block: how to read
    parts.append(f'<text x="{left_block_x + 10}" y="{bottom_y + 18}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#3a3a3a">{escape(tr("Leeswijzer", "How to read"))}</text>')
    guide_lines = [
        tr("Jaar: achtergrond, familie en vroege imprint.", "Year: background, family, early imprint."),
        tr("Maand: werk, omgeving en maatschappelijke rol.", "Month: work, environment, social role."),
        tr("Dag: kernidentiteit en relaties (Dagmeester).", "Day: core identity and relationships (Day Master)."),
        tr("Uur: innerlijke drijfveren en latere levensfase.", "Hour: inner drives and later-life themes."),
        tr("Hidden stems tonen extra, minder zichtbare invloeden.", "Hidden stems show additional less-visible influences."),
    ]
    gy = bottom_y + 36
    for line in guide_lines:
        parts.append(f'<text x="{left_block_x + 10}" y="{gy}" font-family="DM Sans,system-ui,sans-serif" font-size="11" fill="#3a3a3a">{escape(line)}</text>')
        gy += 20

    # Right block: element distribution dashboard
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{bottom_y + 18}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#3a3a3a">{escape(tr("Elementenoverzicht", "Element overview"))}</text>')
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{bottom_y + 34}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(tr("Telling op basis van stams + takken + verborgen stammen", "Count based on stems + branches + hidden stems"))}</text>')
    ey = bottom_y + 58
    for el in ["Hout", "Vuur", "Aarde", "Metaal", "Water"]:
        count = element_counts.get(el, 0)
        el_label = el if not is_en else {
            "Hout": "Wood",
            "Vuur": "Fire",
            "Aarde": "Earth",
            "Metaal": "Metal",
            "Water": "Water",
        }.get(el, el)
        bar_w = min(180, count * 18)
        parts.append(f'<text x="{right_block_x + 10:.1f}" y="{ey}" font-family="DM Sans,system-ui,sans-serif" font-size="11" fill="#3a3a3a">{escape(el_label)}</text>')
        parts.append(f'<rect x="{right_block_x + 82:.1f}" y="{ey - 9}" width="186" height="10" fill="#f1e9fb" stroke="#d7c7eb" stroke-width="1"/>')
        parts.append(f'<rect x="{right_block_x + 82:.1f}" y="{ey - 9}" width="{bar_w}" height="10" fill="#884dc9"/>')
        parts.append(f'<text x="{right_block_x + 274:.1f}" y="{ey}" font-family="DM Sans,system-ui,sans-serif" font-size="11" fill="#3a3a3a">{count}</text>')
        ey += 24

    # Practical interpretation block
    practical_y = ey + 10
    sorted_elements = sorted(element_counts.items(), key=lambda kv: kv[1], reverse=True)
    dominant_el, dominant_count = sorted_elements[0]
    weakest_el, weakest_count = sorted_elements[-1]
    tie_top = len(sorted_elements) > 1 and sorted_elements[1][1] == dominant_count
    tie_low = len(sorted_elements) > 1 and sorted_elements[-2][1] == weakest_count

    en_name = {
        "Hout": "Wood",
        "Vuur": "Fire",
        "Aarde": "Earth",
        "Metaal": "Metal",
        "Water": "Water",
    }

    def _el_label(nl_name: str) -> str:
        return en_name.get(nl_name, nl_name) if is_en else nl_name

    def _advice_for(nl_name: str) -> str:
        if is_en:
            mapping = {
                "Hout": "Use growth routines: planning, movement, and clear weekly goals.",
                "Vuur": "Express outward: social contact, visibility, and creative output.",
                "Aarde": "Stabilize with rhythm: regular meals, sleep, and grounding routines.",
                "Metaal": "Create structure: simplify, prioritize, and set clear boundaries.",
                "Water": "Deepen recovery: rest, reflection, and strategic pacing.",
            }
        else:
            mapping = {
                "Hout": "Gebruik groeiroutines: plannen, beweging en duidelijke weekdoelen.",
                "Vuur": "Zoek expressie naar buiten: contact, zichtbaarheid en creatie.",
                "Aarde": "Stabiliseer met ritme: regelmaat in eten, slaap en basisroutines.",
                "Metaal": "Werk met structuur: versimpelen, prioriteren en duidelijke grenzen.",
                "Water": "Versterk herstel: rust, reflectie en slim doseren van energie.",
            }
        return mapping.get(nl_name, "")

    parts.append(f'<line x1="{right_block_x + 10:.1f}" y1="{practical_y - 12}" x2="{right_block_x + block_w - 10:.1f}" y2="{practical_y - 12}" stroke="#d7c7eb" stroke-width="1"/>')
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{practical_y}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#3a3a3a">{escape(tr("Praktische duiding", "Practical interpretation"))}</text>')

    dom_text = (
        tr("Dominant element", "Dominant element") + f": {_el_label(dominant_el)} ({dominant_count})"
        if not tie_top
        else tr("Dominante elementen (gelijk)", "Dominant elements (tie)") + f": {_el_label(dominant_el)} ({dominant_count})"
    )
    low_text = (
        tr("Zwakste element", "Weakest element") + f": {_el_label(weakest_el)} ({weakest_count})"
        if not tie_low
        else tr("Laagste elementen (gelijk)", "Lowest elements (tie)") + f": {_el_label(weakest_el)} ({weakest_count})"
    )
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{practical_y + 18}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#3a3a3a">{escape(dom_text)}</text>')
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{practical_y + 32}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#3a3a3a">{escape(low_text)}</text>')

    advice_dom = tr("Benut sterk punt", "Leverage strength") + ": " + _advice_for(dominant_el)
    advice_low = tr("Compenseer zwakker punt", "Compensate weaker point") + ": " + _advice_for(weakest_el)
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{practical_y + 50}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(advice_dom)}</text>')
    parts.append(f'<text x="{right_block_x + 10:.1f}" y="{practical_y + 64}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#6f6f6f">{escape(advice_low)}</text>')

    # Shared-style legend panel for BaZi
    lg_x = right_block_x + 10
    lg_w = block_w - 20
    lg_h = 112
    lg_y = bottom_y + block_h - lg_h - 10
    parts.append(f'<rect x="{lg_x:.1f}" y="{lg_y:.1f}" width="{lg_w:.1f}" height="{lg_h}" fill="#ffffff" stroke="#222" stroke-width="1"/>')
    parts.append(
        f'<text x="{lg_x + 10:.1f}" y="{lg_y + 16:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="12" font-weight="700" fill="#111">{escape(tr("LEGENDA", "LEGEND"))}</text>'
    )
    bazi_legend_rows = [
        (tr("HEMELSTAM", "HEAVENLY STEM"), tr("persoonlijke expressie", "personal expression"), "#884dc9"),
        (tr("AARDETAK", "EARTHLY BRANCH"), tr("context en omgeving", "context and environment"), "#c9a24d"),
        (tr("VERBORGEN STAMMEN", "HIDDEN STEMS"), tr("onderliggende invloeden", "underlying influences"), "#6f6f6f"),
        (tr("DAGMEESTER", "DAY MASTER"), tr("kernsignatuur", "core signature"), "#884dc9"),
    ]
    lgy = lg_y + 34
    for left, right, col in bazi_legend_rows:
        parts.append(f'<line x1="{lg_x + 10:.1f}" y1="{lgy - 4:.1f}" x2="{lg_x + 26:.1f}" y2="{lgy - 4:.1f}" stroke="{col}" stroke-width="2"/>')
        parts.append(f'<text x="{lg_x + 32:.1f}" y="{lgy:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#222">{escape(left)}</text>')
        parts.append(f'<text x="{lg_x + lg_w - 8:.1f}" y="{lgy:.1f}" font-family="DM Sans,system-ui,sans-serif" font-size="10" fill="#555" text-anchor="end">{escape(right)}</text>')
        lgy += 18

    parts.append(
        f'<text x="{side_x + 12}" y="{side_y + side_h - 8}" font-family="DM Sans,system-ui,sans-serif" font-size="9" fill="#6f6f6f">{escape(tr("BaZi: eigenschappen volgen uit pilaren + grensregels.", "BaZi: traits follow pillars + boundary rules."))}</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def render_section_svg(engine_json: dict[str, Any], section: str, *, locale: str = "nl-NL") -> str:
    """
    Single SVG for UI/PDF previews.
    section: western_tropical | western_sidereal | vedic_panchanga | chinese_bazi
    """
    s = (section or "").strip().lower()
    if s == "western_tropical":
        return render_wheel_from_engine(engine_json, method_id="western_tropical", size=520)
    if s == "western_sidereal":
        return render_wheel_from_engine(engine_json, method_id="western_sidereal", size=520)
    if s == "vedic_panchanga":
        return render_panchanga_banner_svg(engine_json, width=1240, height=920, locale=locale)
    if s == "chinese_bazi":
        return render_bazi_banner_svg(engine_json, width=1240, height=820, locale=locale)
    raise ValueError(f"unknown section: {section!r}")
