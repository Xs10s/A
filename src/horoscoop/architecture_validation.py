"""Architecture Validation Layer.

Controleert de samenhang tussen de architectuurlagen:

    - Elke FormulaDefinition.requiredValues bestaat in de Values Registry
      (na placeholder-substitutie).
    - Elke Formula.glossaryKeysNeeded heeft minstens 1 glossary entry
      per categorie.
    - Geen orphan values: elke Values Registry value heeft minstens
      een formule of relatie waar hij in voorkomt (high/medium priority).
    - Elke value met `priority="high"` heeft minimaal 1 formule.
    - Elke formule heeft een fallbackTemplate.
    - Cross-method relaties verwijzen naar bestaande values.
    - Coverage rapport.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .data.glossary import GLOSSARY, get_entries_by_category
from .formulas import FORMULA_REGISTRY, FormulaDefinition
from .relationships import RELATIONSHIP_MATRIX
from .values import VALUES_REGISTRY


_PLACEHOLDER_VALUE_RE = re.compile(r"<([^>]+)>")


@dataclass
class FormulaCoverageReport:
    total_values: int = 0
    covered_values: list[str] = field(default_factory=list)
    orphan_values: list[str] = field(default_factory=list)
    high_priority_orphans: list[str] = field(default_factory=list)
    total_formulas: int = 0
    invalid_formulas: list[dict] = field(default_factory=list)
    missing_glossary_keys: list[str] = field(default_factory=list)
    missing_glossary_categories: list[str] = field(default_factory=list)
    output_section_coverage: dict[str, int] = field(default_factory=dict)
    method_coverage: dict[str, int] = field(default_factory=dict)
    recommended_missing_formulas: list[str] = field(default_factory=list)
    relationship_issues: list[dict] = field(default_factory=list)


def _resolves_value(value_pattern: str) -> list[str]:
    """Expand patterns like 'western.planets.<planet>.sign' to all known matches."""
    placeholders = _PLACEHOLDER_VALUE_RE.findall(value_pattern)
    if not placeholders:
        return [value_pattern] if value_pattern in VALUES_REGISTRY else []

    pattern_re = re.escape(value_pattern)
    for ph in placeholders:
        pattern_re = pattern_re.replace(re.escape(f"<{ph}>"), r"[a-z0-9_-]+")
    full_re = re.compile(f"^{pattern_re}$")
    return [vid for vid in VALUES_REGISTRY.keys() if full_re.match(vid)]


def _validate_formula(formula: FormulaDefinition) -> dict | None:
    issues: dict[str, list[str]] = {}

    fallback = formula.get("fallbackTemplate", "")
    if not fallback:
        issues.setdefault("missing_fields", []).append("fallbackTemplate")

    required = formula.get("requiredValues") or []
    for req in required:
        resolved = _resolves_value(req)
        if not resolved:
            issues.setdefault("missing_required_values", []).append(req)

    if not formula.get("meaningConstruct"):
        issues.setdefault("missing_fields", []).append("meaningConstruct")

    if not formula.get("relationshipType"):
        issues.setdefault("missing_fields", []).append("relationshipType")

    if not formula.get("outputSection"):
        issues.setdefault("missing_fields", []).append("outputSection")

    if issues:
        return {"formulaId": formula.get("id", ""), **issues}
    return None


def _validate_glossary_keys_for_formula(formula: FormulaDefinition) -> list[str]:
    needed = formula.get("glossaryKeysNeeded") or []
    missing: list[str] = []
    for category in needed:
        if not get_entries_by_category(category):
            missing.append(category)
    return missing


def _formula_uses_value(formula: FormulaDefinition, value_id: str) -> bool:
    for req in formula.get("requiredValues", []):
        for resolved in _resolves_value(req):
            if resolved == value_id:
                return True
    for opt in formula.get("optionalValues", []) or []:
        for resolved in _resolves_value(opt):
            if resolved == value_id:
                return True
    return False


def _relationship_uses_value(value_id: str) -> bool:
    for rel in RELATIONSHIP_MATRIX:
        if rel.get("left") == value_id or rel.get("right") == value_id:
            return True
    return False


def _validate_relationships() -> list[dict]:
    issues: list[dict] = []
    for rel in RELATIONSHIP_MATRIX:
        for side in ("left", "right"):
            value_id = rel.get(side)
            if value_id and value_id not in VALUES_REGISTRY:
                issues.append({
                    "relationshipId": rel.get("id"),
                    "issue": f"missing-value-on-{side}",
                    "value": value_id,
                })
    return issues


def generate_formula_coverage_report() -> FormulaCoverageReport:
    report = FormulaCoverageReport()
    report.total_values = len(VALUES_REGISTRY)
    report.total_formulas = len(FORMULA_REGISTRY)

    for formula in FORMULA_REGISTRY.values():
        invalid = _validate_formula(formula)
        if invalid is not None:
            report.invalid_formulas.append(invalid)
        missing_categories = _validate_glossary_keys_for_formula(formula)
        if missing_categories:
            report.missing_glossary_categories.extend(
                f"{formula['id']}::{cat}" for cat in missing_categories
            )
        section = formula.get("outputSection", "unknown")
        report.output_section_coverage[section] = (
            report.output_section_coverage.get(section, 0) + 1
        )
        method = formula.get("method", "unknown")
        report.method_coverage[method] = report.method_coverage.get(method, 0) + 1

    for value_id, value in VALUES_REGISTRY.items():
        used = any(_formula_uses_value(f, value_id) for f in FORMULA_REGISTRY.values())
        used = used or _relationship_uses_value(value_id)
        if used:
            report.covered_values.append(value_id)
        else:
            report.orphan_values.append(value_id)
            if value.get("priority") == "high":
                report.high_priority_orphans.append(value_id)

    if not get_entries_by_category("sign"):
        report.missing_glossary_keys.append("category:sign")
    if not get_entries_by_category("planet"):
        report.missing_glossary_keys.append("category:planet")

    if report.high_priority_orphans:
        report.recommended_missing_formulas.append(
            "Voeg minstens 1 formule toe voor elke high-priority value zonder formule."
        )
    if report.invalid_formulas:
        report.recommended_missing_formulas.append(
            "Los validatiefouten op in formules (zie invalid_formulas)."
        )

    report.relationship_issues = _validate_relationships()

    return report


def validate_architecture() -> list[str]:
    """Return een lijst met human-readable issues. Lege lijst => geen issues."""
    issues: list[str] = []
    report = generate_formula_coverage_report()
    if report.invalid_formulas:
        for inv in report.invalid_formulas:
            issues.append(f"Formula {inv.get('formulaId')} heeft issues: {sorted(set(inv.keys()) - {'formulaId'})}")
    if report.high_priority_orphans:
        issues.append(
            f"High-priority orphan values (geen formule): {report.high_priority_orphans}"
        )
    if report.relationship_issues:
        for ri in report.relationship_issues:
            issues.append(f"Relationship issue: {ri}")
    if report.missing_glossary_categories:
        issues.append(
            f"Glossary categories ontbreken voor formules: {report.missing_glossary_categories}"
        )
    return issues
