#!/usr/bin/env python3
"""
Log Viewer - Unified Log Browser for Orchestrator

A FastAPI-based log viewer that queries all three log tables:
- orchestrator_chat: User/orchestrator/agent conversations
- agent_logs: Subagent hook events and response blocks
- system_logs: Orchestrator thinking blocks and tool use

Run with: python -m uvicorn main:app --host 0.0.0.0 --port 5998
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment from orchestrator's .env
ENV_PATH = Path(__file__).parent.parent / "orchestrator_3_stream" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/orchestrator")

# Global connection pool
_pool: Optional[ThreadedConnectionPool] = None


# ============================================================================
# DATABASE CONNECTION
# ============================================================================


def parse_database_url(url: str) -> Dict[str, Any]:
    """Parse PostgreSQL connection URL into components."""
    import re
    from urllib.parse import unquote

    # Pattern: postgresql://user:pass@host:port/database
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, url)

    if not match:
        raise ValueError(f"Invalid DATABASE_URL format: {url}")

    return {
        'user': match.group(1),
        'password': unquote(match.group(2)),
        'host': match.group(3),
        'port': int(match.group(4)),
        'database': match.group(5)
    }


def resolve_hostname(hostname: str) -> str:
    """Resolve hostname to IP address (helps with Windows DNS issues)."""
    import socket
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return hostname


def init_pool() -> ThreadedConnectionPool:
    """Initialize the database connection pool."""
    global _pool

    if _pool is not None:
        return _pool

    conn_params = parse_database_url(DATABASE_URL)
    conn_params['host'] = resolve_hostname(conn_params['host'])

    _pool = ThreadedConnectionPool(
        minconn=2,
        maxconn=10,
        host=conn_params['host'],
        port=conn_params['port'],
        database=conn_params['database'],
        user=conn_params['user'],
        password=conn_params['password']
    )

    return _pool


def get_pool() -> ThreadedConnectionPool:
    """Get the connection pool, initializing if needed."""
    global _pool
    if _pool is None:
        init_pool()
    return _pool


def close_pool():
    """Close the connection pool."""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class UnifiedLogEntry(BaseModel):
    """Unified log entry from any source table."""
    id: str
    source: Literal["agent_logs", "system_logs", "orchestrator_chat"]
    timestamp: str

    # Common fields
    message: Optional[str] = None
    summary: Optional[str] = None

    # Source-specific fields
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    level: Optional[str] = None
    sender_type: Optional[str] = None
    receiver_type: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    orchestrator_agent_id: Optional[str] = None

    # Metadata/payload
    metadata: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None


class LogStats(BaseModel):
    """Statistics about logs."""
    total_count: int
    agent_logs_count: int
    system_logs_count: int
    chat_count: int
    event_types: Dict[str, int]
    sources: Dict[str, int]


class FilterOptions(BaseModel):
    """Available filter options."""
    sources: List[str]
    event_types: List[str]
    event_categories: List[str]
    levels: List[str]
    sender_types: List[str]
    agents: List[Dict[str, str]]
    orchestrator_agents: List[Dict[str, str]]


# ============================================================================
# DATABASE QUERIES
# ============================================================================


def fetch_unified_logs(
    limit: int = 100,
    offset: int = 0,
    source: Optional[str] = None,
    event_type: Optional[str] = None,
    event_category: Optional[str] = None,
    level: Optional[str] = None,
    sender_type: Optional[str] = None,
    agent_id: Optional[str] = None,
    orchestrator_agent_id: Optional[str] = None,
    search: Optional[str] = None,
    hours: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch logs from all three tables using UNION ALL.

    Returns unified log entries sorted by timestamp DESC.
    """
    pool = get_pool()
    conn = pool.getconn()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build time filter
            time_filter = ""
            if hours:
                time_filter = f"AND timestamp > NOW() - INTERVAL '{hours} hours'"

            # Build search filter
            search_filter = ""
            search_params = []
            if search:
                search_filter = "AND (message ILIKE %s OR content ILIKE %s)"
                search_params = [f"%{search}%", f"%{search}%"]

            queries = []
            params = []

            # Agent logs query
            if source is None or source == "agent_logs":
                agent_where = ["1=1"]
                if event_type:
                    agent_where.append("al.event_type = %s")
                    params.append(event_type)
                if event_category:
                    agent_where.append("al.event_category = %s")
                    params.append(event_category)
                if agent_id:
                    agent_where.append("al.agent_id::text = %s")
                    params.append(agent_id)

                queries.append(f"""
                    SELECT
                        al.id::text as id,
                        'agent_logs' as source,
                        al.timestamp::text as timestamp,
                        al.content as message,
                        al.summary,
                        al.event_type,
                        al.event_category,
                        NULL as level,
                        NULL as sender_type,
                        NULL as receiver_type,
                        al.agent_id::text,
                        a.name as agent_name,
                        a.orchestrator_agent_id::text,
                        NULL::jsonb as metadata,
                        al.payload
                    FROM agent_logs al
                    LEFT JOIN agents a ON al.agent_id = a.id
                    WHERE {' AND '.join(agent_where)}
                    {time_filter.replace('timestamp', 'al.timestamp')}
                """)

            # System logs query
            if source is None or source == "system_logs":
                sys_where = ["1=1"]
                if level:
                    sys_where.append("sl.level = %s")
                    params.append(level)
                if orchestrator_agent_id:
                    sys_where.append("sl.metadata->>'orchestrator_agent_id' = %s")
                    params.append(orchestrator_agent_id)

                queries.append(f"""
                    SELECT
                        sl.id::text as id,
                        'system_logs' as source,
                        sl.timestamp::text as timestamp,
                        sl.message,
                        sl.summary,
                        sl.metadata->>'type' as event_type,
                        'system' as event_category,
                        sl.level,
                        NULL as sender_type,
                        NULL as receiver_type,
                        NULL as agent_id,
                        NULL as agent_name,
                        sl.metadata->>'orchestrator_agent_id' as orchestrator_agent_id,
                        sl.metadata,
                        NULL::jsonb as payload
                    FROM system_logs sl
                    WHERE {' AND '.join(sys_where)}
                    {time_filter.replace('timestamp', 'sl.timestamp')}
                """)

            # Orchestrator chat query
            if source is None or source == "orchestrator_chat":
                chat_where = ["1=1"]
                if sender_type:
                    chat_where.append("oc.sender_type = %s")
                    params.append(sender_type)
                if agent_id:
                    chat_where.append("oc.agent_id::text = %s")
                    params.append(agent_id)
                if orchestrator_agent_id:
                    chat_where.append("oc.orchestrator_agent_id::text = %s")
                    params.append(orchestrator_agent_id)

                queries.append(f"""
                    SELECT
                        oc.id::text as id,
                        'orchestrator_chat' as source,
                        oc.created_at::text as timestamp,
                        oc.message,
                        oc.summary,
                        oc.metadata->>'type' as event_type,
                        'chat' as event_category,
                        NULL as level,
                        oc.sender_type,
                        oc.receiver_type,
                        oc.agent_id::text,
                        a.name as agent_name,
                        oc.orchestrator_agent_id::text,
                        oc.metadata,
                        NULL::jsonb as payload
                    FROM orchestrator_chat oc
                    LEFT JOIN agents a ON oc.agent_id = a.id
                    WHERE {' AND '.join(chat_where)}
                    {time_filter.replace('timestamp', 'oc.created_at')}
                """)

            # Combine with UNION ALL
            full_query = f"""
                SELECT * FROM (
                    {' UNION ALL '.join(queries)}
                ) unified
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])

            cur.execute(full_query, tuple(params))
            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                # Parse JSON fields
                if result.get('metadata') and isinstance(result['metadata'], str):
                    result['metadata'] = json.loads(result['metadata'])
                if result.get('payload') and isinstance(result['payload'], str):
                    result['payload'] = json.loads(result['payload'])
                results.append(result)

            return results

    finally:
        pool.putconn(conn)


def fetch_log_stats() -> Dict[str, Any]:
    """Fetch statistics about logs from all tables."""
    pool = get_pool()
    conn = pool.getconn()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Count from each table
            cur.execute("SELECT COUNT(*) as count FROM agent_logs")
            agent_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM system_logs")
            system_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) as count FROM orchestrator_chat")
            chat_count = cur.fetchone()['count']

            # Event types from agent_logs
            cur.execute("""
                SELECT event_type, COUNT(*) as count
                FROM agent_logs
                GROUP BY event_type
                ORDER BY count DESC
            """)
            event_types = {row['event_type']: row['count'] for row in cur.fetchall()}

            return {
                'total_count': agent_count + system_count + chat_count,
                'agent_logs_count': agent_count,
                'system_logs_count': system_count,
                'chat_count': chat_count,
                'event_types': event_types,
                'sources': {
                    'agent_logs': agent_count,
                    'system_logs': system_count,
                    'orchestrator_chat': chat_count
                }
            }

    finally:
        pool.putconn(conn)


def fetch_filter_options() -> Dict[str, Any]:
    """Fetch available filter options from all tables."""
    pool = get_pool()
    conn = pool.getconn()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Event types from agent_logs
            cur.execute("SELECT DISTINCT event_type FROM agent_logs WHERE event_type IS NOT NULL ORDER BY event_type")
            event_types = [row['event_type'] for row in cur.fetchall()]

            # Event categories
            cur.execute("SELECT DISTINCT event_category FROM agent_logs WHERE event_category IS NOT NULL ORDER BY event_category")
            event_categories = [row['event_category'] for row in cur.fetchall()]

            # Log levels from system_logs
            cur.execute("SELECT DISTINCT level FROM system_logs WHERE level IS NOT NULL ORDER BY level")
            levels = [row['level'] for row in cur.fetchall()]

            # Sender types from chat
            cur.execute("SELECT DISTINCT sender_type FROM orchestrator_chat WHERE sender_type IS NOT NULL ORDER BY sender_type")
            sender_types = [row['sender_type'] for row in cur.fetchall()]

            # Agents
            cur.execute("SELECT id::text, name FROM agents WHERE archived = false ORDER BY name")
            agents = [{'id': row['id'], 'name': row['name']} for row in cur.fetchall()]

            # Orchestrator agents
            cur.execute("SELECT id::text, session_id FROM orchestrator_agents WHERE archived = false ORDER BY created_at DESC")
            orchestrator_agents = [
                {'id': row['id'], 'session_id': row['session_id'] or 'No session'}
                for row in cur.fetchall()
            ]

            return {
                'sources': ['agent_logs', 'system_logs', 'orchestrator_chat'],
                'event_types': event_types,
                'event_categories': event_categories,
                'levels': levels,
                'sender_types': sender_types,
                'agents': agents,
                'orchestrator_agents': orchestrator_agents
            }

    finally:
        pool.putconn(conn)


# ============================================================================
# FASTAPI APP
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - init and close DB pool."""
    init_pool()
    print("Log Viewer started - Database pool initialized")
    yield
    close_pool()
    print("Log Viewer stopped - Database pool closed")


app = FastAPI(
    title="Log Viewer",
    description="Unified log browser for orchestrator, agent, and system logs",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates = Jinja2Templates(directory=templates_dir) if templates_dir.exists() else None


# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main log viewer page."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>Log Viewer</h1><p>Templates not found. Use /api/logs endpoint.</p>")


@app.get("/api/logs")
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    source: Optional[str] = Query(None, description="Filter by source: agent_logs, system_logs, orchestrator_chat"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    event_category: Optional[str] = Query(None, description="Filter by event category: hook, response, system, chat"),
    level: Optional[str] = Query(None, description="Filter by log level (system_logs only)"),
    sender_type: Optional[str] = Query(None, description="Filter by sender type (chat only): user, orchestrator, agent"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    orchestrator_agent_id: Optional[str] = Query(None, description="Filter by orchestrator agent ID"),
    search: Optional[str] = Query(None, description="Search in message content"),
    hours: Optional[int] = Query(None, ge=1, description="Only show logs from last N hours"),
):
    """
    Get unified logs from all sources.

    Queries orchestrator_chat, agent_logs, and system_logs tables
    and returns a unified view sorted by timestamp.
    """
    try:
        logs = await asyncio.to_thread(
            fetch_unified_logs,
            limit=limit,
            offset=offset,
            source=source,
            event_type=event_type,
            event_category=event_category,
            level=level,
            sender_type=sender_type,
            agent_id=agent_id,
            orchestrator_agent_id=orchestrator_agent_id,
            search=search,
            hours=hours,
        )
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs/stats")
async def get_stats():
    """Get statistics about logs from all tables."""
    try:
        stats = await asyncio.to_thread(fetch_log_stats)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs/filter-options")
async def get_filter_options():
    """Get available filter options for the UI."""
    try:
        options = await asyncio.to_thread(fetch_filter_options)
        return options
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat")
async def get_chat(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    orchestrator_agent_id: Optional[str] = Query(None),
):
    """Get orchestrator chat messages only."""
    try:
        logs = await asyncio.to_thread(
            fetch_unified_logs,
            limit=limit,
            offset=offset,
            source="orchestrator_chat",
            orchestrator_agent_id=orchestrator_agent_id,
        )
        return {"chat": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent-logs")
async def get_agent_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    event_category: Optional[str] = Query(None),
):
    """Get agent logs only."""
    try:
        logs = await asyncio.to_thread(
            fetch_unified_logs,
            limit=limit,
            offset=offset,
            source="agent_logs",
            agent_id=agent_id,
            event_type=event_type,
            event_category=event_category,
        )
        return {"agent_logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system-logs")
async def get_system_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level: Optional[str] = Query(None),
    orchestrator_agent_id: Optional[str] = Query(None),
):
    """Get system logs only (includes orchestrator thinking/tool use)."""
    try:
        logs = await asyncio.to_thread(
            fetch_unified_logs,
            limit=limit,
            offset=offset,
            source="system_logs",
            level=level,
            orchestrator_agent_id=orchestrator_agent_id,
        )
        return {"system_logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        pool = get_pool()
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return {"status": "healthy", "database": "connected"}
        finally:
            pool.putconn(conn)
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("LOG_VIEWER_PORT", "5998"))
    host = os.getenv("LOG_VIEWER_HOST", "0.0.0.0")

    print(f"\n{'='*60}")
    print("LOG VIEWER - Unified Orchestrator Log Browser")
    print(f"{'='*60}")
    print(f"  Server:   http://{host}:{port}")
    print(f"  API Docs: http://{host}:{port}/docs")
    print(f"  Database: {DATABASE_URL[:50]}...")
    print(f"{'='*60}\n")

    uvicorn.run(app, host=host, port=port)
