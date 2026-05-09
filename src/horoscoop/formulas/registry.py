"""Formula Registry.

Verzamelt alle FormulaDefinition objecten in een deterministische
mapping op id. Nieuwe methodes voegen hier hun formules toe.
"""

from __future__ import annotations

from .cross_method import CROSS_FORMULAS
from .types import FormulaDefinition
from .western import WESTERN_FORMULAS


def _build_registry(*formula_lists: list[FormulaDefinition]) -> dict[str, FormulaDefinition]:
    out: dict[str, FormulaDefinition] = {}
    for formulas in formula_lists:
        for f in formulas:
            fid = f["id"]
            if fid in out:
                raise ValueError(f"Duplicate formula id: {fid}")
            out[fid] = f
    return out


FORMULA_REGISTRY: dict[str, FormulaDefinition] = _build_registry(
    WESTERN_FORMULAS,
    CROSS_FORMULAS,
)


def get_formula(formula_id: str) -> FormulaDefinition:
    return FORMULA_REGISTRY[formula_id]


def get_formula_or_none(formula_id: str) -> FormulaDefinition | None:
    return FORMULA_REGISTRY.get(formula_id)


def get_formulas_by_method(method: str) -> list[FormulaDefinition]:
    return [f for f in FORMULA_REGISTRY.values() if f.get("method") == method]


def get_formulas_by_section(section: str) -> list[FormulaDefinition]:
    return [
        f for f in FORMULA_REGISTRY.values()
        if f.get("outputSection") == section
    ]


def list_formula_ids() -> list[str]:
    return sorted(FORMULA_REGISTRY.keys())
