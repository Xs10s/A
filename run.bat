@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%\src
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8001
python -m uvicorn app.main:app --host %HOST% --port %PORT%
pause
