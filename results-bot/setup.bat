@echo off
REM Wrapper: runs setup.py with whichever Python is available.
REM Kept ASCII-only on purpose - Arabic text lives in setup.py, which
REM prints Unicode to the Windows console reliably.
cd /d "%~dp0"

set "PY="
python --version >nul 2>&1
if %errorlevel%==0 set "PY=python"
py --version >nul 2>&1
if %errorlevel%==0 if not defined PY set "PY=py"

if not defined PY (
    echo.
    echo   [ERROR] Python was not found.
    echo.
    echo   Install it from https://www.python.org/downloads/
    echo   IMPORTANT: tick "Add Python to PATH" on the first screen.
    echo.
    pause
    exit /b 1
)

%PY% setup.py
echo.
pause
