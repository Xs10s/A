# Run the Horoscoop FastAPI app
# Usage: .\run.ps1   or   powershell -File run.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Add src to PYTHONPATH so horoscoop package can be imported
$env:PYTHONPATH = Join-Path $scriptDir "src"

# Self-host friendly defaults (override via HOST/PORT env vars)
if (-not $env:HOST) { $env:HOST = "0.0.0.0" }
if (-not $env:PORT) { $env:PORT = "8001" }

# Run without --reload (avoids Windows multiprocessing permission issues)
python -m uvicorn app.main:app --host $env:HOST --port $env:PORT
