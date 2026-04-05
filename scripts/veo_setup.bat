@echo off
REM Veo 3.1 GCS Quick Setup Script for Windows

echo.
echo ========================================
echo Veo 3.1 with Google Cloud Storage Setup
echo ========================================
echo.

REM Check gcloud
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Error: gcloud CLI not found
    echo Install from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)
echo [OK] gcloud CLI installed

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Error: Python not found
    pause
    exit /b 1
)
echo [OK] Python installed

echo.
echo Installing Python packages...
python -m pip install google-cloud-storage requests --quiet
echo [OK] Packages installed

echo.
echo ========================================
echo Step 1: Authenticate with Google Cloud
echo ========================================
echo This will open a browser window...
echo.
gcloud auth application-default login

echo.
echo ========================================
echo Step 2: Set GCP Project
echo ========================================
echo.
set /p PROJECT_ID="Enter your GCP Project ID: "
gcloud config set project %PROJECT_ID%

echo.
echo ========================================
echo Step 3: Create GCS Bucket
echo ========================================
echo.
set BUCKET_NAME=veo-video-gen-%RANDOM%%RANDOM%
echo Creating bucket: %BUCKET_NAME%
gsutil mb gs://%BUCKET_NAME%/
echo [OK] Bucket created

echo.
echo ========================================
echo Step 4: Save Configuration
echo ========================================
echo.

REM Save to .env
echo VEO_GCS_BUCKET=%BUCKET_NAME%>> .env
echo GCP_PROJECT_ID=%PROJECT_ID%>> .env

echo [OK] Configuration saved to .env
echo.
echo Your setup:
echo   Project: %PROJECT_ID%
echo   Bucket: %BUCKET_NAME%
echo.

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Generate video from your frames:
echo.
echo      python "C:/Users/gblac/.claude/global/skills/veo-agent/scripts/interpolate_frames_gcs.py" ^
echo        option7_start.png option7_end.png ^
echo        "Your prompt here" ^
echo        --bucket %BUCKET_NAME%
echo.
echo   2. See full guide:
echo      type .claude\context\VEO_GCS_SETUP_GUIDE.md
echo.
pause
