@echo off
cd /d "C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\consulting-admin"
python -m scripts.calendar_watcher >> logs\calendar_watcher.log 2>&1
