"""
Normalize diagnostics from engine output to ViewModel format.
{codes: [], warnings: [{code, label_nl}], confidence_overall}
"""
from __future__ import annotations

from typing import Any

DIAGNOSTIC_LABELS_NL: dict[str, str] = {
    "NO_TIMEZONE": "Geen tijdzone opgegeven; huizen niet berekend.",
    "NO_BIRTHTIME": "Geen geboortetijd opgegeven.",
    "USED_DEFAULT_TIME": "Standaardtijd 12:00 gebruikt.",
    "EOP_MISSING": "UT1-UTC niet beschikbaar; aangenomen 0s.",
    "DELTAT_MODEL": "ΔT via model (geen IERS).",
    "VEDIC_SUNRISE_REQUIRES_LOCATION": "Vedisch op basis van zonsopkomst vereist locatie.",
    "VEDIC_SUNRISE_UNAVAILABLE": "Zonsopkomst niet berekend.",
    "CNY_LEAP_RULES_SIMPLIFIED": "Chinese Nieuwjaar (vereenvoudigde berekening).",
    "MISSING_FIELD": "Ontbrekend veld.",
}


def _label_for_code(code: str) -> str:
    if code.startswith("MISSING_FIELD:"):
        return f"Ontbrekend veld: {code.replace('MISSING_FIELD:', '', 1)}"
    return DIAGNOSTIC_LABELS_NL.get(code, code)


def normalize_diagnostics(engine_json: dict[str, Any]) -> dict[str, Any]:
    """
    Aggregate diagnostics from engine JSON into ViewModel format.
    Sources: diagnostics.codes, time.status.warnings, block statuses.
    """
    codes: list[str] = []
    warnings: list[dict[str, str]] = []

    diag = engine_json.get("diagnostics") or {}
    codes = list(diag.get("codes") or [])

    time_block = engine_json.get("time") or {}
    time_status = time_block.get("status") or {}
    time_warnings = time_status.get("warnings") or []
    for w in time_warnings:
        if isinstance(w, str) and ":" in w:
            code_part = w.split(":")[0].strip()
            if code_part and code_part not in codes:
                codes.append(code_part)
        elif isinstance(w, str) and w not in [x.get("code") for x in warnings]:
            codes.append(w)

    western = engine_json.get("western")
    if western:
        houses = western.get("houses") or {}
        h_status = houses.get("status") or {}
        for w in (h_status.get("warnings") or []):
            if isinstance(w, str) and w not in codes:
                codes.append(w)

    vedic = engine_json.get("vedic") or {}
    vedic_diag = vedic.get("diagnostics") or []
    for d in vedic_diag:
        if isinstance(d, str) and d not in codes:
            codes.append(d)

    chinese = engine_json.get("chinese") or {}
    chinese_diag = chinese.get("diagnostics") or []
    for d in chinese_diag:
        if isinstance(d, str) and d not in codes:
            codes.append(d)
    chinese_status = chinese.get("status") or {}
    for w in (chinese_status.get("warnings") or []):
        if isinstance(w, str) and w not in codes:
            codes.append(w)

    seen: set[str] = set()
    for c in codes:
        if c not in seen:
            seen.add(c)
            warnings.append({"code": c, "label_nl": _label_for_code(c)})

    confidence_overall = "high"
    if "NO_TIMEZONE" in codes or "EOP_MISSING" in codes:
        confidence_overall = "estimated"
    if "NO_BIRTHTIME" in codes or "USED_DEFAULT_TIME" in codes:
        if confidence_overall == "high":
            confidence_overall = "estimated"
    if "VEDIC_SUNRISE_REQUIRES_LOCATION" in codes or "VEDIC_SUNRISE_UNAVAILABLE" in codes:
        if confidence_overall == "high":
            confidence_overall = "medium"

    return {
        "codes": codes,
        "warnings": warnings,
        "confidence_overall": confidence_overall,
    }
