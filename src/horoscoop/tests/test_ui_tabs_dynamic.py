from __future__ import annotations

from pathlib import Path


TEMPLATE_PATH = Path("app/templates/index.html")


def _template_text() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def test_method_tabs_use_dynamic_dashboard_data():
    txt = _template_text()
    assert 'function renderWesternTabV2(data)' in txt
    assert 'renderResultDashboard("western", data)' in txt

    assert 'function renderVedicTabV2(data)' in txt
    assert 'renderResultDashboard("vedic", data)' in txt

    assert 'function renderBaziTabV2(data)' in txt
    assert 'renderResultDashboard("bazi", data)' in txt


def test_no_static_demo_payloads_left_in_active_tabs():
    txt = _template_text()
    # Old static demo snippets that should not be present in active tabs.
    assert "Shukla Panchami" not in txt
    assert "Shravana, pada 4" not in txt
    assert "Day Master\", \"Yang Water" not in txt
    assert "\"Water\", \"34%\"" not in txt


def test_energy_tab_uses_live_energy_payload():
    txt = _template_text()
    assert "function renderEnergyTabV2(data, energy, combined)" in txt
    assert "const domains = Array.isArray(energy && energy.domains) ? energy.domains : [];" in txt
    assert "notes[0] || summary" in txt
