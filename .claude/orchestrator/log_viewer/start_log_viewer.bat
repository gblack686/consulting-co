@echo off
REM Log Viewer Startup Script for Windows
REM Starts the log viewer on port 5998

echo =============================================
echo LOG VIEWER - Unified Orchestrator Log Browser
echo =============================================
echo.

REM Check if running from correct directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run from log_viewer directory.
    pause
    exit /b 1
)

REM Start the server
echo Starting server on http://localhost:5998
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 5998 --reload
