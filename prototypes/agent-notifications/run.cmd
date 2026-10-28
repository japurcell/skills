@echo off
rem User-local prototype launcher. No administrator or PowerShell policy changes.
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -c "import PySide6; from PySide6.QtMultimedia import QSoundEffect; assert PySide6.__version__ == '6.12.0'" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install --only-binary=:all: --no-cache-dir -r requirements.txt
    if errorlevel 1 exit /b 1
)
if "%~1"=="" (
    ".venv\Scripts\python.exe" native_alerts.py open
) else (
    ".venv\Scripts\python.exe" native_alerts.py %*
)
exit /b %errorlevel%
