@echo off
title GBAutomation - Personal Calendar Auth Setup
cd /d "C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\consulting-admin"
echo.
echo ============================================================
echo   GBAutomation - Personal Calendar OAuth Setup
echo   Log in as gblack686@gmail.com when the browser opens
echo ============================================================
echo.
python -m scripts.setup_personal_calendar_auth
echo.
pause
