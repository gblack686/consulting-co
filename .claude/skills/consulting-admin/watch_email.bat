@echo off
cd /d "C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\skills\consulting-admin"
python -m scripts.email_watcher >> logs\email_watcher.log 2>&1
