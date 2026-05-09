from __future__ import annotations

import math
from typing import Any

from .calculable_values import CALCULABLE_VALUES
from .types import CalculationDefinition, CalculationResult, InputRequirement


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _input_present(input_name: InputRequirement, user_input: dict[str, Any], calculated_data: dict[str, Any]) -> bool:
    mapping = {
        "birthDate": user_input.get("birthDate"),
        "birthTime": user_input.get("birthTime"),
        "birthPlace": user_input.get("birthPlace"),
        "timezone": user_input.get("timezone"),
        "coordinates": user_input.get("coordinates"),
        "calculatedWesternChart": calculated_data.get("western"),
        "calculatedVedicChart": calculated_data.get("vedic"),
        "calculatedBaziChart": calculated_data.get("chinese"),
        "calculatedHumanDesignChart": calculated_data.get("human_design"),
        "calculatedMayaChart": calculated_data.get("maya"),
    }
    return not _is_missing(mapping.get(input_name))


def validate_calculation_inputs(
    calculation_definition: CalculationDefinition,
    user_input: dict[str, Any],
    calculated_data: dict[str, Any],
    dependency_results: dict[str, CalculationResult],
) -> CalculationResult | None:
    missing_inputs: list[InputRequirement] = []
    for req in calculation_definition.get("requiredInputs", []):
        if not _input_present(req, user_input, calculated_data):
            missing_inputs.append(req)

    if missing_inputs:
        return {
            "calculationId": calculation_definition["id"],
            "method": calculation_definition["method"],
            "status": "missing-input",
            "missingInputs": missing_inputs,
            "userMessage": (calculation_definition.get("fallback", {}) or {}).get("missingInput", "Benodigde invoer ontbreekt."),
        }

    for dep in calculation_definition.get("dependsOnCalculations", []):
        dep_result = dependency_results.get(dep)
        if not dep_result or dep_result.get("status") not in ("ready",):
            return {
                "calculationId": calculation_definition["id"],
                "method": calculation_definition["method"],
                "status": "calculation-failed",
                "errorMessage": f"Dependency not ready: {dep}",
                "userMessage": (calculation_definition.get("fallback", {}) or {}).get("calculationFailed", "Afhankelijke berekening niet beschikbaar."),
            }
    return None


def _flatten(d: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(d, dict):
        for key, val in d.items():
            nxt = f"{prefix}.{key}" if prefix else str(key)
            out.update(_flatten(val, nxt))
    else:
        out[prefix] = d
    return out


def validate_calculation_output(
    calculation_definition: CalculationDefinition,
    result_data: dict[str, Any],
) -> CalculationResult | None:
    flat = _flatten(result_data)
    for key in calculation_definition.get("outputKeys", []):
        if key not in flat and not any(k.startswith(f"{key}.") for k in flat):
            return {
                "calculationId": calculation_definition["id"],
                "method": calculation_definition["method"],
                "status": "invalid-data",
                "errorMessage": f"Output key missing: {key}",
                "userMessage": (calculation_definition.get("fallback", {}) or {}).get("invalidData", "Berekende output is onvolledig."),
            }
    values_by_calc = {v.get("calculationId") for v in CALCULABLE_VALUES}
    if calculation_definition["id"] not in values_by_calc:
        return {
            "calculationId": calculation_definition["id"],
            "method": calculation_definition["method"],
            "status": "invalid-data",
            "errorMessage": "No calculable value mapping found",
            "userMessage": (calculation_definition.get("fallback", {}) or {}).get("invalidData", "Geen calculableValues-koppeling gevonden."),
        }
    return None

