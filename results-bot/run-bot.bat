@echo off
REM Starts the Telegram bot. Uses the venv interpreter directly, so no
REM "activate" step and no PowerShell execution-policy problems.
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo.
    echo   [ERROR] Setup has not been run yet.
    echo   Double-click setup.bat first.
    echo.
    pause
    exit /b 1
)

venv\Scripts\python.exe bot.py
echo.
pause
