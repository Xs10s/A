from __future__ import annotations

from horoscoop.architecture_validation import (
    generate_formula_coverage_report,
    validate_architecture,
)


def test_no_high_priority_orphans():
    report = generate_formula_coverage_report()
    assert report.high_priority_orphans == [], (
        f"High-priority orphan values: {report.high_priority_orphans}"
    )


def test_no_invalid_formulas():
    report = generate_formula_coverage_report()
    assert report.invalid_formulas == [], (
        f"Invalid formulas: {report.invalid_formulas}"
    )


def test_no_relationship_value_issues():
    report = generate_formula_coverage_report()
    assert report.relationship_issues == [], (
        f"Relationship issues: {report.relationship_issues}"
    )


def test_validate_architecture_returns_no_issues():
    issues = validate_architecture()
    assert issues == [], f"Architecture issues found: {issues}"


def test_method_coverage_includes_western_and_cross():
    report = generate_formula_coverage_report()
    assert report.method_coverage.get("western", 0) >= 1
    assert report.method_coverage.get("cross", 0) >= 1


def test_output_section_coverage_includes_core_identity():
    report = generate_formula_coverage_report()
    assert "core_identity" in report.output_section_coverage
