from __future__ import annotations

from horoscoop.relationships import (
    RELATIONSHIP_MATRIX,
    evaluate_relationships,
)


def test_matrix_is_non_empty():
    assert len(RELATIONSHIP_MATRIX) > 0


def test_evaluate_same_element_match():
    out = evaluate_relationships(
        {
            "western.planets.sun.sign": "Aries",
            "western.planets.moon.sign": "Sagittarius",
        }
    )
    matched = {r.relationship_id: r.matched for r in out}
    assert matched["western_sun_moon_same_element"] is True


def test_evaluate_same_element_no_match():
    out = evaluate_relationships(
        {
            "western.planets.sun.sign": "Aries",
            "western.planets.moon.sign": "Cancer",
        }
    )
    matched = {r.relationship_id: r.matched for r in out}
    assert matched["western_sun_moon_same_element"] is False


def test_evaluate_polarity_contrast():
    out = evaluate_relationships(
        {
            "western.planets.sun.sign": "Aries",
            "western.planets.moon.sign": "Taurus",
        }
    )
    matched = {r.relationship_id: r.matched for r in out}
    assert matched["western_sun_moon_opposing_polarity"] is True


def test_cross_method_fire_overlap_match():
    out = evaluate_relationships(
        {
            "western.balance.elements.fire": 0.7,
            "bazi.element-balance.core": {"fire": 0.65},
        }
    )
    matched = {r.relationship_id: r.matched for r in out}
    assert matched["western_fire_bazi_fire_overlap"] is True


def test_evaluate_handles_missing_values():
    out = evaluate_relationships({})
    for r in out:
        assert r.matched is False
