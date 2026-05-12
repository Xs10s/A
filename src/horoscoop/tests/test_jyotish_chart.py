"""Unit checks for Jyotish chart helpers (dignity, naisargika)."""
from horoscoop import jyotish_chart as jc


def test_natural_dignity_mitra_to_sign_lord():
    # Jupiter in Mesha (0): lord Mars; Jupiter is mitra with Mars
    d = jc.natural_dignity("Jupiter", 0)
    assert d is not None
    assert d["code"] == "mitra_sign_lord"
    assert d.get("rashilord_en") == "Mars"


def test_natural_dignity_satru_to_sign_lord():
    # Venus in Simha (4): lord Sun; Venus is satru with Sun
    d = jc.natural_dignity("Venus", 4)
    assert d is not None
    assert d["code"] == "satru_sign_lord"
    assert d.get("rashilord_en") == "Sun"


def test_natural_dignity_sama_to_sign_lord():
    # Moon in Dhanu (8): lord Jupiter; Moon is sama (neutral) with Jupiter
    d = jc.natural_dignity("Moon", 8)
    assert d is not None
    assert d["code"] == "sama_sign_lord"
    assert d.get("rashilord_en") == "Jupiter"


def test_natural_dignity_moon_exalted_in_vrishabha():
    d = jc.natural_dignity("Moon", 1)
    assert d["code"] == "exalted"
    assert d.get("rashilord_en") == "Venus"


def test_natural_dignity_nodes_carry_rashilord():
    d = jc.natural_dignity("Rahu", 3)
    assert d["code"] == "nodes"
    assert d.get("rashilord_en") == "Moon"


def test_navamsa_equals_varga_d9():
    sid = 118.5  # Cancer near 28.5 deg; water-sign D9 from Cancer
    assert jc.navamsa_rashi_index(sid) == jc.varga_rashi_index("D9", sid)
    assert jc.varga_rashi_index("D9", sid) == 11  # Pisces


def test_dashamsa_equals_varga_d10():
    sid = 45.25  # arbitrary Taurus mid
    assert jc.dashamsa_rashi_index(sid) == jc.varga_rashi_index("D10", sid)


def test_build_varga_map_has_sixteen_keys():
    sid = 15.0
    lag = 20.0
    m = jc.build_varga_map(sid, lag)
    assert set(m.keys()) == set(jc.SHODASHA_VARGA_IDS)
    assert m["D1"]["house"] == jc.whole_sign_house_from_reference_sign(
        jc._rashi_index(sid), jc._rashi_index(lag)
    )


def test_hora_odd_sign_first_half_leo():
    # Aries 10 deg: first hora is Leo
    assert jc.hora_rashi_index(10.0) == 4


def test_trimshamsa_odd_first_portion_scorpio():
    assert jc.trimshamsa_rashi_index(2.0) == 8
