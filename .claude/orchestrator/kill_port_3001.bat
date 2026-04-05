@echo off
echo Killing processes on port 3001...

REM Find and kill process listening on port 3001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
    echo Killing PID: %%a
    taskkill /F /PID %%a
)

echo.
echo Port 3001 is now free!
timeout /t 2 /nobreak >nul
