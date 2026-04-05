@echo off
REM Get a secret from AWS Secrets Manager
REM Usage: get-secret-aws.bat AWS_SECRET_NAME

set SECRET_NAME=%1

if "%SECRET_NAME%"=="" (
    echo Usage: get-secret-aws.bat AWS_SECRET_NAME
    echo.
    echo Example: get-secret-aws.bat gbautomation/core/openai-api-key
    exit /b 1
)

aws secretsmanager get-secret-value --secret-id %SECRET_NAME% --query SecretString --output text
