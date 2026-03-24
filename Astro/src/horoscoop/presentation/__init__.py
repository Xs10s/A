"""Presentation layer: engine JSON → ViewModel → web/PDF/SVG rendering."""

from .view_model import build_view_model
from .diagnostics import normalize_diagnostics
from .formatters import (
    format_degrees,
    format_orb,
    format_datetime_nl,
    sign_code_to_nl,
    BODY_LABELS_NL,
    SIGN_CODES,
)
from .template_registry import get_template, resolve_sections
from .render_svg import render_wheel_svg, render_wheel_from_engine
from .render_pdf import render_pdf

__all__ = [
    "build_view_model",
    "normalize_diagnostics",
    "format_degrees",
    "format_orb",
    "format_datetime_nl",
    "sign_code_to_nl",
    "BODY_LABELS_NL",
    "SIGN_CODES",
    "get_template",
    "resolve_sections",
    "render_wheel_svg",
    "render_wheel_from_engine",
    "render_pdf",
]
