from __future__ import annotations

from horoscoop.interpretation import (
    build_interpretation_points,
    extract_resolved_values,
)


def _engine_output() -> dict:
    return {
        "western": {
            "placements": {
                "Sun": {"sign": "Sagittarius", "degree_in_sign": 12.5, "house": 9, "retrograde": False},
                "Moon": {"sign": "Cancer", "degree_in_sign": 5.0, "house": 4, "retrograde": False},
                "Venus": {"sign": "Taurus", "degree_in_sign": 1.0, "house": 2, "retrograde": False},
            },
            "angles": {
                "ascendant": {"sign": "Leo", "degree_in_sign": 2.0},
                "mc": {"sign": "Taurus", "degree_in_sign": 5.0},
            },
            "balance": {"elements": {"fire": 0.7, "earth": 0.1, "air": 0.1, "water": 0.1}},
            "aspects": [
                {"a": "Sun", "b": "Moon", "type": "square", "orb_deg": 3.0, "applying": True}
            ],
            "nodes": {
                "north": {"sign": "Aquarius", "house": 7},
                "south": {"sign": "Leo", "house": 1},
            },
        },
        "chinese": {"element_balance": {"fire": 0.7, "water": 0.1}},
    }


def test_extract_resolved_values_includes_planets():
    resolved = extract_resolved_values(_engine_output())
    assert resolved["western.planets.sun.sign"] == "Sagittarius"
    assert resolved["western.planets.sun.house"] == 9
    assert resolved["western.ascendant.sign"] == "Leo"


def test_build_planet_in_sign_in_house():
    points = build_interpretation_points(_engine_output())
    sun_point = next(
        p for p in points
        if p["formulaId"] == "western.planet_in_sign_in_house"
        and "Sun" in p["technicalLabel"]
    )
    assert "bewuste levensenergie" in sun_point["humanMeaning"]
    assert "boogschutter" in sun_point["humanMeaning"].lower() or "betekenis" in sun_point["humanMeaning"]
    assert sun_point["balancedExpression"]
    assert sun_point["shadowExpression"]
    assert sun_point["confidence"] in {"high", "medium"}
    assert "western.planet.sun" in sun_point["glossarySources"]
    assert "western.sign.sagittarius" in sun_point["glossarySources"]
    assert "western.house.9" in sun_point["glossarySources"]


def test_aspect_point_built():
    points = build_interpretation_points(_engine_output())
    aspect_points = [p for p in points if p["formulaId"] == "western.aspect_between_planets"]
    assert len(aspect_points) == 1
    asp = aspect_points[0]
    assert "Sun square Moon" in asp["technicalLabel"]
    assert "spanning" in asp["humanMeaning"].lower()


def test_ascendant_and_node_points():
    points = build_interpretation_points(_engine_output())
    asc = [p for p in points if p["formulaId"] == "western.ascendant_presentation"]
    assert len(asc) == 1
    nodes = [p for p in points if p["formulaId"] == "western.node_developmental_direction"]
    assert len(nodes) == 1


def test_element_balance_dominant_point():
    points = build_interpretation_points(_engine_output())
    elem = [p for p in points if p["formulaId"] == "western.element_balance_dominant"]
    assert len(elem) == 1
    assert "Vuur" in elem[0]["technicalLabel"]


def test_cross_method_overlap_when_both_high():
    points = build_interpretation_points(_engine_output())
    cross = [p for p in points if p["formulaId"] == "cross.element_overlap"]
    assert len(cross) >= 1
    assert "fire" in cross[0]["inputs"].get("element", "").lower()


def test_cross_decision_pattern_with_hd_and_moon():
    out = _engine_output()
    out["human_design"] = {"type": "Generator", "authority": "Sacral"}
    points = build_interpretation_points(out)
    dec = [p for p in points if p["formulaId"] == "cross.decision_pattern"]
    assert len(dec) == 1
    assert "Beslispatroon" in dec[0]["technicalLabel"]
    assert "responderen" in dec[0]["humanMeaning"].lower() or "generator" in dec[0]["humanMeaning"].lower()
    assert "maan" in dec[0]["humanMeaning"].lower()


def test_no_points_when_engine_output_empty():
    out = build_interpretation_points({})
    assert out == []
