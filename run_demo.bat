@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_demo.ps1"
if errorlevel 1 (
    echo.
    echo 启动失败，请查看上方错误信息。
    echo 如果窗口中提示端口被占用，请关闭旧的 FastAPI / Streamlit 命令行窗口后重试。
    echo.
    pause
) else (
    echo.
    echo 启动命令已完成，前端页面会自动打开。
    timeout /t 3 >nul
)
endlocal
