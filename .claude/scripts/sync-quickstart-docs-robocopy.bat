@echo off
setlocal enabledelayedexpansion

echo Starting QuickStart documentation sync...
echo ==========================================

set SOURCE_DIR=claude-repos
set TARGET_BASE=.

:: Array of QuickStart directories
set QUICKSTARTS=quickstart-acme-test-claude quickstart-agentcore-claude quickstart-board-director-claude quickstart-compcorrect-claude quickstart-nexus-claude quickstart-parenting-autism-claude quickstart-perl-street-claude quickstart-word-collections-claude

set TOTAL_FILES=0

for %%Q in (%QUICKSTARTS%) do (
    echo.
    echo [92mSyncing: %%Q[0m

    if exist "%SOURCE_DIR%\%%Q" (
        echo    Source: %SOURCE_DIR%\%%Q
        echo    Target: %TARGET_BASE%\%%Q

        :: Create target directory
        if not exist "%TARGET_BASE%\%%Q" mkdir "%TARGET_BASE%\%%Q"

        :: Use robocopy to sync markdown and text files, excluding cloud folders and .git
        :: /E = copy subdirectories including empty ones
        :: /XD = exclude directories
        :: /XF = exclude files
        :: /IS = include same files (overwrite)
        :: /IT = include tweaked files
        :: /NJH /NJS /NFL /NDL = minimal output

        robocopy "%SOURCE_DIR%\%%Q" "%TARGET_BASE%\%%Q" *.md *.txt /E /XD cloud .git node_modules /IS /IT /NP /R:1 /W:1

        if !ERRORLEVEL! LEQ 7 (
            echo    [92mDone syncing %%Q[0m
        ) else (
            echo    [93mWarning: Some issues during sync of %%Q[0m
        )
    ) else (
        echo    [93mWarning: %%Q directory not found[0m
    )
)

echo.
echo ==========================================
echo [92mQuickStart documentation sync complete![0m
echo.
echo Documentation has been synced to:
for %%Q in (%QUICKSTARTS%) do (
    if exist "%TARGET_BASE%\%%Q" (
        echo   - %%Q/
    )
)
echo.

pause
