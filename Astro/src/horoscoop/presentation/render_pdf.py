"""
PDF report renderer using reportlab.
Sections: input summary, time scales, diagnostics, per-method tables + embedded wheel SVG.
"""
from __future__ import annotations

from io import BytesIO
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _para(text: str, style_name: str = "Normal") -> Paragraph:
    styles = getSampleStyleSheet()
    return Paragraph((text or "").replace("\n", "<br/>").replace("&", "&amp;"), styles[style_name])


def _table(data: list, col_widths: Optional[list] = None) -> Table:
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


def render_pdf(
    engine_json: dict[str, Any],
    view_model: Optional[dict[str, Any]] = None,
    template_id: str = "default_report",
) -> bytes:
    """
    Build PDF from engine JSON. Optionally pass pre-built view_model.
    No interpretative text; computed values only.
    """
    if view_model is None:
        from .view_model import build_view_model
        view_model = build_view_model(engine_json)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    meta = engine_json.get("meta", {})
    input_summary = view_model.get("input_summary", {})
    diagnostics = view_model.get("diagnostics", {})
    time_block = engine_json.get("time", {})

    # Title
    elements.append(_para("<b>Horoscoop – Computation Report</b>", "Title"))
    elements.append(Spacer(1, 6))
    version = meta.get("version", "onbekend")
    gen = meta.get("generated_at_utc", "")
    elements.append(_para(f"v{version} • gegenereerd: {gen[:19] if gen else 'onbekend'} UTC", "Normal"))
    elements.append(Spacer(1, 12))

    # Input summary
    elements.append(_para("<b>Input</b>", "Heading2"))
    comp = input_summary.get("completeness", {})
    rows = [
        ["Veld", "Waarde"],
        ["Datum", input_summary.get("birth_date", "niet opgegeven")],
        ["Tijd (lokaal)", input_summary.get("birth_time_local", "niet opgegeven")],
        ["Plaats", input_summary.get("place_label", "niet opgegeven")],
        ["Timezone", input_summary.get("timezone_label", "niet opgegeven")],
        ["has_date", str(comp.get("has_date"))],
        ["has_time", str(comp.get("has_time"))],
        ["has_location", str(comp.get("has_location"))],
        ["has_timezone", str(comp.get("has_timezone"))],
    ]
    elements.append(_table(rows))
    elements.append(Spacer(1, 12))

    # Time scales
    elements.append(_para("<b>Astronomie & tijd</b>", "Heading2"))
    jd = time_block.get("jd") or {}
    rows = [
        ["Veld", "Waarde"],
        ["datetime_utc", str(time_block.get("datetime_utc"))],
        ["JD(UT1)", f"{time_block.get('jd_ut1'):.6f}" if time_block.get("jd_ut1") is not None else "n.v.t."],
        ["JD(TT)", f"{time_block.get('jd_tt'):.6f}" if time_block.get("jd_tt") is not None else "n.v.t."],
        ["ΔT (s)", f"{time_block.get('delta_t_seconds'):.1f}" if time_block.get("delta_t_seconds") is not None else "n.v.t."],
        ["UT1−UTC (s)", str(time_block.get("ut1_utc_seconds"))],
        ["delta_t_source", str(time_block.get("delta_t_source"))],
        ["ut1_utc_source", str(time_block.get("ut1_utc_source"))],
    ]
    elements.append(_table(rows))
    elements.append(Spacer(1, 12))

    # Diagnostics
    elements.append(_para("<b>Diagnostics</b>", "Heading2"))
    codes = diagnostics.get("codes") or []
    warnings = diagnostics.get("warnings") or []
    elements.append(_para("Codes: " + ", ".join(codes), "Normal"))
    for w in warnings[:5]:
        if isinstance(w, dict):
            elements.append(_para(f"• {w.get('label_nl', w.get('code', ''))}", "Normal"))
    elements.append(_para(f"Vertrouwen: {diagnostics.get('confidence_overall', 'onbekend')}", "Normal"))
    elements.append(Spacer(1, 12))

    # Per method
    from .render_svg import render_wheel_from_engine

    for method in view_model.get("methods", []):
        mid = method.get("id", "")
        label = method.get("label_nl", mid)
        available = method.get("available", False)
        elements.append(_para(f"<b>{label}</b> ({'beschikbaar' if available else 'niet beschikbaar'})", "Heading2"))

        if not available:
            elements.append(_para("Methode niet berekend (zie requires).", "Normal"))
            elements.append(Spacer(1, 12))
            continue

        sections = method.get("sections") or {}
        # Planet table
        pt = sections.get("planet_table") or []
        if pt:
            rows = [["Lichaam", "Lon", "Teken", "Huis"]]
            for r in pt:
                rows.append([str(r.get("body", "")), str(r.get("lon", "")), str(r.get("sign", "")), str(r.get("house", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # Houses table
        ht = sections.get("houses_table") or []
        if ht:
            rows = [["Huis", "Cusp", "Teken"]]
            for r in ht:
                rows.append([str(r.get("house", "")), str(r.get("cusp", "")), str(r.get("sign", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # Aspect table
        at = sections.get("aspect_table") or []
        if at:
            rows = [["Paar", "Orb"]]
            for r in at:
                rows.append([str(r.get("pair", "")), str(r.get("orb", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # Panchanga cards
        pc = sections.get("panchanga_cards") or []
        if pc:
            rows = [["Component", "Waarde"]]
            for r in pc:
                rows.append([str(r.get("label", "")), str(r.get("value", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # End times
        et = sections.get("end_times") or []
        if et:
            rows = [["Event", "Tijd"]]
            for r in et:
                rows.append([str(r.get("label", "")), str(r.get("value", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # Pillars
        pt = sections.get("pillars_table") or []
        if pt:
            rows = [["Pilaar", "Stem", "Branch"]]
            for r in pt:
                rows.append([str(r.get("pillar", "")), str(r.get("stem", "")), str(r.get("branch", ""))])
            elements.append(_table(rows))
            elements.append(Spacer(1, 6))

        # Wheel SVG
        if mid in ("western_tropical", "western_sidereal"):
            try:
                svg_str = render_wheel_from_engine(engine_json, method_id=mid)
                if svg_str and "<svg" in svg_str:
                    try:
                        from reportlab.platypus import Image
                        try:
                            import cairosvg
                            png_io = BytesIO()
                            cairosvg.svg2png(bytestring=svg_str.encode("utf-8"), write_to=png_io)
                            png_io.seek(0)
                            img = Image(png_io, width=200, height=200)
                            elements.append(img)
                        except Exception:
                            elements.append(_para("[Wiel: SVG beschikbaar via /api/render/wheel.svg]", "Normal"))
                    except Exception:
                        elements.append(_para("[Wiel: zie /api/render/wheel.svg]", "Normal"))
            except Exception:
                elements.append(_para("[Wiel niet gerenderd]", "Normal"))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    return buffer.getvalue()
