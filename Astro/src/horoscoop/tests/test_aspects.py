"""
Unit tests: angular separation, aspect detection, orb.
Workstream 4: applying/separating, orb_degrees, orb resolver, extended aspects.
"""
import pytest
import sqlite3

from horoscoop import aspects
from horoscoop import db_orbs


def test_angular_separation_deg():
    assert aspects.angular_separation_deg(0, 0) == 0
    assert aspects.angular_separation_deg(0, 90) == 90
    assert aspects.angular_separation_deg(0, 180) == 180
    assert aspects.angular_separation_deg(350, 10) == 20


def test_is_aspect_in_orb():
    in_orb, orb = aspects.is_aspect_in_orb(0, 90, 90, 8)
    assert in_orb is True
    in_orb2, _ = aspects.is_aspect_in_orb(0, 100, 90, 5)
    assert in_orb2 is False


def test_find_aspects():
    found = aspects.find_aspects(0, 180, orb_deg=10)
    assert any(t[0] == "opposition" for t in found)
    found2 = aspects.find_aspects(0, 120, orb_deg=8)
    assert any(t[0] == "trine" for t in found2)


def test_find_aspects_returns_orb_degrees_and_exact_angle():
    found = aspects.find_aspects(0, 92, orb_deg=10)
    assert any(t[0] == "square" for t in found)
    sq = [x for x in found if x[0] == "square"][0]
    name, exact_deg, orb_deg, applying = sq
    assert exact_deg == 90.0
    assert orb_deg == 2.0


def test_applying_separating_with_mocked_speeds():
    # Square at 88° separation: d=88, exact=90. dd/dt = speed_b - speed_a (delta in 0..180).
    # If speed_b > speed_a, d increases -> moving toward 90 -> applying.
    found = aspects.find_aspects(
        0, 88,
        orb_deg=5,
        speed1_deg_per_day=1.0,
        speed2_deg_per_day=1.5,
        body_a="Sun",
        body_b="Moon",
    )
    sq = [x for x in found if x[0] == "square"]
    assert len(sq) == 1
    assert sq[0][3] is True  # applying

    # Same 88° but Moon slower: d decreases -> separating
    found2 = aspects.find_aspects(
        0, 88,
        orb_deg=5,
        speed1_deg_per_day=1.5,
        speed2_deg_per_day=1.0,
        body_a="Sun",
        body_b="Moon",
    )
    sq2 = [x for x in found2 if x[0] == "square"]
    assert len(sq2) == 1
    assert sq2[0][3] is False  # separating


def test_default_orb_resolver_fallback_without_db():
    r = db_orbs.create_orb_resolver(db_path=None)
    assert r.get_orb("square", "Sun", "Moon") == 8.0
    assert r.get_orb("conjunction", "Sun", "Moon") == 10.0
    assert r.get_orb("quincunx", "Sun", "Moon") == 3.0


def test_db_resolver_in_memory_sqlite():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE kb_item_type (type_id TEXT PRIMARY KEY, code TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE kb_item (item_id TEXT PRIMARY KEY, type_id TEXT NOT NULL, code TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE kb_property_def (prop_id TEXT PRIMARY KEY, code TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE kb_item_property (item_id TEXT, prop_id TEXT, value_float REAL, PRIMARY KEY (item_id, prop_id))"
    )
    conn.execute("INSERT INTO kb_item_type VALUES ('t1', 'aspect')")
    conn.execute("INSERT INTO kb_item VALUES ('i_sq', 't1', 'square')")
    conn.execute("INSERT INTO kb_property_def VALUES ('p_orb', 'orb_deg')")
    conn.execute("INSERT INTO kb_item_property VALUES ('i_sq', 'p_orb', 6.0)")
    conn.commit()
    conn.close()

    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        path = f.name
    try:
        conn2 = sqlite3.connect(path)
        conn2.execute(
            "CREATE TABLE kb_item_type (type_id TEXT PRIMARY KEY, code TEXT NOT NULL)"
        )
        conn2.execute(
            "CREATE TABLE kb_item (item_id TEXT PRIMARY KEY, type_id TEXT NOT NULL, code TEXT NOT NULL)"
        )
        conn2.execute(
            "CREATE TABLE kb_property_def (prop_id TEXT PRIMARY KEY, code TEXT NOT NULL)"
        )
        conn2.execute(
            "CREATE TABLE kb_item_property (item_id TEXT, prop_id TEXT, value_float REAL, PRIMARY KEY (item_id, prop_id))"
        )
        conn2.execute("INSERT INTO kb_item_type VALUES ('t1', 'aspect')")
        conn2.execute("INSERT INTO kb_item VALUES ('i_sq', 't1', 'square')")
        conn2.execute("INSERT INTO kb_property_def VALUES ('p_orb', 'orb_deg')")
        conn2.execute("INSERT INTO kb_item_property VALUES ('i_sq', 'p_orb', 6.0)")
        conn2.commit()
        conn2.close()

        resolver = db_orbs.SqliteOrbResolver(path)
        assert resolver.get_orb("square", "Sun", "Moon") == 6.0
        assert resolver.get_orb("conjunction", "Sun", "Moon") == 10.0  # fallback
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def test_extended_aspects_quincunx():
    found = aspects.find_aspects(0, 150, aspects=aspects.EXTENDED_ASPECT_DEFS, orb_deg=4)
    assert any(t[0] == "quincunx" for t in found)
    found2 = aspects.find_aspects(0, 150, aspects=aspects.ASPECT_DEFS, orb_deg=4)
    assert not any(t[0] == "quincunx" for t in found2)
