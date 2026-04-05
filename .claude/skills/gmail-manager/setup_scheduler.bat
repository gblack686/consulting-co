@echo off
REM Gmail Digest Scheduler Setup
REM Run this script as Administrator to create Windows scheduled tasks

echo ============================================
echo Gmail Digest - Windows Task Scheduler Setup
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%scripts\digest_runner.py

REM Find Python executable
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and in your PATH
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON_EXE=%%i
echo Found Python: %PYTHON_EXE%
echo Script path: %PYTHON_SCRIPT%
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Not running as Administrator
    echo Some scheduled task operations may fail
    echo.
)

echo Creating scheduled tasks...
echo.

REM Delete existing tasks if they exist (ignore errors)
schtasks /delete /tn "Gmail Digest - Morning" /f >nul 2>&1
schtasks /delete /tn "Gmail Digest - Afternoon" /f >nul 2>&1
schtasks /delete /tn "Gmail Digest - Evening" /f >nul 2>&1

REM Morning digest at 7:00 AM
echo Creating Morning digest task (7:00 AM)...
schtasks /create /tn "Gmail Digest - Morning" ^
    /tr "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\" --action classify-and-digest --type morning" ^
    /sc daily /st 07:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Morning task created
) else (
    echo   [FAILED] Could not create morning task
)

REM Afternoon digest at 1:00 PM
echo Creating Afternoon digest task (1:00 PM)...
schtasks /create /tn "Gmail Digest - Afternoon" ^
    /tr "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\" --action classify-and-digest --type afternoon" ^
    /sc daily /st 13:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Afternoon task created
) else (
    echo   [FAILED] Could not create afternoon task
)

REM Evening digest at 6:00 PM
echo Creating Evening digest task (6:00 PM)...
schtasks /create /tn "Gmail Digest - Evening" ^
    /tr "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\" --action classify-and-digest --type evening" ^
    /sc daily /st 18:00 /f
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Evening task created
) else (
    echo   [FAILED] Could not create evening task
)

echo.
echo ============================================
echo Scheduled Tasks Summary
echo ============================================
echo.

schtasks /query /tn "Gmail Digest - Morning" /fo list 2>nul
if %ERRORLEVEL% NEQ 0 echo Morning task: NOT FOUND
echo.

schtasks /query /tn "Gmail Digest - Afternoon" /fo list 2>nul
if %ERRORLEVEL% NEQ 0 echo Afternoon task: NOT FOUND
echo.

schtasks /query /tn "Gmail Digest - Evening" /fo list 2>nul
if %ERRORLEVEL% NEQ 0 echo Evening task: NOT FOUND
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Your Gmail digests will run 3x daily:
echo   - Morning:   7:00 AM
echo   - Afternoon: 1:00 PM
echo   - Evening:   6:00 PM
echo.
echo To test a digest manually, run:
echo   python "%PYTHON_SCRIPT%" --action classify-and-digest --type now
echo.
echo To view logs:
echo   %SCRIPT_DIR%logs\
echo.

pause
