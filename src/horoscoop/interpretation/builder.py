"""Interpretation Builder.

Stuurt formules door, controleert verplichte waarden, verzamelt
glossary-bronnen en produceert gecontroleerde InterpretationPoints.

De builder genereert NOOIT vrije tekst en doet NOOIT astrologische
gevolgtrekkingen die niet in de glossary of formule-templates staan.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from ..data.glossary import GLOSSARY, get_entry_or_none
from ..formulas import FORMULA_REGISTRY, FormulaDefinition
from ..values import VALUES_REGISTRY, glossary_key_for_value
from .types import InterpretationConfidence, InterpretationPoint


_PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_]+)\}")


# ---------------------------------------------------------------------------
# Helpers to extract resolved values from engine output
# ---------------------------------------------------------------------------


def extract_resolved_values(engine_output: dict[str, Any]) -> dict[str, Any]:
    """Map known value-id's naar raw values vanuit de engine-output.

    Robuust: ontbrekende waarden zijn `None`. Deze stap is een wrapper
    die niet alle id's in de calculation manifest hoeft te dekken; de
    Interpretation Builder kan met partiele data werken.
    """
    out: dict[str, Any] = {}

    western = engine_output.get("western") or {}
    placements = western.get("placements") or {}
    aspects = western.get("aspects") or []

    for planet_key, plan in placements.items():
        slug = planet_key.lower()
        out[f"western.planets.{slug}.sign"] = plan.get("sign")
        out[f"western.planets.{slug}.house"] = plan.get("house")
        out[f"western.planets.{slug}.degree"] = plan.get("degree_in_sign")
        out[f"western.planets.{slug}.retrograde"] = plan.get("retrograde")

    asc = (western.get("angles") or {}).get("ascendant") or {}
    if asc.get("sign"):
        out["western.ascendant.sign"] = asc["sign"]
        out["western.ascendant.degree"] = asc.get("degree_in_sign")

    mc = (western.get("angles") or {}).get("mc") or {}
    if mc.get("sign"):
        out["western.mc.sign"] = mc["sign"]

    nodes = western.get("nodes") or {}
    for node_key in ("north", "south"):
        node = nodes.get(node_key) or {}
        if node.get("sign"):
            out[f"western.nodes.{node_key}.sign"] = node["sign"]
            out[f"western.nodes.{node_key}.house"] = node.get("house")

    elements = (western.get("balance") or {}).get("elements") or {}
    for elem in ("fire", "earth", "air", "water"):
        if elem in elements:
            out[f"western.balance.elements.{elem}"] = elements[elem]

    out["__western.aspects"] = aspects  # convenience for aspect formulas

    bazi = engine_output.get("chinese") or {}
    bazi_balance = bazi.get("element_balance")
    if bazi_balance is not None:
        out["bazi.element-balance.core"] = bazi_balance

    hd = engine_output.get("human_design") or {}
    hd_type_raw = hd.get("type")
    if isinstance(hd_type_raw, dict):
        hd_type = hd_type_raw.get("name") or hd_type_raw.get("type")
    else:
        hd_type = hd_type_raw or hd.get("type_name")
    hd_authority_raw = hd.get("authority")
    if isinstance(hd_authority_raw, dict):
        hd_authority = hd_authority_raw.get("name") or hd_authority_raw.get("authority")
    else:
        hd_authority = hd_authority_raw or hd.get("authority_name")
    if hd_type:
        out["human-design.type.core"] = hd_type
    if hd_authority:
        out["human-design.authority.core"] = hd_authority

    maya = engine_output.get("maya") or {}
    seal_raw = maya.get("seal")
    if isinstance(seal_raw, dict):
        out["maya.seal.core"] = seal_raw.get("name") or seal_raw.get("seal")
    elif isinstance(seal_raw, str):
        out["maya.seal.core"] = seal_raw
    tone_raw = maya.get("tone")
    if isinstance(tone_raw, dict):
        out["maya.tone.core"] = tone_raw.get("number") or tone_raw.get("name")
    elif isinstance(tone_raw, (int, str)):
        out["maya.tone.core"] = tone_raw

    return out


# ---------------------------------------------------------------------------
# Glossary placeholder rendering
# ---------------------------------------------------------------------------


def _render_template(
    template: str,
    glossary_bindings: dict[str, dict[str, Any]],
) -> tuple[str, list[str]]:
    """Render `{role.field}` placeholders against a glossary binding dict.

    Returns (rendered_text, missing_placeholders).
    """
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        role = match.group(1)
        field = match.group(2)
        binding = glossary_bindings.get(role)
        if binding is None:
            missing.append(f"{role}.{field}")
            return match.group(0)
        if field not in binding:
            missing.append(f"{role}.{field}")
            return match.group(0)
        value = binding[field]
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return str(value)

    rendered = _PLACEHOLDER_RE.sub(replace, template)
    return rendered, missing


# ---------------------------------------------------------------------------
# Formula evaluation
# ---------------------------------------------------------------------------


def _expand_required_values(formula: FormulaDefinition, planet: str | None) -> list[str]:
    """Substitute `<planet>` / `<a>` / `<b>` patterns in requiredValues."""
    out = []
    for req in formula.get("requiredValues", []):
        if "<planet>" in req and planet:
            out.append(req.replace("<planet>", planet))
        else:
            out.append(req)
    return out


def _confidence_for(formula: FormulaDefinition, present_inputs: int) -> InterpretationConfidence:
    minimum = (formula.get("confidenceRules") or {}).get("minimumInputs", 1)
    if present_inputs >= minimum + 1:
        return "high"
    if present_inputs >= minimum:
        return "medium"
    return "low"


def _build_planet_in_sign_in_house(
    planet: str,
    resolved: dict[str, Any],
) -> InterpretationPoint | None:
    sign = resolved.get(f"western.planets.{planet}.sign")
    house = resolved.get(f"western.planets.{planet}.house")
    if not sign and house is None:
        return None

    formula = FORMULA_REGISTRY["western.planet_in_sign_in_house"]
    construct = formula["meaningConstruct"]

    planet_glossary_key = f"western.planet.{planet}"
    sign_glossary_key = f"western.sign.{str(sign).lower()}" if sign else None
    house_glossary_key = f"western.house.{house}" if house else None

    bindings: dict[str, dict[str, Any]] = {}
    sources: list[str] = []
    inputs: dict[str, str] = {"planet": planet}

    p_entry = get_entry_or_none(planet_glossary_key)
    if p_entry:
        bindings["planet"] = dict(p_entry)
        sources.append(planet_glossary_key)
    s_entry = get_entry_or_none(sign_glossary_key) if sign_glossary_key else None
    if s_entry:
        bindings["sign"] = dict(s_entry)
        sources.append(sign_glossary_key)
        inputs["sign"] = str(sign)
    h_entry = get_entry_or_none(house_glossary_key) if house_glossary_key else None
    if h_entry:
        bindings["house"] = dict(h_entry)
        sources.append(house_glossary_key)
        inputs["house"] = str(house)

    present_inputs = len(bindings)
    if present_inputs == 0:
        return None

    technical = _technical_label_planet(planet, sign, house)

    notes: list[str] = []

    if "planet" in bindings and "sign" in bindings and "house" in bindings:
        human_meaning, missing = _render_template(construct["semanticPattern"], bindings)
        notes.extend(missing)
        balanced, m1 = _render_template(construct["balancedTemplate"], bindings)
        notes.extend(m1)
        shadow, m2 = _render_template(construct["shadowTemplate"], bindings)
        notes.extend(m2)
        reflections: list[str] = []
        for q in construct["reflectionQuestionsTemplate"]:
            r, m = _render_template(q, bindings)
            reflections.append(r)
            notes.extend(m)
    elif "planet" in bindings and "sign" in bindings:
        sub = FORMULA_REGISTRY["western.planet_in_sign"]["meaningConstruct"]
        human_meaning, _ = _render_template(sub["semanticPattern"], bindings)
        balanced, _ = _render_template(sub["balancedTemplate"], bindings)
        shadow, _ = _render_template(sub["shadowTemplate"], bindings)
        reflections = [_render_template(q, bindings)[0] for q in sub["reflectionQuestionsTemplate"]]
    elif "planet" in bindings and "house" in bindings:
        sub = FORMULA_REGISTRY["western.planet_in_house"]["meaningConstruct"]
        human_meaning, _ = _render_template(sub["semanticPattern"], bindings)
        balanced, _ = _render_template(sub["balancedTemplate"], bindings)
        shadow, _ = _render_template(sub["shadowTemplate"], bindings)
        reflections = [_render_template(q, bindings)[0] for q in sub["reflectionQuestionsTemplate"]]
    else:
        return None

    return {
        "formulaId": formula["id"],
        "method": "western",
        "section": formula["outputSection"],
        "technicalLabel": technical,
        "humanMeaning": human_meaning,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "reflectionQuestions": reflections,
        "glossarySources": sources,
        "inputs": inputs,
        "confidence": _confidence_for(formula, present_inputs),
        "relationshipType": formula["relationshipType"],
        "notes": notes,
    }


def _technical_label_planet(planet: str, sign: Any, house: Any) -> str:
    label = planet.capitalize()
    parts: list[str] = [label]
    if sign:
        parts.append(f"in {sign}")
    if house:
        parts.append(f"(huis {house})")
    return " ".join(parts)


def _build_aspect_points(resolved: dict[str, Any]) -> list[InterpretationPoint]:
    out: list[InterpretationPoint] = []
    aspects = resolved.get("__western.aspects") or []
    formula = FORMULA_REGISTRY["western.aspect_between_planets"]
    construct = formula["meaningConstruct"]

    for asp in aspects:
        a = asp.get("a")
        b = asp.get("b")
        atype = asp.get("type") or asp.get("aspect")
        if not (a and b and atype):
            continue
        a_key = f"western.planet.{str(a).lower()}"
        b_key = f"western.planet.{str(b).lower()}"
        aspect_key = f"western.aspect.{str(atype).lower()}"
        bindings: dict[str, dict[str, Any]] = {}
        sources: list[str] = []
        for role, key in (("a", a_key), ("b", b_key), ("aspect", aspect_key)):
            entry = get_entry_or_none(key)
            if entry:
                bindings[role] = dict(entry)
                sources.append(key)
        if "aspect" not in bindings or "a" not in bindings or "b" not in bindings:
            continue
        human, _ = _render_template(construct["semanticPattern"], bindings)
        balanced, _ = _render_template(construct["balancedTemplate"], bindings)
        shadow, _ = _render_template(construct["shadowTemplate"], bindings)
        reflections = [_render_template(q, bindings)[0] for q in construct["reflectionQuestionsTemplate"]]
        out.append(
            {
                "formulaId": formula["id"],
                "method": "western",
                "section": formula["outputSection"],
                "technicalLabel": f"{a} {atype} {b}",
                "humanMeaning": human,
                "balancedExpression": balanced,
                "shadowExpression": shadow,
                "reflectionQuestions": reflections,
                "glossarySources": sources,
                "inputs": {"a": str(a), "b": str(b), "aspect": str(atype)},
                "confidence": "high" if asp.get("orb_deg") is not None else "medium",
                "relationshipType": formula["relationshipType"],
                "notes": [],
            }
        )
    return out


def _build_ascendant_point(resolved: dict[str, Any]) -> InterpretationPoint | None:
    sign = resolved.get("western.ascendant.sign")
    if not sign:
        return None
    formula = FORMULA_REGISTRY["western.ascendant_presentation"]
    construct = formula["meaningConstruct"]
    sign_key = f"western.sign.{str(sign).lower()}"
    s_entry = get_entry_or_none(sign_key)
    if not s_entry:
        return None
    bindings = {"sign": dict(s_entry)}
    sources = [sign_key]
    human, _ = _render_template(construct["semanticPattern"], bindings)
    balanced, _ = _render_template(construct["balancedTemplate"], bindings)
    shadow, _ = _render_template(construct["shadowTemplate"], bindings)
    reflections = [_render_template(q, bindings)[0] for q in construct["reflectionQuestionsTemplate"]]
    return {
        "formulaId": formula["id"],
        "method": "western",
        "section": formula["outputSection"],
        "technicalLabel": f"Ascendant in {sign}",
        "humanMeaning": human,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "reflectionQuestions": reflections,
        "glossarySources": sources,
        "inputs": {"sign": str(sign)},
        "confidence": "high",
        "relationshipType": formula["relationshipType"],
        "notes": [],
    }


def _build_node_point(resolved: dict[str, Any]) -> InterpretationPoint | None:
    nn_sign = resolved.get("western.nodes.north.sign")
    sn_sign = resolved.get("western.nodes.south.sign")
    if not (nn_sign or sn_sign):
        return None
    formula = FORMULA_REGISTRY["western.node_developmental_direction"]
    construct = formula["meaningConstruct"]
    bindings: dict[str, dict[str, Any]] = {}
    sources: list[str] = []
    if nn_sign:
        nn_entry = get_entry_or_none(f"western.sign.{str(nn_sign).lower()}")
        if nn_entry:
            bindings["northSign"] = dict(nn_entry)
            sources.append(f"western.sign.{str(nn_sign).lower()}")
    if sn_sign:
        sn_entry = get_entry_or_none(f"western.sign.{str(sn_sign).lower()}")
        if sn_entry:
            bindings["southSign"] = dict(sn_entry)
            sources.append(f"western.sign.{str(sn_sign).lower()}")
    if not bindings:
        return None
    human, _ = _render_template(construct["semanticPattern"], bindings)
    balanced, _ = _render_template(construct["balancedTemplate"], bindings)
    shadow, _ = _render_template(construct["shadowTemplate"], bindings)
    reflections = [_render_template(q, bindings)[0] for q in construct["reflectionQuestionsTemplate"]]
    return {
        "formulaId": formula["id"],
        "method": "western",
        "section": formula["outputSection"],
        "technicalLabel": f"Knopen: {nn_sign or '?'} / {sn_sign or '?'}",
        "humanMeaning": human,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "reflectionQuestions": reflections,
        "glossarySources": sources,
        "inputs": {"northSign": str(nn_sign or ""), "southSign": str(sn_sign or "")},
        "confidence": "medium" if len(bindings) == 1 else "high",
        "relationshipType": formula["relationshipType"],
        "notes": [],
    }


def _build_element_balance_point(resolved: dict[str, Any]) -> InterpretationPoint | None:
    scores = {
        elem: resolved.get(f"western.balance.elements.{elem}")
        for elem in ("fire", "earth", "air", "water")
    }
    available = {k: v for k, v in scores.items() if isinstance(v, (int, float))}
    if not available:
        return None
    dominant = max(available.items(), key=lambda kv: kv[1])
    elem_key = f"western.element.{dominant[0]}"
    entry = get_entry_or_none(elem_key)
    if not entry:
        return None
    formula = FORMULA_REGISTRY["western.element_balance_dominant"]
    construct = formula["meaningConstruct"]
    bindings = {"element": dict(entry)}
    human, _ = _render_template(construct["semanticPattern"], bindings)
    balanced, _ = _render_template(construct["balancedTemplate"], bindings)
    shadow, _ = _render_template(construct["shadowTemplate"], bindings)
    reflections = [_render_template(q, bindings)[0] for q in construct["reflectionQuestionsTemplate"]]
    return {
        "formulaId": formula["id"],
        "method": "western",
        "section": formula["outputSection"],
        "technicalLabel": f"Dominant element: {entry['label']}",
        "humanMeaning": human,
        "balancedExpression": balanced,
        "shadowExpression": shadow,
        "reflectionQuestions": reflections,
        "glossarySources": [elem_key],
        "inputs": {"element": dominant[0], "score": str(round(dominant[1], 3))},
        "confidence": "high" if len(available) == 4 else "medium",
        "relationshipType": formula["relationshipType"],
        "notes": [],
    }


def _build_cross_element_overlap(resolved: dict[str, Any]) -> list[InterpretationPoint]:
    from ..relationships import evaluate_relationships

    formula = FORMULA_REGISTRY["cross.element_overlap"]
    construct = formula["meaningConstruct"]

    out: list[InterpretationPoint] = []

    relations = evaluate_relationships(resolved)
    for rel in relations:
        if rel.relationship_id in {"western_fire_bazi_fire_overlap", "western_water_bazi_water_overlap"} and rel.matched:
            element = "fire" if "fire" in rel.relationship_id else "water"
            elem_key = f"western.element.{element}"
            entry = get_entry_or_none(elem_key)
            if not entry:
                continue
            bindings = {"element": dict(entry)}
            human, _ = _render_template(construct["semanticPattern"], bindings)
            balanced, _ = _render_template(construct["balancedTemplate"], bindings)
            shadow, _ = _render_template(construct["shadowTemplate"], bindings)
            reflections = [_render_template(q, bindings)[0] for q in construct["reflectionQuestionsTemplate"]]
            out.append(
                {
                    "formulaId": formula["id"],
                    "method": "cross",
                    "section": "synthesis",
                    "technicalLabel": f"Cross-method overlap: {entry['label']}",
                    "humanMeaning": human,
                    "balancedExpression": balanced,
                    "shadowExpression": shadow,
                    "reflectionQuestions": reflections,
                    "glossarySources": [elem_key],
                    "inputs": {"element": element},
                    "confidence": "high",
                    "relationshipType": formula["relationshipType"],
                    "notes": [],
                }
            )
    return out


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------


_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
            "uranus", "neptune", "pluto", "chiron"]


def build_interpretation_points(
    engine_output: dict[str, Any] | None = None,
    resolved_values: dict[str, Any] | None = None,
) -> list[InterpretationPoint]:
    """Bouw alle interpretationPoints uit gegeven engine-output of resolved values.

    Aanvaardt OFWEL `engine_output` (rauwe engine.compute()-dict) OF
    een vooraf gevulde `resolved_values`-dict; bij beide wordt
    `engine_output` voorrang gegeven en aangevuld met extra resolved
    values uit de gebruiker.
    """
    resolved: dict[str, Any] = {}
    if engine_output is not None:
        resolved.update(extract_resolved_values(engine_output))
    if resolved_values:
        resolved.update(resolved_values)

    points: list[InterpretationPoint] = []

    for planet in _PLANETS:
        pt = _build_planet_in_sign_in_house(planet, resolved)
        if pt:
            points.append(pt)

    asc_pt = _build_ascendant_point(resolved)
    if asc_pt:
        points.append(asc_pt)

    points.extend(_build_aspect_points(resolved))

    node_pt = _build_node_point(resolved)
    if node_pt:
        points.append(node_pt)

    elem_pt = _build_element_balance_point(resolved)
    if elem_pt:
        points.append(elem_pt)

    points.extend(_build_cross_element_overlap(resolved))

    return points
