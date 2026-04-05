@echo off
REM Quick install script for Anthropic Memory Tool (Windows)
REM Makes the skill available globally across all Claude Code sessions

echo ================================================
echo Anthropic Memory Tool - Global Installation
echo ================================================
echo.

REM Create global directories
echo Creating global directories...
mkdir "%USERPROFILE%\.claude\skills" 2>nul
mkdir "%USERPROFILE%\.claude\hooks" 2>nul
mkdir "%USERPROFILE%\.claude\memories\sessions" 2>nul
mkdir "%USERPROFILE%\.claude\memories\patterns" 2>nul
mkdir "%USERPROFILE%\.claude\memories\entities" 2>nul

REM Copy skill
echo Copying skill files...
xcopy /E /I /Y ".claude\skills\anthropic-memory" "%USERPROFILE%\.claude\skills\anthropic-memory\"

REM Copy hook
echo Copying Stop hook...
copy /Y ".claude\hooks\memory_ingest_hook.py" "%USERPROFILE%\.claude\hooks\memory_ingest_hook.py"

REM Update config for global paths
echo Updating configuration for global paths...
powershell -Command "(Get-Content '%USERPROFILE%\.claude\skills\anthropic-memory\config\memory-config.yaml') -replace 'memory_base_path: .claude/memories', 'memory_base_path: %USERPROFILE%/.claude/memories' | Set-Content '%USERPROFILE%\.claude\skills\anthropic-memory\config\memory-config.yaml'"

REM Create global settings file
echo Creating global settings file...
(
echo {
echo   "hooks": {
echo     "Stop": [
echo       {
echo         "command": "uv run %USERPROFILE%\.claude\hooks\memory_ingest_hook.py",
echo         "timeout": 15
echo       }
echo     ]
echo   }
echo }
) > "%USERPROFILE%\.claude\settings.json"

echo.
echo ================================================
echo ✅ Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Open a NEW Claude Code terminal (in any directory)
echo 2. Run: uv run %USERPROFILE%\.claude\skills\anthropic-memory\tests\test_memory_system.py
echo 3. Have a conversation and exit (Ctrl+C)
echo 4. Check: dir %USERPROFILE%\.claude\memories\sessions
echo.
echo Memory files will be stored in:
echo   %USERPROFILE%\.claude\memories\
echo.
pause
