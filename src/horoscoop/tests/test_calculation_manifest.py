from __future__ import annotations

from horoscoop.data.calculations.calculable_values import CALCULABLE_VALUES
from horoscoop.data.calculations.calculation_manifest import CALCULATION_MANIFEST
from horoscoop.data.calculations.pipeline import run_calculation_pipeline
from horoscoop.data.calculations.result_fields import RESULT_FIELD_DEFINITIONS


def test_manifest_ids_unique():
    ids = [d["id"] for d in CALCULATION_MANIFEST]
    assert len(ids) == len(set(ids))


def test_manifest_has_required_core_fields():
    for definition in CALCULATION_MANIFEST:
        assert definition.get("requiredInputs") is not None
        assert definition.get("outputKeys") is not None
        assert definition.get("fallback") is not None


def test_calculable_values_reference_manifest_or_explicit_status():
    calc_ids = {d["id"] for d in CALCULATION_MANIFEST}
    for value in CALCULABLE_VALUES:
        cid = value.get("calculationId")
        if cid:
            assert cid in calc_ids
        assert value.get("status") in {"implemented", "planned", "unsupported", "not-needed", "derived"}


def test_variable_result_fields_have_calculation_ids():
    for field in RESULT_FIELD_DEFINITIONS:
        if field.get("kind") == "variable":
            assert field.get("calculationIds")


def test_pipeline_returns_statuses_without_crashing():
    out = run_calculation_pipeline(
        user_input={
            "birthDate": "2000-01-01",
            "birthTime": "12:00:00",
            "birthPlace": {"lat": 52.0, "lon": 5.0},
            "timezone": 1.0,
            "coordinates": {"lat": 52.0, "lon": 5.0},
        },
        enabled_methods=["western", "vedic", "bazi", "human-design", "maya", "energy-profile"],
        calculated_data={"western": {}, "vedic": {}, "chinese": {}, "human_design": {}, "maya": {}},
    )
    assert "results" in out
    assert "valueStatus" in out

