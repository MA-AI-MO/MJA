@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required to rebuild data.
  pause
  exit /b 1
)

echo Installing/updating required packages...
python -m pip install -r requirements.txt

echo Rebuilding tier hierarchy and review data...
python scripts\build_tiers.py
python scripts\refresh_review_data.py

echo Rebuild complete.
pause
