"""
PDF report generation for horoscoop engine output.

Uses reportlab to render a simple, deterministic multi-section report:
- Meta / input
- Time and diagnostics
- Western
- Vedic
- Chinese / BaZi
"""
from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def _para(text: str, style_name: str = "Normal"):
    styles = getSampleStyleSheet()
    return Paragraph(text.replace("\n", "<br/>"), styles[style_name])


def _table(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return t


def build_pdf(horoscoop: Dict[str, Any]) -> bytes:
    """
    Build a PDF report from the horoscoop output dict.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    meta = horoscoop.get("meta", {})
    input_block = horoscoop.get("input", {})
    time_block = horoscoop.get("time", {})
    diagnostics = horoscoop.get("diagnostics", {}) or {}

    # Title
    elements.append(_para("<b>Horoscoop – Computation Report</b>", "Title"))
    elements.append(Spacer(1, 12))

    # Meta
    elements.append(_para("<b>Meta</b>", "Heading2"))
    engine = meta.get("engine", {})
    elements.append(
        _table(
            [
                ["Key", "Value"],
                ["Version", meta.get("version")],
                ["Generated at (UTC)", meta.get("generated_at_utc")],
                ["Ephemeris engine", engine.get("ephemeris_engine")],
                ["House engine", engine.get("house_engine")],
            ]
        )
    )
    elements.append(Spacer(1, 12))

    # Input
    elements.append(_para("<b>Input</b>", "Heading2"))
    birth = input_block.get("birth", {})
    tz = birth.get("timezone", {})
    place = birth.get("place", {})
    elements.append(
        _table(
            [
                ["Field", "Value"],
                ["Date", birth.get("date")],
                ["Time (local)", birth.get("time_local")],
                ["Latitude", place.get("lat")],
                ["Longitude", place.get("lon")],
                ["Elevation (m)", place.get("elevation_m")],
                ["Timezone IANA", tz.get("iana")],
                ["UTC offset (min)", tz.get("utc_offset_minutes")],
            ]
        )
    )
    elements.append(Spacer(1, 12))

    # Time / diagnostics
    elements.append(_para("<b>Time scales & diagnostics</b>", "Heading2"))
    rows = [
        ["Field", "Value"],
        ["datetime_utc", time_block.get("datetime_utc")],
        ["datetime_local", time_block.get("datetime_local")],
        ["jd_ut1", time_block.get("jd_ut1")],
        ["jd_tt", time_block.get("jd_tt")],
        ["delta_t_seconds", time_block.get("delta_t_seconds")],
        ["delta_t_source", time_block.get("delta_t_source")],
        ["ut1_utc_seconds", time_block.get("ut1_utc_seconds")],
        ["ut1_utc_source", time_block.get("ut1_utc_source")],
    ]
    elements.append(_table(rows))
    elements.append(Spacer(1, 6))
    codes = diagnostics.get("codes") or []
    elements.append(_para("<b>Diagnostics codes:</b> " + ", ".join(codes)))
    elements.append(Spacer(1, 12))

    # Western
    western = horoscoop.get("western") or {}
    elements.append(_para("<b>Western (tropical)</b>", "Heading2"))
    houses = (western.get("houses") or {}).get("cusps_deg") or []
    aspects_block = western.get("aspects") or []
    if houses:
        data = [["House", "Cusp (deg)"]] + [[str(i + 1), f"{h:.4f}"] for i, h in enumerate(houses)]
        elements.append(_table(data))
        elements.append(Spacer(1, 6))
    if aspects_block:
        asp_rows = [["A", "B", "Type", "Exact (deg)", "Orb (deg)", "Applying"]]
        for a in aspects_block:
            asp_rows.append(
                [
                    a.get("a"),
                    a.get("b"),
                    a.get("type"),
                    f"{a.get('exact_angle_deg', 0.0):.4f}",
                    f"{a.get('orb_deg', 0.0):.4f}",
                    str(a.get("applying")),
                ]
            )
        elements.append(_table(asp_rows))
    elements.append(Spacer(1, 12))

    # Vedic
    vedic = horoscoop.get("vedic") or {}
    panchanga = vedic.get("panchanga") or {}
    elements.append(_para("<b>Vedic Panchanga</b>", "Heading2"))
    if panchanga:
        t = panchanga.get("tithi") or {}
        n = panchanga.get("nakshatra") or {}
        y = panchanga.get("yoga") or {}
        k = panchanga.get("karana") or {}
        rows = [
            ["Component", "Index / Value"],
            ["Vaara", panchanga.get("vaara")],
            ["Tithi index", t.get("index")],
            ["Tithi ends at (local)", t.get("ends_at_local")],
            ["Nakshatra index", n.get("index")],
            ["Nakshatra ends at (local)", n.get("ends_at_local")],
            ["Yoga index", y.get("index")],
            ["Yoga ends at (local)", y.get("ends_at_local")],
            ["Karana indices", ", ".join(str(i) for i in (k.get("indices") or []))],
        ]
        elements.append(_table(rows))
    elements.append(Spacer(1, 12))

    # Chinese / BaZi
    chinese = horoscoop.get("chinese") or {}
    elements.append(_para("<b>Chinese / BaZi</b>", "Heading2"))
    if chinese:
        gz = (chinese.get("ganzhi") or {}).get("day") or {}
        bazi = chinese.get("bazi_pillars") or {}
        rows = [
            ["Field", "Value"],
            ["Boundary year mode", chinese.get("boundary_year")],
            ["Ganzhi day", f"{gz.get('stem')} {gz.get('branch')} ({gz.get('index_60')})"],
        ]
        elements.append(_table(rows))
        elements.append(Spacer(1, 6))
        if bazi:
            b_rows = [["Pillar", "Stem", "Branch"]]
            for key in ["year", "month", "day", "hour"]:
                p = bazi.get(key) or {}
                b_rows.append([key, p.get("stem"), p.get("branch")])
            elements.append(_table(b_rows))

    doc.build(elements)
    return buffer.getvalue()

