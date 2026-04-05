@echo off
echo ========================================
echo Orchestrator Backend Logs (Docker)
echo ========================================
echo.
echo Press Ctrl+C to exit log viewing
echo.

cd /d %~dp0
docker-compose logs -f orchestrator-backend
