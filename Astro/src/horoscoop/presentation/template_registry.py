"""
Template registry: load method-specific templates and resolve sections.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

_TEMPLATES: dict[str, dict[str, Any]] = {}
_LOADED = False


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _load_templates() -> None:
    global _LOADED, _TEMPLATES
    if _LOADED:
        return
    web_dir = _templates_dir() / "web"
    report_dir = _templates_dir() / "report"
    for d in [web_dir, report_dir]:
        if not d.exists():
            continue
        for f in d.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                tid = data.get("method_id") or data.get("template_id") or f.stem
                _TEMPLATES[tid] = data
            except Exception:
                pass
    _LOADED = True


def get_template(method_id: str, medium: str = "web") -> Optional[dict[str, Any]]:
    """
    Get template for method_id. medium: "web" | "report".
    Web templates: western_tropical, western_sidereal, vedic_panchanga, chinese_ganzhi_bazi.
    Report: default_report.
    """
    _load_templates()
    key = method_id
    if medium == "report" and method_id == "default":
        key = "default_report"
    return _TEMPLATES.get(key)


def resolve_sections(
    view_model: dict[str, Any],
    method_id: str,
    medium: str = "web",
) -> list[dict[str, Any]]:
    """
    Resolve sections for a method from template + ViewModel.
    Returns list of section configs with resolved source data.
    """
    template = get_template(method_id, medium)
    if not template:
        return []
    method_data = None
    for m in view_model.get("methods", []):
        if m.get("id") == method_id:
            method_data = m
            break
    if not method_data:
        return []
    sections_cfg = template.get("sections", [])
    result = []
    for sec in sections_cfg:
        sec_type = sec.get("type", "table")
        source_keys = sec.get("source_keys", [])
        resolved = dict(sec)
        if source_keys:
            sec_data = method_data.get("sections") or {}
            data = []
            for k in source_keys:
                val = sec_data.get(k)
                if val is not None:
                    data.append(val)
            if len(source_keys) == 1:
                resolved["data"] = sec_data.get(source_keys[0])
            else:
                resolved["data"] = {k: sec_data.get(k) for k in source_keys}
        result.append(resolved)
    return result


def list_templates(medium: Optional[str] = None) -> list[str]:
    """List available template IDs."""
    _load_templates()
    if medium == "web":
        return [k for k in _TEMPLATES if k in ("western_tropical", "western_sidereal", "vedic_panchanga", "chinese_ganzhi_bazi")]
    if medium == "report":
        return [k for k in _TEMPLATES if k == "default_report"]
    return list(_TEMPLATES.keys())
