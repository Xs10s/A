from __future__ import annotations

from datetime import date
import json
import logging
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request as UrlRequest, urlopen
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from horoscoop import engine
from horoscoop.energy_profile import build_energy_profile, build_combined_energy_profile
from horoscoop.cross_system import build_cross_system
from horoscoop.presentation import (
    build_view_model,
    render_wheel_from_engine,
    render_pdf,
    render_section_svg,
)
from horoscoop.interpretations import build_interpretations
from . import chart as chart_mod

_APP_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _APP_DIR / "static"

app = FastAPI(title="Horoscoop Engine API")
templates = Jinja2Templates(directory=str(_APP_DIR / "templates"))
if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


class HoroscoopRequest(BaseModel):
    birth_date: date
    birth_time_local: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    elevation_m: Optional[float] = None
    timezone_iana: Optional[str] = None
    utc_offset_minutes: Optional[int] = None
    utc_offset_hours: Optional[float] = None
    house_system: Optional[str] = Field(default=None)
    ayanamsha_mode: Optional[str] = Field(default=None)
    vedic_at: Optional[str] = Field(default=None)
    vedic_sunrise_method: Optional[str] = Field(default=None)
    chinese_year_boundary: Optional[str] = Field(default=None)
    chinese_day_boundary: Optional[str] = Field(default=None)
    chinese_timezone_for_calendar: Optional[str] = Field(default=None)
    chinese_include_solar_terms: Optional[bool] = Field(default=None)
    western_orb_profile: Optional[str] = Field(default=None)
    western_db_path: Optional[str] = Field(default=None)
    western_extended_aspects: Optional[bool] = Field(default=None)


def _geocode_city(city: str) -> Optional[dict[str, Any]]:
    """
    Resolve city name to {lat, lon, timezone_iana?}.

    Uses Open-Meteo geocoding API (no key) because Nominatim often blocks
    generic server-side traffic (HTTP 403).
    """
    try:
        params = urlencode(
            {"name": city, "count": 1, "language": "en", "format": "json"}
        )
        url = f"https://geocoding-api.open-meteo.com/v1/search?{params}"
        req = UrlRequest(url)
        req.add_header("User-Agent", "horoscoop-ui/1.0")
        with urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        results = data.get("results") if isinstance(data, dict) else None
        if not results:
            return None
        first = results[0]
        lat = float(first["latitude"])
        lon = float(first["longitude"])
        tz = first.get("timezone")
        return {"lat": lat, "lon": lon, "timezone_iana": tz}
    except Exception:  # pragma: no cover - network / parsing issues
        logging.exception("Geocoding failed for city=%r", city)
        return None


_TF = None


def _timezone_from_latlon(lat: float, lon: float) -> Optional[str]:
    """Resolve IANA timezone from coordinates (WGS84)."""
    global _TF
    try:
        if _TF is None:
            from timezonefinder import TimezoneFinder  # type: ignore

            _TF = TimezoneFinder()
        tz = _TF.timezone_at(lat=lat, lng=lon)  # e.g. "Europe/Amsterdam"
        return tz
    except Exception:  # pragma: no cover
        logging.exception("Timezone lookup failed for lat=%r lon=%r", lat, lon)
        return None


_PLACE_CACHE: dict[str, dict[str, Any]] = {}


def _resolve_place(city: str) -> dict[str, Any]:
    """
    Resolve city -> {lat, lon, timezone_iana}.
    Cached in-memory to reduce external calls.
    """
    key = (city or "").strip().lower()
    if not key:
        return {"ok": False, "error": "city_required"}
    cached = _PLACE_CACHE.get(key)
    if cached:
        return {"ok": True, "city": city, **cached, "cached": True}
    hit = _geocode_city(city)
    if hit is None:
        return {"ok": False, "error": "city_not_found"}
    lat = hit.get("lat")
    lon = hit.get("lon")
    tz = hit.get("timezone_iana")
    if tz is None and lat is not None and lon is not None:
        tz = _timezone_from_latlon(float(lat), float(lon))
    result = {"lat": lat, "lon": lon, "timezone_iana": tz}
    _PLACE_CACHE[key] = result
    return {"ok": True, "city": city, **result, "cached": False}


def _call_engine(payload: HoroscoopRequest) -> Dict[str, Any]:
    data = payload.model_dump()
    lat = data.get("lat")
    lon = data.get("lon")
    timezone_iana = data.get("timezone_iana")
    if (lat is None or lon is None or timezone_iana is None) and data.get("city"):
        hit = _geocode_city(data["city"])
        if hit is not None:
            if lat is None:
                lat = hit.get("lat")
            if lon is None:
                lon = hit.get("lon")
            if timezone_iana is None:
                timezone_iana = hit.get("timezone_iana")
    if timezone_iana is None and lat is not None and lon is not None and data.get("city"):
        tz = _timezone_from_latlon(float(lat), float(lon))
        if tz:
            timezone_iana = tz

    kwargs: Dict[str, Any] = {
        "birth_date": payload.birth_date.isoformat(),
        "birth_time_local": data.get("birth_time_local"),
        "lat": lat,
        "lon": lon,
        "elevation_m": data.get("elevation_m"),
        "timezone_iana": timezone_iana,
        "utc_offset_hours": data.get("utc_offset_hours"),
        "utc_offset_minutes": data.get("utc_offset_minutes"),
    }
    if payload.house_system:
        kwargs["house_system"] = payload.house_system
    if payload.ayanamsha_mode:
        kwargs["ayanamsha_mode"] = payload.ayanamsha_mode
    if payload.chinese_year_boundary:
        kwargs["chinese_year_boundary"] = payload.chinese_year_boundary
    if payload.chinese_day_boundary:
        kwargs["chinese_day_boundary"] = payload.chinese_day_boundary
    if payload.chinese_timezone_for_calendar:
        kwargs["chinese_timezone_for_calendar"] = payload.chinese_timezone_for_calendar
    if payload.chinese_include_solar_terms is not None:
        kwargs["chinese_include_solar_terms"] = payload.chinese_include_solar_terms
    if payload.vedic_at:
        kwargs["vedic_at"] = payload.vedic_at
    if payload.vedic_sunrise_method:
        kwargs["vedic_sunrise_method"] = payload.vedic_sunrise_method
    if payload.western_orb_profile:
        kwargs["western_orb_profile"] = payload.western_orb_profile
    if payload.western_db_path:
        kwargs["western_db_path"] = payload.western_db_path
    if payload.western_extended_aspects is not None:
        kwargs["western_extended_aspects"] = payload.western_extended_aspects
    return engine.compute(**kwargs)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/resolve-place")
async def api_resolve_place(payload: Dict[str, Any] = Body(...)):
    city = (payload.get("city") or "").strip()
    return JSONResponse(_resolve_place(city))


@app.post("/api/horoscoop")
async def api_horoscoop(payload: HoroscoopRequest):
    result = _call_engine(payload)
    return JSONResponse(result)


@app.post("/api/viewmodel")
async def api_viewmodel(payload: HoroscoopRequest, locale: Optional[str] = "nl-NL"):
    result = _call_engine(payload)
    vm = build_view_model(result, locale=locale)
    return JSONResponse(vm)


_ALLOWED_ENERGY_SYSTEMS = (
    "western_tropical",
    "western_sidereal",
    "vedic_panchanga",
    "chinese_bazi",
    "human_design",
    "maya",
)


@app.post("/api/energy-profile")
async def api_energy_profile(
    payload: HoroscoopRequest,
    system: Optional[str] = "western_tropical",
    locale: Optional[str] = "nl-NL",
):
    """
    Generate an energy profile (scores + evidence + narrative) derived from engine output.
    system: western_tropical | western_sidereal | vedic_panchanga | chinese_bazi |
            human_design | maya
    """
    result = _call_engine(payload)
    sys_id = (system or "western_tropical").strip().lower()
    if sys_id not in _ALLOWED_ENERGY_SYSTEMS:
        return JSONResponse(
            {"error": "invalid_system", "allowed": list(_ALLOWED_ENERGY_SYSTEMS)},
            status_code=400,
        )
    prof = build_energy_profile(result, system=sys_id, locale=locale or "nl-NL")  # type: ignore[arg-type]
    return JSONResponse(prof)


@app.post("/api/cross-system")
async def api_cross_system(payload: HoroscoopRequest, locale: Optional[str] = "nl-NL"):
    """
    Cross-system intelligence: element/polarity/decision/timing resonances
    across Western, Vedic, BaZi, Human Design, Maya.
    """
    result = _call_engine(payload)
    cs = build_cross_system(result, locale=locale or "nl-NL")
    return JSONResponse(cs)


@app.post("/api/energy-profile/combined")
async def api_energy_profile_combined(
    payload: HoroscoopRequest,
    locale: Optional[str] = "nl-NL",
):
    """
    Generate a combined multi-system energy profile (Western, Vedic, Chinese).
    """
    result = _call_engine(payload)
    prof = build_combined_energy_profile(result, locale=locale or "nl-NL")
    return JSONResponse(prof)


@app.post("/api/interpretations")
async def api_interpretations(payload: HoroscoopRequest, locale: Optional[str] = "nl-NL"):
    """
    Extended meaning lookup for computed values across methods.
    """
    result = _call_engine(payload)
    # build_interpretations expects NL/EN; it will normalize internally.
    out = build_interpretations(result, locale=locale or "nl-NL")
    return JSONResponse(out)


@app.get("/api/horoscoop/schema")
async def api_schema():
    from pathlib import Path
    import json

    schema_path = Path("src/horoscoop/json_schema.json")
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    return JSONResponse(data)


@app.post("/api/horoscoop/report.pdf")
async def api_report_pdf(payload: HoroscoopRequest):
    """Volledig rapport: alle methodes + ingebedde wielen/banners (presentation layer)."""
    result = _call_engine(payload)
    pdf_bytes = render_pdf(result)
    return Response(content=pdf_bytes, media_type="application/pdf")


@app.post("/api/horoscoop/chart.svg")
async def api_chart_svg(payload: HoroscoopRequest):
    result = _call_engine(payload)
    svg = chart_mod.build_svg(result)
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/api/horoscoop/chart.png")
async def api_chart_png(payload: HoroscoopRequest):
    result = _call_engine(payload)
    png_bytes = chart_mod.build_png(result)
    if png_bytes is None:
        # Fallback to SVG when PNG rendering is not available
        svg = chart_mod.build_svg(result)
        return Response(content=svg, media_type="image/svg+xml")
    return Response(content=png_bytes, media_type="image/png")


def _body_to_engine_json(body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """If body has engine output structure, return it. Else None."""
    if body.get("meta") and body.get("time") and body.get("astronomy"):
        return body
    return None


def _body_to_horoscoop_request(body: Dict[str, Any]) -> HoroscoopRequest:
    """Build HoroscoopRequest from dict (e.g. JSON body)."""
    bd = body.get("birth_date")
    if isinstance(bd, str):
        bd = date.fromisoformat(bd)
    return HoroscoopRequest(
        birth_date=bd or date(2000, 1, 1),
        birth_time_local=body.get("birth_time_local"),
        city=body.get("city"),
        lat=body.get("lat"),
        lon=body.get("lon"),
        elevation_m=body.get("elevation_m"),
        timezone_iana=body.get("timezone_iana"),
        utc_offset_minutes=body.get("utc_offset_minutes"),
        utc_offset_hours=body.get("utc_offset_hours"),
        house_system=body.get("house_system"),
        ayanamsha_mode=body.get("ayanamsha_mode"),
        vedic_at=body.get("vedic_at"),
        vedic_sunrise_method=body.get("vedic_sunrise_method"),
        chinese_year_boundary=body.get("chinese_year_boundary"),
        chinese_day_boundary=body.get("chinese_day_boundary"),
        chinese_timezone_for_calendar=body.get("chinese_timezone_for_calendar"),
        chinese_include_solar_terms=body.get("chinese_include_solar_terms"),
        western_orb_profile=body.get("western_orb_profile"),
        western_db_path=body.get("western_db_path"),
        western_extended_aspects=body.get("western_extended_aspects"),
    )


@app.post("/api/render/wheel.svg")
async def api_render_wheel_svg(
    payload: Dict[str, Any] = Body(...),
):
    """Render SVG wheel. Body: engine_json (or birth_date+params) + method_id."""
    body = payload
    method_id = body.get("method_id") or "western_tropical"
    engine_json = body.get("engine_json") or _body_to_engine_json(body)
    if engine_json is None and body.get("birth_date"):
        req = _body_to_horoscoop_request(body)
        engine_json = _call_engine(req)
    if engine_json is None:
        return JSONResponse({"error": "engine_json or birth_date required"}, status_code=400)
    svg = render_wheel_from_engine(engine_json, method_id=method_id)
    return Response(content=svg, media_type="image/svg+xml")


_SECTION_SVG_ALLOWED = frozenset(
    (
        "western_tropical", "western_sidereal", "vedic_panchanga", "chinese_bazi",
        "human_design", "maya",
    )
)


@app.post("/api/render/section.svg")
async def api_render_section_svg(payload: Dict[str, Any] = Body(...)):
    """
    UI preview: één SVG per onderdeel (tropisch wiel, sidereaals wiel, Panchanga, BaZi).
    Body: engine_json of birth_* + section.
    """
    body = payload
    section = (body.get("section") or "").strip().lower()
    locale = (body.get("locale") or "nl-NL")
    engine_json = body.get("engine_json") or _body_to_engine_json(body)
    if engine_json is None and body.get("birth_date"):
        req = _body_to_horoscoop_request(body)
        engine_json = _call_engine(req)
    if engine_json is None:
        return JSONResponse({"error": "engine_json or birth_date required"}, status_code=400)
    if section not in _SECTION_SVG_ALLOWED:
        return JSONResponse(
            {"error": "invalid_section", "allowed": sorted(_SECTION_SVG_ALLOWED)},
            status_code=400,
        )
    try:
        svg = render_section_svg(engine_json, section, locale=locale)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/api/render/report.pdf")
async def api_render_report_pdf(
    payload: Dict[str, Any] = Body(...),
):
    """Render PDF report. Body: engine_json (or birth_date+params) + template_id, locale."""
    body = payload
    template_id = body.get("template_id") or "default_report"
    engine_json = body.get("engine_json") or _body_to_engine_json(body)
    if engine_json is None and body.get("birth_date"):
        req = _body_to_horoscoop_request(body)
        engine_json = _call_engine(req)
    if engine_json is None:
        return JSONResponse({"error": "engine_json or birth_date required"}, status_code=400)
    pdf_bytes = render_pdf(engine_json, template_id=template_id)
    return Response(content=pdf_bytes, media_type="application/pdf")

