@echo off
REM Builds the static site into ..\natiga so it can be published on GitHub Pages.
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo.
    echo   [ERROR] Setup has not been run yet.
    echo   Double-click setup.bat first.
    echo.
    pause
    exit /b 1
)

venv\Scripts\python.exe build_static.py --clean
echo.
pause
