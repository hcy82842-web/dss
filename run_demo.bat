@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_demo.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
if errorlevel 1 (
    echo.
    echo Demo startup failed. Please read the PowerShell message above.
    echo If a port is occupied, close old FastAPI / Streamlit windows and retry.
    echo.
    pause
) else (
    echo.
    echo Demo startup command completed. The browser should open automatically.
    powershell -NoProfile -Command "Start-Sleep -Seconds 3"
)
endlocal & exit /b %EXIT_CODE%
