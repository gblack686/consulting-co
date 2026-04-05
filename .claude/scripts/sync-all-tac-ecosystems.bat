@echo off
REM ============================================================
REM Sync All TAC .claude Ecosystems to Obsidian
REM ============================================================
REM
REM This script processes all .claude directories from TAC projects
REM and syncs them to the Obsidian AI-Agent-KB.
REM
REM Usage: Run this script, then execute each claude command manually
REM        or pipe to claude CLI for automated processing.
REM
REM ============================================================

setlocal enabledelayedexpansion

set "LOG_FILE=%USERPROFILE%\.claude\logs\tac-ecosystem-sync.log"
set "TIMESTAMP=%date:~-4%-%date:~4,2%-%date:~7,2%_%time:~0,2%%time:~3,2%"
set "COUNT=0"
set "TOTAL=24"

echo ============================================================ > "%LOG_FILE%"
echo TAC Ecosystem Sync Started: %TIMESTAMP% >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"
echo.

echo TAC Ecosystem Sync - Processing %TOTAL% directories
echo ============================================================
echo.

REM TAC Level 1 Projects (12)
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\agent-experts\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\agent-sandbox-skill\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\agent-sandboxes\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\agentic-finance-review\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\building-domain-specific-agents\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\claude-code-damage-control\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\claude-code-hooks-mastery\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\fork-repository-skill\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration-the-o-agent\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\rd-framework-context-window-mastery\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\seven-levels-agentic-prompt-formats\.claude"

REM TAC Numbered Projects (7)
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-1\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-2\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-3\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-4\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-5\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-6\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-7\.claude"

REM TAC-8 Sub-Projects (5)
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app1__agent_layer_primitives\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app2__multi_agent_todone\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app3__out_loop_multi_agent_task_board\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app4__agentic_prototyping\.claude"
call :process_dir "C:\Users\gblac\OneDrive\Desktop\tac\tac-8\tac8_app5__nlq_to_sql_aea\.claude"

echo.
echo ============================================================
echo Sync Complete: %COUNT%/%TOTAL% directories processed
echo Log saved to: %LOG_FILE%
echo ============================================================

echo. >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"
echo Sync Complete: %COUNT%/%TOTAL% directories >> "%LOG_FILE%"
echo ============================================================ >> "%LOG_FILE%"

goto :eof

:process_dir
set /a COUNT+=1
set "DIR=%~1"

REM Extract project name from path
for %%I in ("%DIR%\..") do set "PROJECT=%%~nxI"

echo [%COUNT%/%TOTAL%] Processing: %PROJECT%
echo [%COUNT%/%TOTAL%] %PROJECT% >> "%LOG_FILE%"

REM Check if directory exists
if exist "%DIR%" (
    echo   Path: %DIR%
    echo   Status: Ready for sync
    echo   Command: claude -p "/sync-claude-ecosystem %DIR%"
    echo.

    REM Uncomment below to actually run the sync
    REM claude -p "/sync-claude-ecosystem %DIR%" --dangerously-skip-permissions

    echo   Path: %DIR% >> "%LOG_FILE%"
    echo   Status: Ready >> "%LOG_FILE%"
) else (
    echo   ERROR: Directory not found
    echo   ERROR: Directory not found >> "%LOG_FILE%"
)

goto :eof
