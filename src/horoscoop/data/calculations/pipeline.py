from __future__ import annotations

from typing import Any

from .calculable_values import CALCULABLE_VALUES
from .calculation_manifest import CALCULATION_MANIFEST
from .types import CalculationDefinition, CalculationResult, MethodId
from .validation import validate_calculation_inputs, validate_calculation_output


def _method_data(method: MethodId, calculated_data: dict[str, Any]) -> dict[str, Any]:
    if method == "western":
        return calculated_data.get("western") or {}
    if method == "vedic":
        return calculated_data.get("vedic") or {}
    if method == "bazi":
        return calculated_data.get("chinese") or {}
    if method == "human-design":
        return calculated_data.get("human_design") or {}
    if method == "maya":
        return calculated_data.get("maya") or {}
    if method == "energy-profile":
        return {
            "energy_profile": calculated_data.get("energy_profile") or {},
            "energy_profile_combined": calculated_data.get("energy_profile_combined") or {},
            "cross_system": calculated_data.get("cross_system") or {},
            "profile_book": calculated_data.get("profile_book") or {},
        }
    return {}


def _topological_sort(definitions: list[CalculationDefinition]) -> list[CalculationDefinition]:
    by_id = {d["id"]: d for d in definitions}
    visited: set[str] = set()
    temp: set[str] = set()
    out: list[CalculationDefinition] = []

    def visit(calc_id: str) -> None:
        if calc_id in visited:
            return
        if calc_id in temp:
            return
        temp.add(calc_id)
        node = by_id.get(calc_id)
        if node:
            for dep in node.get("dependsOnCalculations", []):
                visit(dep)
            out.append(node)
        temp.remove(calc_id)
        visited.add(calc_id)

    for calc in definitions:
        visit(calc["id"])
    return out


def run_calculation_pipeline(
    user_input: dict[str, Any],
    enabled_methods: list[MethodId],
    calculated_data: dict[str, Any],
) -> dict[str, Any]:
    definitions = [d for d in CALCULATION_MANIFEST if d["method"] in enabled_methods]
    ordered = _topological_sort(definitions)
    results: dict[str, CalculationResult] = {}

    for definition in ordered:
        input_error = validate_calculation_inputs(
            definition,
            user_input=user_input,
            calculated_data=calculated_data,
            dependency_results=results,
        )
        if input_error is not None:
            results[definition["id"]] = input_error
            continue

        status = definition.get("implementationStatus")
        if status == "planned":
            results[definition["id"]] = {
                "calculationId": definition["id"],
                "method": definition["method"],
                "status": "planned",
                "userMessage": (definition.get("fallback", {}) or {}).get("planned", "Inhoudelijk voorbereid, nog niet actief."),
            }
            continue
        if status == "unsupported":
            results[definition["id"]] = {
                "calculationId": definition["id"],
                "method": definition["method"],
                "status": "unsupported",
                "userMessage": (definition.get("fallback", {}) or {}).get("unsupported", "Niet ondersteund."),
            }
            continue
        if status == "not-needed":
            results[definition["id"]] = {
                "calculationId": definition["id"],
                "method": definition["method"],
                "status": "not-applicable",
                "userMessage": (definition.get("fallback", {}) or {}).get("notApplicable", "Niet nodig in deze app."),
            }
            continue

        data = _method_data(definition["method"], calculated_data)
        invalid = validate_calculation_output(definition, data)
        if invalid is not None:
            results[definition["id"]] = invalid
            continue

        results[definition["id"]] = {
            "calculationId": definition["id"],
            "method": definition["method"],
            "status": "ready",
            "data": data,
            "outputKeys": {},
        }

    value_status: dict[str, dict[str, Any]] = {}
    for val in CALCULABLE_VALUES:
        calc_id = val.get("calculationId")
        calc_result = results.get(calc_id or "")
        value_status[val["id"]] = {
            "status": calc_result.get("status") if calc_result else "not-applicable",
            "calculationId": calc_id,
            "outputKey": val.get("outputKey"),
            "fallbackMessage": val.get("fallbackMessage"),
        }

    return {
        "results": results,
        "valueStatus": value_status,
        "definitions": [d["id"] for d in ordered],
    }

