@echo off
setlocal enabledelayedexpansion

echo Starting QuickStart documentation sync...
echo ==========================================

set SOURCE_DIR=claude-repos
set TARGET_BASE=.

:: Array of QuickStart directories
set QUICKSTARTS=quickstart-acme-test-claude quickstart-agentcore-claude quickstart-board-director-claude quickstart-compcorrect-claude quickstart-nexus-claude quickstart-parenting-autism-claude quickstart-perl-street-claude quickstart-word-collections-claude

for %%Q in (%QUICKSTARTS%) do (
    echo.
    echo Syncing: %%Q

    if exist "%SOURCE_DIR%\%%Q" (
        echo    Source: %SOURCE_DIR%\%%Q
        echo    Target: %TARGET_BASE%\%%Q

        :: Create target directory
        if not exist "%TARGET_BASE%\%%Q" mkdir "%TARGET_BASE%\%%Q"

        :: Copy all markdown and text files, excluding cloud folders
        xcopy /E /I /Y /Q "%SOURCE_DIR%\%%Q\*.md" "%TARGET_BASE%\%%Q\" >nul 2>&1
        xcopy /E /I /Y /Q "%SOURCE_DIR%\%%Q\*.txt" "%TARGET_BASE%\%%Q\" >nul 2>&1

        echo    Done syncing %%Q
    ) else (
        echo    Warning: %%Q directory not found
    )
)

echo.
echo ==========================================
echo QuickStart documentation sync complete!
echo.
echo Documentation has been synced to:
for %%Q in (%QUICKSTARTS%) do (
    if exist "%TARGET_BASE%\%%Q" (
        echo   - %%Q/
    )
)

pause
