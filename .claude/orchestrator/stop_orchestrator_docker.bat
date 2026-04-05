@echo off
echo ========================================
echo Stopping Multi-Agent Orchestrator
echo ========================================
echo.

cd /d %~dp0

echo Stopping Docker containers...
docker-compose down

echo.
echo Killing frontend processes on port 3001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo All services stopped!
echo ========================================
echo.
pause
