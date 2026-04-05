@echo off
REM Daily YouTube Liked Videos Scanner
REM Scheduled via Windows Task Scheduler — runs every 24h
cd /d "C:\Users\gblac\OneDrive\Desktop\consulting-co"
python .claude\scripts\youtube_liked_scanner.py >> .claude\context\youtube-likes\scan.log 2>&1
