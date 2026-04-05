@echo off
echo Waiting for Docker Desktop to start...
echo.

:wait_loop
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not ready yet... waiting 5 seconds
    timeout /t 5 /nobreak >nul
    goto wait_loop
)

echo Docker is ready!
echo.
echo Starting Neo4j container...
cd "C:\Users\gblac\OneDrive\Desktop\consulting-co\claude-repos\quickstart-board-director-claude\logging-service\graphiti-repo\mcp_server"
docker compose up -d neo4j

echo.
echo Waiting for Neo4j to be ready...
timeout /t 10 /nobreak

echo.
echo Checking Neo4j status...
docker ps | findstr neo4j

echo.
echo Neo4j should now be running on:
echo   - Browser: http://localhost:7474
echo   - Bolt: bolt://localhost:7687
echo   - Username: neo4j
echo   - Password: yourpassword
echo.
pause
