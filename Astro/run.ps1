# Run the Horoscoop FastAPI app
# Usage: .\run.ps1   or   powershell -File run.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Add src to PYTHONPATH so horoscoop package can be imported
$env:PYTHONPATH = Join-Path $scriptDir "src"

# Run without --reload (avoids Windows multiprocessing permission issues)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
