from __future__ import annotations

from pathlib import Path

from horoscoop.presentation.astro_symbols import (
    get_astro_symbol,
    get_astro_symbol_or_fallback,
    get_symbol_path,
    resolve_astro_symbol_id,
)


def test_registry_contains_core_symbols():
    mars = get_astro_symbol("mars")
    assert mars is not None
    assert mars.svgPath.endswith("/shared/planets/mars.svg")

    aries = get_astro_symbol("aries")
    assert aries is not None
    assert aries.svgPath.endswith("/western/zodiac/aries.svg")

    bazi = get_astro_symbol("bazi-jia")
    assert bazi is not None
    assert bazi.label.lower().startswith("jia")

    hd = get_astro_symbol("hd-generator")
    assert hd is not None
    assert hd.svgPath.endswith("/human-design/types/generator.svg")


def test_resolver_core_inputs():
    assert resolve_astro_symbol_id("\u2642") == "mars"
    assert resolve_astro_symbol_id("Mars") == "mars"
    assert resolve_astro_symbol_id("\u2648") == "aries"
    assert resolve_astro_symbol_id("Ram") == "aries"
    assert resolve_astro_symbol_id("\u7532") == "bazi-jia"
    assert resolve_astro_symbol_id("Generator") == "hd-generator"


def test_get_symbol_path_and_fallback():
    assert get_symbol_path("mars")
    assert get_astro_symbol_or_fallback("does-not-exist").unicodeFallback == "?"


def test_no_hardcoded_glyphs_in_migrated_presentation_files():
    root = Path(__file__).resolve().parents[1] / "presentation"
    render_svg = (root / "render_svg.py").read_text(encoding="utf-8")
    view_model = (root / "view_model.py").read_text(encoding="utf-8")
    banned = [
        "\u2609", "\u263d", "\u263f", "\u2640", "\u2642", "\u2643", "\u2644",
        "\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d", "\u264e",
        "\u264f", "\u2650", "\u2651", "\u2652", "\u2653", "\u260c", "\u260d",
        "\u25b3", "\u25a1", "\u26b9",
    ]
    for symbol in banned:
        assert symbol not in render_svg
        assert symbol not in view_model


def _extract_block(source: str, marker: str) -> str:
    start = source.find(marker)
    assert start >= 0, f"Missing marker: {marker}"
    next_fn = source.find("\n      function ", start + len(marker))
    return source[start:] if next_fn < 0 else source[start:next_fn]


def test_template_render_blocks_use_iconset_paths():
    template = (Path(__file__).resolve().parents[3] / "app" / "templates" / "index.html").read_text(encoding="utf-8")
    assert "const ASTRO_ICON_BASE = \"/static/icons/astro\"" in template
    assert "function iconPathById(symbolId)" in template

    banned = [
        "\u2609", "\u263d", "\u263f", "\u2640", "\u2642", "\u2643", "\u2644",
        "\u2648", "\u2649", "\u264a", "\u264b", "\u264c", "\u264d", "\u264e",
        "\u264f", "\u2650", "\u2651", "\u2652", "\u2653", "\u260c", "\u260d",
        "\u25b3", "\u25a1", "\u26b9",
    ]
    guarded_blocks = [
        "function createMethodTable(headers, rows) {",
        "function getWesternWheelSvg(data, options) {",
        "function createKundaliGrid(activeVargaId, data) {",
        "function appendVedicGlossaryLegend(frag) {",
        "function appendWesternGlossaryLegend(frag) {",
    ]
    for marker in guarded_blocks:
        block = _extract_block(template, marker)
        assert "iconPathById(" in block or "symbolCell(" in block
        for symbol in banned:
            assert symbol not in block
