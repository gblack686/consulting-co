@echo off
REM Get a secret from Supabase Vault
REM Usage: get-secret.bat SECRET_NAME

setlocal enabledelayedexpansion

set SECRET_NAME=%1
set SUPABASE_URL=https://unickqnwfheaczccvgbw.supabase.co

if "%SECRET_NAME%"=="" (
    echo Usage: get-secret.bat SECRET_NAME
    echo.
    echo Available secrets:
    echo   OPENAI_API_KEY, ANTHROPIC_API_KEY, LINEAR_API_KEY, GOOGLE_AI_API_KEY,
    echo   JINA_AI_API_KEY, YOUTUBE_API_KEY, GITHUB_PAT_GBLACK686, NIH_GITHUB_PAT,
    echo   INFRASTRUCTURE_SUPABASE, INFRASTRUCTURE_LANGFUSE, NEO4J_GRAPHITI,
    echo   CLI_DEFAULT, LANGFUSE_S3, AMPLIFY, POSTGRES_PASSWORD, TELEGRAM,
    echo   GOOGLE_SERVICE_ACCOUNT, APIFY_API_TOKEN, APIFY_TOKEN, REF_TOOLS_API_KEY,
    echo   ANTHROPIC, API_KEY, CREDENTIALS
    exit /b 1
)

if "%SUPABASE_SERVICE_KEY%"=="" (
    echo Error: SUPABASE_SERVICE_KEY environment variable not set
    echo Set it with: set SUPABASE_SERVICE_KEY=your-service-key
    exit /b 1
)

curl -s -X POST "%SUPABASE_URL%/rest/v1/rpc/get_secret" ^
    -H "apikey: %SUPABASE_SERVICE_KEY%" ^
    -H "Authorization: Bearer %SUPABASE_SERVICE_KEY%" ^
    -H "Content-Type: application/json" ^
    -d "{\"secret_name\": \"%SECRET_NAME%\"}"

endlocal
