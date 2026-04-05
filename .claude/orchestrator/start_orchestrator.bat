@echo off
echo ========================================
echo Multi-Agent Orchestration Platform
echo ========================================
echo.

REM Check if backend is already running
tasklist /FI "WINDOWTITLE eq Orchestrator Backend*" 2>NUL | find /I /N "python">NUL
if "%ERRORLEVEL%"=="0" (
    echo Backend already running, skipping...
) else (
    echo Starting Backend (FastAPI + WebSocket)...
    start "Orchestrator Backend" cmd /k "cd /d %~dp0orchestrator_3_stream\backend && uv run python main.py"
    timeout /t 5 /nobreak >nul
)

REM Check if frontend is already running
tasklist /FI "WINDOWTITLE eq Orchestrator Frontend*" 2>NUL | find /I /N "bun">NUL
if "%ERRORLEVEL%"=="0" (
    echo Frontend already running, skipping...
) else (
    echo Starting Frontend (Vue 3 + WebSocket)...
    start "Orchestrator Frontend" cmd /k "cd /d %~dp0orchestrator_3_stream\frontend && bun run dev"
    timeout /t 3 /nobreak >nul
)

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Backend API:      http://localhost:8000
echo WebSocket:        ws://localhost:8000/ws
echo Frontend UI:      http://localhost:3001
echo.
echo Opening UI in 10 seconds...
echo Press Ctrl+C to cancel
echo.

timeout /t 10 /nobreak >nul
start http://localhost:3001

echo.
echo Dashboard opened!
echo Press any key to exit (services will continue running)...
pause >nul
