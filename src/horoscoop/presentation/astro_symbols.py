from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
import re
from typing import Any, Literal, Optional

AstroSymbolMethod = Literal["shared", "western", "vedic", "bazi", "maya", "human_design"]
AstroSymbolCategory = Literal[
    "planet",
    "graha",
    "zodiac_sign",
    "element",
    "modality",
    "house",
    "aspect",
    "point",
    "nakshatra",
    "varga",
    "dasha",
    "panchanga",
    "bazi_stem",
    "bazi_branch",
    "ten_god",
    "bazi_interaction",
    "maya_day_sign",
    "maya_tone",
    "maya_month",
    "maya_calendar",
    "human_design_type",
    "human_design_authority",
    "human_design_center",
    "human_design_gate",
    "human_design_channel",
    "human_design_profile_line",
    "human_design_definition",
    "chart_type",
    "general",
]


@dataclass(frozen=True)
class AstroSymbolDefinition:
    id: str
    method: AstroSymbolMethod
    category: AstroSymbolCategory
    label: str
    svgPath: str
    accessibilityLabel: str
    labelNl: Optional[str] = None
    labelEn: Optional[str] = None
    alternativeNames: tuple[str, ...] = field(default_factory=tuple)
    unicodeFallback: Optional[str] = None
    color: Optional[str] = None
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    element: Optional[str] = None
    polarity: Optional[Literal["yin", "yang", "active", "receptive", "neutral"]] = None
    modality: Optional[str] = None
    keywords: tuple[str, ...] = field(default_factory=tuple)
    shortDescription: Optional[str] = None
    longDescription: Optional[str] = None


_ICON_ROOT = Path(__file__).resolve().parents[3] / "app" / "static" / "icons" / "astro"
_SVG_OPEN_RE = re.compile(r"<svg[^>]*>", re.IGNORECASE)
_VIEWBOX_RE = re.compile(r'viewBox="([^"]+)"')

_UNICODE_ALIASES: dict[str, str] = {
    "\u2609": "sun",
    "\u263d": "moon",
    "\u263f": "mercury",
    "\u2640": "venus",
    "\u2642": "mars",
    "\u2643": "jupiter",
    "\u2644": "saturn",
    "\u2645": "uranus",
    "\u2646": "neptune",
    "\u2647": "pluto",
    "\u260a": "north-node",
    "\u260b": "south-node",
    "\u2648": "aries",
    "\u2649": "taurus",
    "\u264a": "gemini",
    "\u264b": "cancer",
    "\u264c": "leo",
    "\u264d": "virgo",
    "\u264e": "libra",
    "\u264f": "scorpio",
    "\u2650": "sagittarius",
    "\u2651": "capricorn",
    "\u2652": "aquarius",
    "\u2653": "pisces",
    "\u260c": "conjunction",
    "\u260d": "opposition",
    "\u25b3": "trine",
    "\u25a1": "square",
    "\u2736": "sextile",
    "\u26b9": "sextile",
    "\u26bb": "quincunx",
    "\u7532": "bazi-jia",
}

_NORMALIZED_ALIASES: dict[str, str] = {
    "mars": "mars",
    "mangala": "mars",
    "venus": "venus",
    "sun": "sun",
    "moon": "moon",
    "ram": "aries",
    "aries": "aries",
    "jia": "bazi-jia",
    "generator": "hd-generator",
    "emotional authority": "hd-emotional-authority",
}


def _slug(s: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return out


def _method_from_folder(folder: str) -> AstroSymbolMethod:
    if folder == "human-design":
        return "human_design"
    return folder.replace("-", "_")  # type: ignore[return-value]


def _category_for(method: AstroSymbolMethod, group: str) -> AstroSymbolCategory:
    m = {
        ("shared", "planets"): "planet",
        ("shared", "points"): "point",
        ("shared", "elements"): "element",
        ("western", "zodiac"): "zodiac_sign",
        ("western", "aspects"): "aspect",
        ("western", "houses"): "house",
        ("western", "modalities"): "modality",
        ("vedic", "nakshatras"): "nakshatra",
        ("vedic", "vargas"): "varga",
        ("vedic", "dasha"): "dasha",
        ("vedic", "panchanga"): "panchanga",
        ("bazi", "stems"): "bazi_stem",
        ("bazi", "branches"): "bazi_branch",
        ("bazi", "ten-gods"): "ten_god",
        ("bazi", "general"): "bazi_interaction",
        ("maya", "tzolkin"): "maya_day_sign",
        ("maya", "tones"): "maya_tone",
        ("maya", "haab"): "maya_month",
        ("maya", "general"): "maya_calendar",
        ("human_design", "types"): "human_design_type",
        ("human_design", "authorities"): "human_design_authority",
        ("human_design", "centers"): "human_design_center",
        ("human_design", "gates"): "human_design_gate",
        ("human_design", "profile-lines"): "human_design_profile_line",
        ("human_design", "general"): "human_design_definition",
    }
    return m.get((method, group), "general")


def _id_for(method: AstroSymbolMethod, group: str, stem: str) -> str:
    if method == "bazi" and group == "stems":
        return f"bazi-{stem}"
    if method == "bazi" and group == "branches":
        return f"bazi-{stem}"
    if method == "human_design" and group == "types":
        return f"hd-{stem}"
    if method == "human_design" and group == "authorities":
        return f"hd-{stem}-authority"
    if method == "human_design" and group == "centers":
        return f"hd-{stem}-center"
    if method == "human_design" and group == "gates":
        return f"hd-{stem}"
    if method == "human_design" and group == "profile-lines":
        return f"hd-{stem}"
    if method == "human_design" and group == "general":
        return f"hd-{stem}"
    if method == "maya" and group == "tzolkin":
        return f"maya-{stem}"
    if method == "maya" and group == "tones":
        return f"maya-{stem}"
    if method == "maya" and group == "haab":
        return f"maya-haab-{stem}"
    return stem


@lru_cache(maxsize=1)
def _registry() -> dict[str, AstroSymbolDefinition]:
    out: dict[str, AstroSymbolDefinition] = {}
    if not _ICON_ROOT.is_dir():
        return out
    for file in sorted(_ICON_ROOT.glob("*/*/*.svg")):
        rel = file.relative_to(_ICON_ROOT).as_posix()
        parts = rel.split("/")
        method = _method_from_folder(parts[0])
        group = parts[1]
        stem = _slug(file.stem)
        symbol_id = _id_for(method, group, stem)
        category = _category_for(method, group)
        label = file.stem.replace("-", " ").title()
        out[symbol_id] = AstroSymbolDefinition(
            id=symbol_id,
            method=method,
            category=category,
            label=label,
            labelNl=label,
            labelEn=label,
            svgPath=f"/static/icons/astro/{rel}",
            accessibilityLabel=label,
            alternativeNames=tuple({label.lower(), stem.replace("-", " ")}),
            unicodeFallback=None,
        )
    for k, v in _UNICODE_ALIASES.items():
        if v in out:
            base = out[v]
            out[v] = AstroSymbolDefinition(**{**base.__dict__, "unicodeFallback": k})
    return out


_FALLBACK = AstroSymbolDefinition(
    id="unknown",
    method="shared",
    category="general",
    label="Unknown Symbol",
    svgPath="",
    accessibilityLabel="Unknown symbol",
    unicodeFallback="?",
)


def get_astro_symbol(symbol_id: str) -> Optional[AstroSymbolDefinition]:
    return _registry().get(symbol_id)


def get_astro_symbol_or_fallback(symbol_id: str) -> AstroSymbolDefinition:
    return get_astro_symbol(symbol_id) or _FALLBACK


def get_astro_symbols_by_method(method: AstroSymbolMethod) -> list[AstroSymbolDefinition]:
    return [s for s in _registry().values() if s.method == method]


def get_astro_symbols_by_category(category: AstroSymbolCategory) -> list[AstroSymbolDefinition]:
    return [s for s in _registry().values() if s.category == category]


def get_symbol_color(symbol_id: str) -> Optional[str]:
    sym = get_astro_symbol(symbol_id)
    return sym.color if sym else None


def get_symbol_label(symbol_id: str, language: Literal["nl", "en"] = "nl") -> str:
    sym = get_astro_symbol_or_fallback(symbol_id)
    if language == "en":
        return sym.labelEn or sym.label
    return sym.labelNl or sym.label


def get_symbol_path(symbol_id: str) -> Optional[str]:
    sym = get_astro_symbol(symbol_id)
    return sym.svgPath if sym else None


def resolve_astro_symbol_id(
    input_value: str,
    context: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    if not input_value:
        return None
    if input_value in _UNICODE_ALIASES:
        return _UNICODE_ALIASES[input_value]
    raw = input_value.strip().lower()
    if raw in _NORMALIZED_ALIASES:
        return _NORMALIZED_ALIASES[raw]
    slug = _slug(raw)
    if slug in _NORMALIZED_ALIASES:
        return _NORMALIZED_ALIASES[slug]
    reg = _registry()
    if slug in reg:
        return slug
    method = (context or {}).get("method")
    category = (context or {}).get("category")
    for sym in reg.values():
        if method and sym.method != method:
            continue
        if category and sym.category != category:
            continue
        names = {sym.id, sym.label.lower(), *(sym.alternativeNames or ())}
        if raw in names or slug in {_slug(n) for n in names}:
            return sym.id
    return None


@lru_cache(maxsize=512)
def get_inline_svg_payload(symbol_id: str) -> Optional[tuple[str, str]]:
    symbol = get_astro_symbol(symbol_id)
    if not symbol or not symbol.svgPath:
        return None
    file_path = _ICON_ROOT / Path(symbol.svgPath.replace("/static/icons/astro/", ""))
    if not file_path.is_file():
        return None
    raw = file_path.read_text(encoding="utf-8")
    open_match = _SVG_OPEN_RE.search(raw)
    if not open_match:
        return None
    viewbox_match = _VIEWBOX_RE.search(open_match.group(0))
    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 24 24"
    inner = raw[open_match.end() :]
    inner = inner.rsplit("</svg>", 1)[0].strip()
    return (viewbox, inner)
