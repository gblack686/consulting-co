@echo off
echo ========================================
echo Opening All Observability Dashboards
echo ========================================
echo.

echo 1. Multi-Agent Orchestrator
start http://localhost:3001
timeout /t 2 /nobreak >nul

echo 2. Langfuse (Traces + Analytics)
start http://localhost:3000
timeout /t 2 /nobreak >nul

echo 3. Neo4j Browser (Knowledge Graph)
start http://localhost:7474
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo DASHBOARDS OPENED
echo ========================================
echo.
echo Multi-Agent Orchestrator:  http://localhost:3001
echo   - Real-time agent monitoring
echo   - WebSocket event stream
echo   - Cost tracking per agent
echo   - Natural language control
echo.
echo Langfuse:                   http://localhost:3000
echo   - Login and get API keys from Settings
echo   - View traces at /traces
echo   - Analytics at /analytics
echo.
echo Neo4j:                      http://localhost:7474
echo   - Username: neo4j
echo   - Password: yourpassword
echo   - Run: MATCH (e:Episodic) RETURN e LIMIT 10
echo.
echo ========================================
echo OBSERVABILITY STACK READY
echo ========================================
echo.
echo All systems integrated:
echo   [Orchestrator] -^> PostgreSQL (Supabase)
echo   [Langfuse]     -^> Traces + Token Usage
echo   [Neo4j]        -^> Knowledge Graph + Memory
echo.
pause
