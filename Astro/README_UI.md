# Horoscoop UI & API

This folder describes the FastAPI-based UI and API wrapper around the existing `horoscoop` engine.

## Backend (FastAPI)

- Entry point: `app/main.py`
- PDF report: `app/report.py`
- Chart rendering (SVG/PNG): `app/chart.py`
- HTML UI template: `app/templates/index.html`

### Quick start

Install dependencies and run:

```bash
pip install -r requirements.txt
```

**Windows** – run from the project root:

```powershell
.\run.ps1
```

Or:

```cmd
run.bat
```

**Alternatively** (any OS) – set `PYTHONPATH` so the `horoscoop` package is found:

```bash
# From project root
set PYTHONPATH=%CD%\src          # Windows cmd
$env:PYTHONPATH = ".\src"       # Windows PowerShell
export PYTHONPATH=./src         # Linux/macOS

python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

> **Note:** Use `python -m uvicorn` if `uvicorn` is not on your PATH. Omit `--reload` on Windows if you see multiprocessing permission errors.

Then open `http://127.0.0.1:8001/` in your browser.

### API endpoints

- `POST /api/horoscoop` – compute full horoscope. Body:
  - `birth_date` (required, `YYYY-MM-DD`)
  - optional: `birth_time_local`, `lat`, `lon`, `timezone_iana`, `utc_offset_minutes`, `house_system`, `ayanamsha_mode`, `vedic_at`, `chinese_year_boundary`, etc.
- `GET /api/horoscoop/schema` – returns `json_schema.json`.
- `POST /api/horoscoop/report.pdf` – same body as `/api/horoscoop`, returns a PDF report.
- `POST /api/horoscoop/chart.svg` – returns an SVG chart (zodiac + planets, houses if available).
- `POST /api/horoscoop/chart.png` – returns PNG when `cairosvg` is installed, otherwise SVG as fallback.

## Frontend (minimal UI)

The UI is a single page rendered via Jinja2 (`app/templates/index.html`):

- Required field: `birth_date`.
- Optional advanced fields:
  - `birth_time_local`
  - `lat`, `lon`
  - `timezone_iana`, `utc_offset_minutes`
  - `house_system`, `ayanamsha_mode`
  - `vedic_at`, `chinese_year_boundary`
- Tabs:
  - Western
  - Sidereal (astronomy block)
  - Vedic
  - Chinese
  - BaZi
  - Raw JSON (with copy button)
- Download buttons:
  - JSON (`/api/horoscoop`)
  - PDF (`/api/horoscoop/report.pdf`)
  - Chart SVG (`/api/horoscoop/chart.svg`)

