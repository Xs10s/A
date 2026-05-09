from __future__ import annotations

from horoscoop.data.glossary import (
    GLOSSARY,
    get_entries_by_category,
    get_entries_by_method,
    get_entry,
    get_entry_or_none,
    list_keys,
)


def test_glossary_has_all_western_signs():
    signs = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ]
    for s in signs:
        entry = get_entry(f"western.sign.{s}")
        assert entry["category"] == "sign"
        assert entry["method"] == "western"
        assert entry["essence"]
        assert entry["balancedExpression"]
        assert entry["shadowExpression"]
        assert entry["lifeArea"]
        assert entry["reflectionQuestions"]
        assert entry["avoidClaims"]


def test_glossary_has_all_western_planets():
    planets = [
        "sun", "moon", "mercury", "venus", "mars", "jupiter",
        "saturn", "uranus", "neptune", "pluto", "chiron",
    ]
    for p in planets:
        entry = get_entry(f"western.planet.{p}")
        assert entry["category"] == "planet"
        assert entry["essence"]


def test_glossary_has_all_houses_1_to_12():
    for n in range(1, 13):
        entry = get_entry(f"western.house.{n}")
        assert entry["category"] == "house"
        assert entry["essence"]


def test_glossary_aspects_present():
    for a in ("conjunction", "sextile", "square", "trine", "opposition", "quincunx"):
        entry = get_entry(f"western.aspect.{a}")
        assert entry["category"] == "aspect"


def test_glossary_elements_present():
    for e in ("fire", "earth", "air", "water"):
        entry = get_entry(f"western.element.{e}")
        assert entry["category"] == "element"


def test_get_entries_by_method():
    western = get_entries_by_method("western")
    assert len(western) > 30
    bazi = get_entries_by_method("bazi")
    assert any(e["category"] == "five_element" for e in bazi)


def test_get_entries_by_category_signs():
    signs = get_entries_by_category("sign")
    assert len(signs) >= 12


def test_get_entry_or_none_returns_none_for_missing():
    assert get_entry_or_none("western.sign.nonexistent") is None


def test_list_keys_sorted():
    keys = list_keys()
    assert keys == sorted(keys)


def test_glossary_no_duplicate_keys():
    seen: set[str] = set()
    for entry in GLOSSARY.values():
        key = entry["key"]
        assert key not in seen
        seen.add(key)
