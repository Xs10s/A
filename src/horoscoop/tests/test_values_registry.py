from __future__ import annotations

from horoscoop.values import (
    VALUES_REGISTRY,
    get_value,
    get_value_or_none,
    get_values_by_method,
    get_values_by_section,
    glossary_key_for_value,
    list_value_ids,
)


def test_registry_built_from_calculable_values():
    assert "western.planets.sun.sign" in VALUES_REGISTRY
    assert "western.balance.elements.fire" in VALUES_REGISTRY


def test_western_sun_sign_metadata_enrichment():
    v = get_value("western.planets.sun.sign")
    assert v["valueType"] == "sign"
    assert v["glossaryKeyPrefix"] == "western.sign."
    assert v["priority"] == "high"
    assert "identity" in v["requiredFor"]
    assert "western.planets.sun.house" in v["canRelateTo"]


def test_glossary_key_resolution_for_sign():
    key = glossary_key_for_value("western.planets.sun.sign", "Sagittarius")
    assert key == "western.sign.sagittarius"
    assert glossary_key_for_value("western.planets.sun.sign", None) is None
    assert glossary_key_for_value("western.planets.sun.sign", "BogusSign") is None


def test_glossary_key_resolution_for_house_uses_fixed_key():
    key = glossary_key_for_value("western.houses.5.cusp-sign", "Leo")
    assert key == "western.house.5"


def test_get_values_by_method():
    western = get_values_by_method("western")
    assert len(western) > 40


def test_get_values_by_section_identity():
    section_values = get_values_by_section("identity")
    ids = [v["id"] for v in section_values]
    assert "western.planets.sun.sign" in ids


def test_value_or_none_returns_none():
    assert get_value_or_none("nonexistent.value") is None


def test_list_value_ids_sorted():
    ids = list_value_ids()
    assert ids == sorted(ids)
