@echo off
REM Drag the results file onto this icon to import it.
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo.
    echo   [ERROR] Setup has not been run yet.
    echo   Double-click setup.bat first.
    echo.
    pause
    exit /b 1
)

if "%~1"=="" (
    echo.
    echo   Drag the results file ^(xlsx / csv^) and drop it on this file.
    echo.
    pause
    exit /b 1
)

venv\Scripts\python.exe import_results.py "%~1" --confirm
echo.
pause
