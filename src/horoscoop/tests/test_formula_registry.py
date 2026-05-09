from __future__ import annotations

from horoscoop.formulas import (
    FORMULA_REGISTRY,
    get_formula,
    get_formulas_by_method,
    get_formulas_by_section,
    list_formula_ids,
)


def test_western_planet_in_sign_in_house_present():
    f = get_formula("western.planet_in_sign_in_house")
    assert f["method"] == "western"
    assert f["fallbackTemplate"]
    assert f["meaningConstruct"]["semanticPattern"]
    assert f["meaningConstruct"]["balancedTemplate"]
    assert f["meaningConstruct"]["shadowTemplate"]


def test_aspect_formula_present():
    f = get_formula("western.aspect_between_planets")
    assert f["relationshipType"] == "tension_or_flow"


def test_cross_method_formulas_present():
    cross = get_formulas_by_method("cross")
    ids = [f["id"] for f in cross]
    assert "cross.element_overlap" in ids


def test_formula_ids_unique():
    ids = list_formula_ids()
    assert len(ids) == len(set(ids))


def test_each_formula_has_required_fields():
    for f in FORMULA_REGISTRY.values():
        assert f.get("id")
        assert f.get("method")
        assert f.get("fallbackTemplate")
        assert f.get("meaningConstruct")
        assert f["meaningConstruct"].get("semanticPattern")
        assert f.get("relationshipType")
        assert f.get("outputSection")


def test_get_formulas_by_section_core_identity():
    core = get_formulas_by_section("core_identity")
    assert any(f["id"] == "western.planet_in_sign_in_house" for f in core)
