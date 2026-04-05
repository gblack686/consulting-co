@echo off
setlocal
set LOG_DIR=C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\consulting-admin\logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
cd /d "C:\Users\gblac\OneDrive\Desktop\consulting-co"
claude -p "Read .claude/skills/consulting-admin/workflows/monday-client-digest.md and execute that workflow. Today is %date%. Save output to .claude/context/clients/" >> "%LOG_DIR%\monday-digest.log" 2>&1
