from __future__ import annotations

from horoscoop.interpretations import build_interpretations
from horoscoop.method_explanations import build_method_explanations


def test_build_interpretations_includes_method_explanations():
    out = build_interpretations({"western": None}, locale="nl-NL")
    assert "method_explanations" in out
    me = out["method_explanations"]
    assert "_meta" in me
    for key in ("western_tropical", "vedic_panchanga", "chinese_ganzhi_bazi", "human_design", "maya"):
        assert key in me
        bundle = me[key]
        assert bundle.get("overview")
        assert isinstance(bundle.get("blocks"), list)
        assert len(bundle["blocks"]) >= 1


def test_western_bundle_splits_headline_and_personal():
    engine = {
        "western": {
            "placements": {
                "Sun": {"sign": "Pisces", "house": 9},
                "Moon": {"sign": "Capricorn", "house": 7},
                "Saturn": {"sign": "Capricorn", "house": 7},
            },
            "aspects": [],
            "houses": {"angles": {"asc_deg": 90.0}, "cusps_deg": []},
        }
    }
    bundle = build_method_explanations(engine, locale="nl-NL")["western_tropical"]
    ids = [b["id"] for b in bundle["blocks"]]
    assert "sun" in ids and "moon" in ids and "ascendant" in ids
    sun = next(b for b in bundle["blocks"] if b["id"] == "sun")
    assert sun["headline"].strip()
    assert sun["personal_layer"].startswith("Persoonlijk")
