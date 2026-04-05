@echo off
echo ========================================
echo Multi-Agent Orchestration Platform
echo (Docker Backend + Windows Frontend)
echo ========================================
echo.

REM Navigate to orchestrator directory
cd /d %~dp0

echo Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not installed or not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo.
echo Starting Backend in Docker container...
docker-compose up -d --build

echo.
echo Waiting for backend to be ready...
timeout /t 10 /nobreak >nul

REM Check if backend is healthy
echo Checking backend health...
curl -f http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Backend may still be starting up...
    echo Check Docker logs: docker-compose logs -f orchestrator-backend
)

echo.
echo Starting Frontend (Vue 3)...
start "Orchestrator Frontend" cmd /k "cd /d %~dp0orchestrator_3_stream\frontend && bun run dev"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Backend (Docker):  http://localhost:8000
echo   - API Docs:      http://localhost:8000/docs
echo   - Health Check:  http://localhost:8000/health
echo   - WebSocket:     ws://localhost:8000/ws
echo.
echo Frontend:          http://localhost:3001
echo.
echo Docker Commands:
echo   - View logs:     docker-compose logs -f
echo   - Stop:          docker-compose down
echo   - Restart:       docker-compose restart
echo.
echo Opening UI in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3001

echo.
echo Press any key to exit (services will continue running)...
pause >nul
