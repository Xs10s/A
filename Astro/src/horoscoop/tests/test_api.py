"""
Minimal API tests for FastAPI wrapper.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_horoscoop_minimal_birth_date_only():
    resp = client.post("/api/horoscoop", json={"birth_date": "2000-01-01"})
    assert resp.status_code == 200
    data = resp.json()
    assert "time" in data
    assert "diagnostics" in data


def test_api_report_pdf_content_type():
    resp = client.post("/api/horoscoop/report.pdf", json={"birth_date": "2000-01-01"})
    assert resp.status_code == 200
    ct = resp.headers.get("content-type", "")
    assert ct.startswith("application/pdf")
    assert len(resp.content) > 0


def test_api_chart_svg_content_type():
    resp = client.post("/api/horoscoop/chart.svg", json={"birth_date": "2000-01-01"})
    assert resp.status_code == 200
    ct = resp.headers.get("content-type", "")
    assert ct.startswith("image/svg+xml")
    assert resp.content.startswith(b"<svg")


def test_api_viewmodel():
    resp = client.post("/api/viewmodel", json={"birth_date": "2000-01-01", "utc_offset_hours": 1.0})
    assert resp.status_code == 200
    data = resp.json()
    assert "methods" in data
    assert "input_summary" in data
    assert "diagnostics" in data


def test_api_render_wheel_svg():
    resp = client.post(
        "/api/render/wheel.svg",
        json={"birth_date": "2000-01-01", "utc_offset_hours": 1.0, "method_id": "western_tropical"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("image/svg+xml")
    assert b"<svg" in resp.content


def test_api_render_report_pdf():
    resp = client.post(
        "/api/render/report.pdf",
        json={"birth_date": "2000-01-01", "utc_offset_hours": 1.0},
    )
    assert resp.status_code == 200
    assert resp.headers.get("content-type", "").startswith("application/pdf")
    assert resp.content.startswith(b"%PDF")


def test_api_schema_get():
    resp = client.get("/api/horoscoop/schema")
    assert resp.status_code == 200
    data = resp.json()
    assert "$schema" in data or "properties" in data

