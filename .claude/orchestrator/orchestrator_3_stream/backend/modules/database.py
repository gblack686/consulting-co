"""
Database Connection Pool and Operations

Consolidated database module for orchestrator_3_stream providing:
- Connection pool management (psycopg2 with ThreadedConnectionPool)
- Orchestrator agent operations (singleton pattern)
- Chat message operations (three-way communication)
- Agent CRUD operations
- Agent event logging operations
- System logs operations

Reference:
- apps/orchestrator_1_term/modules/database/database.py
- apps/orchestrator_1_term/modules/database/orchestrator_agents_db.py
- apps/orchestrator_1_term/modules/database/orchestrator_chat_db.py

Adapted for psycopg2 (synchronous) with asyncio wrappers for FastAPI compatibility.
"""

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor, register_uuid
import asyncio
import uuid
import json
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .orch_database_models import Agent, AgentLog
from .config import DEFAULT_AGENT_LOG_LIMIT, DEFAULT_SYSTEM_LOG_LIMIT, DEFAULT_CHAT_HISTORY_LIMIT
from .dns_resolver import parse_and_resolve_database_url

# Global connection pool
_pool: Optional[ThreadedConnectionPool] = None


# ═══════════════════════════════════════════════════════════
# CONNECTION POOL MANAGEMENT
# ═══════════════════════════════════════════════════════════


def _init_pool_sync(
    database_url: str = None, min_size: int = 5, max_size: int = 20
) -> ThreadedConnectionPool:
    """
    Initialize psycopg2 connection pool (synchronous).

    Args:
        database_url: PostgreSQL connection string (from env if not provided)
        min_size: Minimum pool size
        max_size: Maximum pool size

    Returns:
        ThreadedConnectionPool instance

    Raises:
        ValueError: If DATABASE_URL is not provided and not set in environment
    """
    global _pool

    if _pool is not None:
        return _pool

    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Parse URL and resolve hostname to IP (avoids Windows DNS issues)
    conn_params = parse_and_resolve_database_url(url)

    # Create threaded connection pool
    _pool = ThreadedConnectionPool(
        minconn=min_size,
        maxconn=max_size,
        host=conn_params['host'],
        port=conn_params['port'],
        database=conn_params['database'],
        user=conn_params['user'],
        password=conn_params['password']
    )

    # Register UUID type adapter for psycopg2
    register_uuid()

    return _pool


async def init_pool(
    database_url: str = None, min_size: int = 5, max_size: int = 20
) -> ThreadedConnectionPool:
    """
    Initialize psycopg2 connection pool (async wrapper).

    Args:
        database_url: PostgreSQL connection string (from env if not provided)
        min_size: Minimum pool size
        max_size: Maximum pool size

    Returns:
        ThreadedConnectionPool instance
    """
    return await asyncio.to_thread(_init_pool_sync, database_url, min_size, max_size)


def get_pool() -> ThreadedConnectionPool:
    """
    Get existing connection pool.

    Returns:
        ThreadedConnectionPool instance

    Raises:
        RuntimeError: If pool not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_pool() first.")
    return _pool


def _close_pool_sync():
    """
    Close connection pool (synchronous).

    Safely closes all connections in the pool and resets the global pool variable.
    This should be called during application shutdown.
    """
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None


async def close_pool():
    """
    Close connection pool (async wrapper).
    """
    await asyncio.to_thread(_close_pool_sync)


@contextmanager
def get_connection():
    """
    Context manager for database connections.

    Acquires a connection from the pool and ensures it's properly released.

    Usage:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT ...")

    Yields:
        psycopg2.connection: Database connection from the pool

    Raises:
        RuntimeError: If pool not initialized
    """
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


# ═══════════════════════════════════════════════════════════
# ORCHESTRATOR AGENT OPERATIONS
# ═══════════════════════════════════════════════════════════


def _get_or_create_orchestrator_sync(
    system_prompt: str, working_dir: str
) -> Dict[str, Any]:
    """
    Get existing orchestrator or create new one (synchronous).

    Ensures only one orchestrator exists (singleton pattern).
    If an existing orchestrator is found (WHERE archived=false), returns it.
    Otherwise, creates a new orchestrator with default values.

    Args:
        system_prompt: Orchestrator's system prompt
        working_dir: Orchestrator's working directory path

    Returns:
        Dictionary containing orchestrator data with all fields from database
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Try to get existing orchestrator (singleton pattern)
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE archived = false LIMIT 1"
            )
            row = cur.fetchone()

            if row:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                return result

            # Create new orchestrator
            orch_id = uuid.uuid4()
            cur.execute(
                """
                INSERT INTO orchestrator_agents (
                    id, system_prompt, status, working_dir,
                    metadata, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """,
                (orch_id, system_prompt, "idle", working_dir, json.dumps({})),
            )
            conn.commit()

            # Fetch and return the created orchestrator
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE id = %s", (orch_id,)
            )
            row = cur.fetchone()
            result = dict(row)
            if isinstance(result.get("metadata"), str):
                result["metadata"] = json.loads(result["metadata"])
            return result


async def get_or_create_orchestrator(
    system_prompt: str, working_dir: str
) -> Dict[str, Any]:
    """
    Get existing orchestrator or create new one (async wrapper).
    """
    return await asyncio.to_thread(_get_or_create_orchestrator_sync, system_prompt, working_dir)


def _create_new_orchestrator_sync(
    system_prompt: str, working_dir: str
) -> Dict[str, Any]:
    """
    Always create a new orchestrator (synchronous).

    Creates a new orchestrator with a fresh session ID, regardless of
    whether one already exists. Used when explicitly starting a new session.

    Args:
        system_prompt: Orchestrator's system prompt
        working_dir: Orchestrator's working directory path

    Returns:
        Dictionary containing orchestrator data with all fields from database
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Generate new ID (session_id will be NULL initially, set by Claude SDK later)
            orch_id = uuid.uuid4()

            # Create new orchestrator with NULL session_id
            cur.execute(
                """
                INSERT INTO orchestrator_agents (
                    id, session_id, system_prompt, status, working_dir,
                    metadata, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
                (orch_id, None, system_prompt, "idle", working_dir, json.dumps({})),
            )
            conn.commit()

            # Fetch and return the created orchestrator
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE id = %s", (orch_id,)
            )
            row = cur.fetchone()
            result = dict(row)
            if isinstance(result.get("metadata"), str):
                result["metadata"] = json.loads(result["metadata"])
            return result


async def create_new_orchestrator(
    system_prompt: str, working_dir: str
) -> Dict[str, Any]:
    """
    Always create a new orchestrator (async wrapper).
    """
    return await asyncio.to_thread(_create_new_orchestrator_sync, system_prompt, working_dir)


def _get_orchestrator_sync() -> Optional[Dict[str, Any]]:
    """
    Get the active orchestrator (synchronous).

    Retrieves the current orchestrator record (WHERE archived=false).
    Returns None if no orchestrator exists.

    Returns:
        Dictionary containing orchestrator data or None if not found
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE archived = false LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                return result
            return None


async def get_orchestrator() -> Optional[Dict[str, Any]]:
    """
    Get the active orchestrator (async wrapper).
    """
    return await asyncio.to_thread(_get_orchestrator_sync)


def _get_orchestrator_by_session_sync(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get orchestrator by session ID (synchronous).

    Args:
        session_id: Claude SDK session ID to look up

    Returns:
        Dictionary containing orchestrator data or None if session not found
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE session_id = %s AND archived = false",
                (session_id,),
            )
            row = cur.fetchone()
            if row:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                return result
            return None


async def get_orchestrator_by_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get orchestrator by session ID (async wrapper).
    """
    return await asyncio.to_thread(_get_orchestrator_by_session_sync, session_id)


def _get_orchestrator_by_id_sync(orchestrator_agent_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get orchestrator by ID (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator to retrieve

    Returns:
        Dictionary containing orchestrator data or None if not found
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM orchestrator_agents WHERE id = %s AND archived = false",
                (orchestrator_agent_id,),
            )
            row = cur.fetchone()
            if row:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                return result
            return None


async def get_orchestrator_by_id(orchestrator_agent_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """
    Get orchestrator by ID (async wrapper).
    """
    return await asyncio.to_thread(_get_orchestrator_by_id_sync, orchestrator_agent_id)


def _update_orchestrator_session_sync(
    orchestrator_agent_id: uuid.UUID, session_id: str
) -> Optional[Dict[str, Any]]:
    """
    Update orchestrator's Claude SDK session ID (synchronous).

    ONLY updates if the current session_id is NULL (first-time session setup).

    Args:
        orchestrator_agent_id: UUID of the orchestrator to update
        session_id: Claude SDK session ID

    Returns:
        Dictionary containing updated orchestrator data or None if not found
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Execute the UPDATE
            cur.execute(
                """
                UPDATE orchestrator_agents
                SET session_id = %s, updated_at = NOW()
                WHERE id = %s AND session_id IS NULL
            """,
                (session_id, orchestrator_agent_id),
            )
            conn.commit()

            # Fetch and return updated row
            cur.execute(
                """
                SELECT * FROM orchestrator_agents
                WHERE id = %s AND archived = false
                """,
                (orchestrator_agent_id,),
            )

            row = cur.fetchone()
            if row:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                return result
            return None


async def update_orchestrator_session(
    orchestrator_agent_id: uuid.UUID, session_id: str
) -> Optional[Dict[str, Any]]:
    """
    Update orchestrator's Claude SDK session ID (async wrapper).
    """
    return await asyncio.to_thread(_update_orchestrator_session_sync, orchestrator_agent_id, session_id)


def _update_orchestrator_costs_sync(
    orchestrator_agent_id: uuid.UUID,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
) -> Dict[str, Any]:
    """
    Update orchestrator's cumulative token usage and costs (synchronous).

    Uses incremental updates (adds to existing values).

    Args:
        orchestrator_agent_id: UUID of the specific orchestrator to update
        input_tokens: Number of input tokens from this execution
        output_tokens: Number of output tokens from this execution
        cost_usd: Cost in USD from this execution

    Returns:
        Dictionary with updated values and row count
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Execute the UPDATE
            cur.execute(
                """
                UPDATE orchestrator_agents
                SET input_tokens = input_tokens + %s,
                    output_tokens = output_tokens + %s,
                    total_cost = total_cost + %s,
                    updated_at = NOW()
                WHERE id = %s AND archived = false
            """,
                (input_tokens, output_tokens, cost_usd, orchestrator_agent_id),
            )
            conn.commit()

            rows_updated = cur.rowcount

            # Get updated row to verify
            cur.execute(
                """
                SELECT id, input_tokens, output_tokens, total_cost, updated_at
                FROM orchestrator_agents
                WHERE id = %s AND archived = false
                """,
                (orchestrator_agent_id,),
            )

            row = cur.fetchone()
            if row:
                return {
                    "success": True,
                    "rows_updated": rows_updated,
                    "id": str(row["id"]),
                    "input_tokens": row["input_tokens"],
                    "output_tokens": row["output_tokens"],
                    "total_cost": float(row["total_cost"]),
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                }
            else:
                return {
                    "success": False,
                    "rows_updated": 0,
                    "error": f"No orchestrator found with id={orchestrator_agent_id} (archived=false)",
                }


async def update_orchestrator_costs(
    orchestrator_agent_id: uuid.UUID,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
) -> Dict[str, Any]:
    """
    Update orchestrator's cumulative token usage and costs (async wrapper).
    """
    return await asyncio.to_thread(
        _update_orchestrator_costs_sync,
        orchestrator_agent_id,
        input_tokens,
        output_tokens,
        cost_usd
    )


def _update_orchestrator_status_sync(
    orchestrator_agent_id: uuid.UUID, status: str
) -> None:
    """
    Update orchestrator's status (synchronous).

    Args:
        orchestrator_agent_id: UUID of the specific orchestrator to update
        status: New status - "idle", "executing", "waiting", "blocked", "complete"
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE orchestrator_agents
                SET status = %s, updated_at = NOW()
                WHERE id = %s AND archived = false
            """,
                (status, orchestrator_agent_id),
            )
            conn.commit()


async def update_orchestrator_status(
    orchestrator_agent_id: uuid.UUID, status: str
) -> None:
    """
    Update orchestrator's status (async wrapper).
    """
    await asyncio.to_thread(_update_orchestrator_status_sync, orchestrator_agent_id, status)


def _update_orchestrator_metadata_sync(
    orchestrator_agent_id: uuid.UUID, metadata_updates: Dict[str, Any]
) -> None:
    """
    Update orchestrator metadata fields using JSONB merge (synchronous).

    Merges provided metadata with existing metadata without replacing it.

    Args:
        orchestrator_agent_id: UUID of the specific orchestrator to update
        metadata_updates: Dictionary of metadata fields to add/update
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE orchestrator_agents
                SET metadata = metadata || %s::jsonb, updated_at = NOW()
                WHERE id = %s AND archived = false
                """,
                (json.dumps(metadata_updates), orchestrator_agent_id),
            )
            conn.commit()


async def update_orchestrator_metadata(
    orchestrator_agent_id: uuid.UUID, metadata_updates: Dict[str, Any]
) -> None:
    """
    Update orchestrator metadata fields using JSONB merge (async wrapper).
    """
    await asyncio.to_thread(_update_orchestrator_metadata_sync, orchestrator_agent_id, metadata_updates)


# ═══════════════════════════════════════════════════════════
# CHAT MESSAGE OPERATIONS
# ═══════════════════════════════════════════════════════════


def _insert_chat_message_sync(
    orchestrator_agent_id: uuid.UUID,
    sender_type: str,
    receiver_type: str,
    message: str,
    agent_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Insert a new chat message into orchestrator_chat table (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent
        sender_type: "user", "orchestrator", or "agent"
        receiver_type: "user", "orchestrator", or "agent"
        message: The message text
        agent_id: UUID of command agent (required when sender/receiver is "agent")
        metadata: Optional JSONB metadata

    Returns:
        UUID of the created chat message
    """
    valid_types = ("user", "orchestrator", "agent")

    if sender_type not in valid_types:
        raise ValueError(
            f"sender_type must be one of {valid_types}, got: {sender_type}"
        )

    if receiver_type not in valid_types:
        raise ValueError(
            f"receiver_type must be one of {valid_types}, got: {receiver_type}"
        )

    # Validate agent_id requirements
    agent_involved = sender_type == "agent" or receiver_type == "agent"
    if agent_involved and agent_id is None:
        raise ValueError(
            "agent_id is required when sender_type or receiver_type is 'agent'"
        )
    if not agent_involved and agent_id is not None:
        raise ValueError(
            "agent_id must be None when neither sender nor receiver is 'agent'"
        )

    message_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO orchestrator_chat (
                    id, orchestrator_agent_id, sender_type, receiver_type,
                    message, agent_id, metadata,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
                (
                    message_id,
                    orchestrator_agent_id,
                    sender_type,
                    receiver_type,
                    message,
                    agent_id,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

    return message_id


async def insert_chat_message(
    orchestrator_agent_id: uuid.UUID,
    sender_type: str,
    receiver_type: str,
    message: str,
    agent_id: Optional[uuid.UUID] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Insert a new chat message into orchestrator_chat table (async wrapper).
    """
    return await asyncio.to_thread(
        _insert_chat_message_sync,
        orchestrator_agent_id,
        sender_type,
        receiver_type,
        message,
        agent_id,
        metadata
    )


def _get_chat_history_sync(
    orchestrator_agent_id: uuid.UUID,
    limit: Optional[int] = None,
    offset: int = 0,
    agent_id: Optional[uuid.UUID] = None,
) -> List[Dict[str, Any]]:
    """
    Get chat history for an orchestrator agent (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent
        limit: Maximum number of messages to return (None = all)
        offset: Number of messages to skip (for pagination)
        agent_id: Optional - filter messages involving specific command agent

    Returns:
        List of chat message dictionaries, ordered by created_at ASC (oldest first)
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, orchestrator_agent_id, sender_type, receiver_type,
                       message, agent_id, metadata,
                       created_at, updated_at
                FROM orchestrator_chat
                WHERE orchestrator_agent_id = %s
            """

            params = [orchestrator_agent_id]

            # Add agent_id filter if provided
            if agent_id is not None:
                query += " AND agent_id = %s"
                params.append(agent_id)

            # Order by DESC to get newest messages when using LIMIT
            query += " ORDER BY created_at DESC"

            if limit is not None:
                query += f" LIMIT {limit} OFFSET {offset}"

            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                # Parse metadata JSONB if it's a string
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                results.append(result)

            # Reverse to return in chronological order (oldest first)
            results.reverse()

            return results


async def get_chat_history(
    orchestrator_agent_id: uuid.UUID,
    limit: Optional[int] = None,
    offset: int = 0,
    agent_id: Optional[uuid.UUID] = None,
) -> List[Dict[str, Any]]:
    """
    Get chat history for an orchestrator agent (async wrapper).
    """
    return await asyncio.to_thread(
        _get_chat_history_sync,
        orchestrator_agent_id,
        limit,
        offset,
        agent_id
    )


def _get_turn_count_sync(orchestrator_agent_id: uuid.UUID) -> int:
    """
    Get the turn count (number of messages) for an orchestrator agent (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent

    Returns:
        Integer count of total messages in the conversation
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM orchestrator_chat
                WHERE orchestrator_agent_id = %s
            """,
                (orchestrator_agent_id,),
            )

            row = cur.fetchone()
            return row["count"] if row else 0


async def get_turn_count(orchestrator_agent_id: uuid.UUID) -> int:
    """
    Get the turn count (number of messages) for an orchestrator agent (async wrapper).
    """
    return await asyncio.to_thread(_get_turn_count_sync, orchestrator_agent_id)


def _delete_chat_history_sync(orchestrator_agent_id: uuid.UUID) -> int:
    """
    Delete all chat history for an orchestrator agent (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent

    Returns:
        Number of messages deleted
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                DELETE FROM orchestrator_chat
                WHERE orchestrator_agent_id = %s
            """,
                (orchestrator_agent_id,),
            )
            conn.commit()

            return cur.rowcount


async def delete_chat_history(orchestrator_agent_id: uuid.UUID) -> int:
    """
    Delete all chat history for an orchestrator agent (async wrapper).
    """
    return await asyncio.to_thread(_delete_chat_history_sync, orchestrator_agent_id)


# ═══════════════════════════════════════════════════════════
# AGENT CRUD OPERATIONS
# ═══════════════════════════════════════════════════════════


def _create_agent_sync(
    orchestrator_agent_id: uuid.UUID,
    name: str,
    model: str,
    system_prompt: str,
    working_dir: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Create new agent in database (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent that owns this command agent
        name: Agent identifier/name (unique per orchestrator)
        model: Claude model ID
        system_prompt: Agent's custom system prompt
        working_dir: Agent's working directory path
        metadata: Optional JSONB metadata

    Returns:
        UUID of created agent
    """
    agent_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO agents (
                    id, orchestrator_agent_id, name, model, system_prompt, working_dir,
                    status, metadata, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
                (
                    agent_id,
                    orchestrator_agent_id,
                    name,
                    model,
                    system_prompt,
                    working_dir,
                    "idle",
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

    return agent_id


async def create_agent(
    orchestrator_agent_id: uuid.UUID,
    name: str,
    model: str,
    system_prompt: str,
    working_dir: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Create new agent in database (async wrapper).
    """
    return await asyncio.to_thread(
        _create_agent_sync,
        orchestrator_agent_id,
        name,
        model,
        system_prompt,
        working_dir,
        metadata
    )


def _get_agent_sync(agent_id: uuid.UUID) -> Optional[Agent]:
    """
    Get agent by ID (synchronous).

    Args:
        agent_id: UUID of the agent

    Returns:
        Agent Pydantic model or None if not found or archived
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM agents WHERE id = %s AND archived = false", (agent_id,)
            )
            row = cur.fetchone()
            if not row:
                return None

            return Agent(**dict(row))


async def get_agent(agent_id: uuid.UUID) -> Optional[Agent]:
    """
    Get agent by ID (async wrapper).
    """
    return await asyncio.to_thread(_get_agent_sync, agent_id)


def _get_agent_by_name_sync(orchestrator_agent_id: uuid.UUID, name: str) -> Optional[Agent]:
    """
    Get agent by name (scoped to orchestrator) (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent
        name: Agent name (unique per orchestrator)

    Returns:
        Agent Pydantic model or None if not found or archived
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM agents
                WHERE orchestrator_agent_id = %s
                  AND name = %s
                  AND archived = false
                """,
                (orchestrator_agent_id, name)
            )
            row = cur.fetchone()
            if not row:
                return None

            return Agent(**dict(row))


async def get_agent_by_name(orchestrator_agent_id: uuid.UUID, name: str) -> Optional[Agent]:
    """
    Get agent by name (scoped to orchestrator) (async wrapper).
    """
    return await asyncio.to_thread(_get_agent_by_name_sync, orchestrator_agent_id, name)


def _list_agents_sync(orchestrator_agent_id: uuid.UUID, archived: bool = False) -> List[Agent]:
    """
    List all agents for this orchestrator (synchronous).

    Args:
        orchestrator_agent_id: UUID of the orchestrator agent
        archived: If True, return archived agents. If False, return active agents.

    Returns:
        List of Agent Pydantic models, ordered by creation date (newest first)
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM agents
                WHERE orchestrator_agent_id = %s
                  AND archived = %s
                ORDER BY created_at DESC
                """,
                (orchestrator_agent_id, archived),
            )
            rows = cur.fetchall()
            return [Agent(**dict(row)) for row in rows]


async def list_agents(orchestrator_agent_id: uuid.UUID, archived: bool = False) -> List[Agent]:
    """
    List all agents for this orchestrator (async wrapper).
    """
    return await asyncio.to_thread(_list_agents_sync, orchestrator_agent_id, archived)


def _update_agent_status_sync(agent_id: uuid.UUID, status: str) -> None:
    """
    Update agent status (synchronous).

    Args:
        agent_id: UUID of the agent
        status: New status
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE agents SET status = %s, updated_at = NOW() WHERE id = %s",
                (status, agent_id),
            )
            conn.commit()


async def update_agent_status(agent_id: uuid.UUID, status: str) -> None:
    """
    Update agent status (async wrapper).
    """
    await asyncio.to_thread(_update_agent_status_sync, agent_id, status)


def _update_agent_session_sync(agent_id: uuid.UUID, session_id: Optional[str]) -> None:
    """
    Update agent's Claude SDK session ID (synchronous).

    Args:
        agent_id: UUID of the agent
        session_id: Claude SDK session ID or None to clear
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE agents SET session_id = %s, updated_at = NOW() WHERE id = %s",
                (session_id, agent_id),
            )
            conn.commit()


async def update_agent_session(agent_id: uuid.UUID, session_id: Optional[str]) -> None:
    """
    Update agent's Claude SDK session ID (async wrapper).
    """
    await asyncio.to_thread(_update_agent_session_sync, agent_id, session_id)


def _update_agent_costs_sync(
    agent_id: uuid.UUID, input_tokens: int, output_tokens: int, cost_usd: float
) -> None:
    """
    Update agent's cumulative token usage and costs (synchronous).

    Args:
        agent_id: UUID of the agent
        input_tokens: Number of input tokens from this execution
        output_tokens: Number of output tokens from this execution
        cost_usd: Cost in USD from this execution
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE agents
                SET input_tokens = input_tokens + %s,
                    output_tokens = output_tokens + %s,
                    total_cost = total_cost + %s,
                    updated_at = NOW()
                WHERE id = %s
            """,
                (input_tokens, output_tokens, cost_usd, agent_id),
            )
            conn.commit()


async def update_agent_costs(
    agent_id: uuid.UUID, input_tokens: int, output_tokens: int, cost_usd: float
) -> None:
    """
    Update agent's cumulative token usage and costs (async wrapper).
    """
    await asyncio.to_thread(_update_agent_costs_sync, agent_id, input_tokens, output_tokens, cost_usd)


def _reset_agent_tokens_sync(agent_id: uuid.UUID) -> None:
    """
    Reset agent's token usage and costs to zero (synchronous).

    Args:
        agent_id: UUID of the agent to reset
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE agents
                SET input_tokens = 0,
                    output_tokens = 0,
                    total_cost = 0.0,
                    updated_at = NOW()
                WHERE id = %s
            """,
                (agent_id,),
            )
            conn.commit()


async def reset_agent_tokens(agent_id: uuid.UUID) -> None:
    """
    Reset agent's token usage and costs to zero (async wrapper).
    """
    await asyncio.to_thread(_reset_agent_tokens_sync, agent_id)


def _delete_agent_sync(agent_id: uuid.UUID) -> None:
    """
    Soft delete agent (sets archived=true) (synchronous).

    Args:
        agent_id: UUID of the agent to archive
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE agents SET archived = true, updated_at = NOW() WHERE id = %s",
                (agent_id,),
            )
            conn.commit()


async def delete_agent(agent_id: uuid.UUID) -> None:
    """
    Soft delete agent (async wrapper).
    """
    await asyncio.to_thread(_delete_agent_sync, agent_id)


# ═══════════════════════════════════════════════════════════
# AGENT EVENT LOGGING OPERATIONS
# ═══════════════════════════════════════════════════════════


def _insert_hook_event_sync(
    agent_id: uuid.UUID,
    task_slug: str,
    entry_index: int,
    event_type: str,
    payload: Dict[str, Any],
    content: Optional[str] = None,
    session_id: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert hook event to agent_logs (synchronous).

    Returns:
        UUID of the created log entry
    """
    log_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO agent_logs (
                    id, agent_id, session_id, task_slug, adw_id, adw_step, entry_index,
                    event_category, event_type, content, payload, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    log_id,
                    agent_id,
                    session_id,
                    task_slug,
                    adw_id,
                    adw_step,
                    entry_index,
                    "hook",
                    event_type,
                    content,
                    json.dumps(payload),
                ),
            )
            conn.commit()

    return log_id


async def insert_hook_event(
    agent_id: uuid.UUID,
    task_slug: str,
    entry_index: int,
    event_type: str,
    payload: Dict[str, Any],
    content: Optional[str] = None,
    session_id: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert hook event to agent_logs (async wrapper).
    """
    return await asyncio.to_thread(
        _insert_hook_event_sync,
        agent_id,
        task_slug,
        entry_index,
        event_type,
        payload,
        content,
        session_id,
        adw_id,
        adw_step
    )


def _insert_message_block_sync(
    agent_id: uuid.UUID,
    task_slug: str,
    entry_index: int,
    block_type: str,
    content: Optional[str],
    payload: Dict[str, Any],
    session_id: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert message block to agent_logs (synchronous).

    Returns:
        UUID of the created log entry
    """
    log_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO agent_logs (
                    id, agent_id, session_id, task_slug, adw_id, adw_step, entry_index,
                    event_category, event_type, content, payload, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    log_id,
                    agent_id,
                    session_id,
                    task_slug,
                    adw_id,
                    adw_step,
                    entry_index,
                    "response",
                    block_type,
                    content,
                    json.dumps(payload),
                ),
            )
            conn.commit()

    return log_id


async def insert_message_block(
    agent_id: uuid.UUID,
    task_slug: str,
    entry_index: int,
    block_type: str,
    content: Optional[str],
    payload: Dict[str, Any],
    session_id: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert message block to agent_logs (async wrapper).
    """
    return await asyncio.to_thread(
        _insert_message_block_sync,
        agent_id,
        task_slug,
        entry_index,
        block_type,
        content,
        payload,
        session_id,
        adw_id,
        adw_step
    )


def _update_log_summary_sync(log_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing log entry (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE agent_logs SET summary = %s WHERE id = %s", (summary, log_id)
            )
            conn.commit()


async def update_log_summary(log_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing log entry (async wrapper).
    """
    await asyncio.to_thread(_update_log_summary_sync, log_id, summary)


def _update_log_payload_sync(log_id: uuid.UUID, payload: Dict[str, Any]) -> None:
    """
    Update payload for existing log entry (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE agent_logs SET payload = payload || %s::jsonb WHERE id = %s",
                (json.dumps(payload), log_id)
            )
            conn.commit()


async def update_log_payload(log_id: uuid.UUID, payload: Dict[str, Any]) -> None:
    """
    Update payload for existing log entry (async wrapper).
    """
    await asyncio.to_thread(_update_log_payload_sync, log_id, payload)


def _update_chat_summary_sync(chat_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing chat message (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE orchestrator_chat SET summary = %s WHERE id = %s", (summary, chat_id)
            )
            conn.commit()


async def update_chat_summary(chat_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing chat message (async wrapper).
    """
    await asyncio.to_thread(_update_chat_summary_sync, chat_id, summary)


def _update_prompt_summary_sync(prompt_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing prompt (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE prompts SET summary = %s WHERE id = %s", (summary, prompt_id)
            )
            conn.commit()


async def update_prompt_summary(prompt_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing prompt (async wrapper).
    """
    await asyncio.to_thread(_update_prompt_summary_sync, prompt_id, summary)


def _update_system_log_summary_sync(log_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing system log (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "UPDATE system_logs SET summary = %s WHERE id = %s", (summary, log_id)
            )
            conn.commit()


async def update_system_log_summary(log_id: uuid.UUID, summary: str) -> None:
    """
    Add AI-generated summary to existing system log (async wrapper).
    """
    await asyncio.to_thread(_update_system_log_summary_sync, log_id, summary)


def _get_agent_logs_sync(
    agent_id: uuid.UUID,
    task_slug: Optional[str] = None,
    limit: int = DEFAULT_AGENT_LOG_LIMIT,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Get agent logs with optional filtering (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if task_slug:
                cur.execute(
                    """
                    SELECT id, agent_id, session_id, task_slug, adw_id, adw_step,
                           entry_index, event_category, event_type, content, payload, summary, timestamp
                    FROM agent_logs
                    WHERE agent_id = %s AND task_slug = %s
                    ORDER BY entry_index ASC
                    LIMIT %s OFFSET %s
                """,
                    (agent_id, task_slug, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT id, agent_id, session_id, task_slug, adw_id, adw_step,
                           entry_index, event_category, event_type, content, payload, summary, timestamp
                    FROM agent_logs
                    WHERE agent_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """,
                    (agent_id, limit, offset),
                )

            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if isinstance(result.get("payload"), str):
                    result["payload"] = json.loads(result["payload"])
                results.append(result)
            return results


async def get_agent_logs(
    agent_id: uuid.UUID,
    task_slug: Optional[str] = None,
    limit: int = DEFAULT_AGENT_LOG_LIMIT,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Get agent logs with optional filtering (async wrapper).
    """
    return await asyncio.to_thread(_get_agent_logs_sync, agent_id, task_slug, limit, offset)


def _get_tail_summaries_sync(
    agent_id: uuid.UUID, task_slug: str, count: int = 10, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get last N events with their AI-generated summaries (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT entry_index, event_category, event_type, summary, timestamp
                FROM agent_logs
                WHERE agent_id = %s
                  AND task_slug = %s
                  AND summary IS NOT NULL
                ORDER BY entry_index DESC
                LIMIT %s OFFSET %s
            """,
                (agent_id, task_slug, count, offset),
            )

            rows = cur.fetchall()

    # Return in ascending order (chronological: oldest to newest)
    return [dict(row) for row in reversed(rows)]


async def get_tail_summaries(
    agent_id: uuid.UUID, task_slug: str, count: int = 10, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get last N events with their AI-generated summaries (async wrapper).
    """
    return await asyncio.to_thread(_get_tail_summaries_sync, agent_id, task_slug, count, offset)


def _get_tail_raw_sync(
    agent_id: uuid.UUID, task_slug: str, count: int = 10, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get last N events with full details (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT entry_index, event_category, event_type, content, payload, timestamp
                FROM agent_logs
                WHERE agent_id = %s AND task_slug = %s
                ORDER BY entry_index DESC
                LIMIT %s OFFSET %s
            """,
                (agent_id, task_slug, count, offset),
            )

            rows = cur.fetchall()

    # Return in ascending order (chronological: oldest to newest)
    results = []
    for row in reversed(rows):
        result = dict(row)
        if isinstance(result.get("payload"), str):
            result["payload"] = json.loads(result["payload"])
        results.append(result)
    return results


async def get_tail_raw(
    agent_id: uuid.UUID, task_slug: str, count: int = 10, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get last N events with full details (async wrapper).
    """
    return await asyncio.to_thread(_get_tail_raw_sync, agent_id, task_slug, count, offset)


def _get_latest_task_slug_sync(agent_id: uuid.UUID) -> Optional[str]:
    """
    Get the most recent task_slug for an agent (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT task_slug
                FROM agent_logs
                WHERE agent_id = %s
                GROUP BY task_slug
                ORDER BY MAX(timestamp) DESC
                LIMIT 1
            """,
                (agent_id,),
            )

            row = cur.fetchone()

    return row["task_slug"] if row else None


async def get_latest_task_slug(agent_id: uuid.UUID) -> Optional[str]:
    """
    Get the most recent task_slug for an agent (async wrapper).
    """
    return await asyncio.to_thread(_get_latest_task_slug_sync, agent_id)


def _insert_prompt_sync(
    agent_id: uuid.UUID,
    task_slug: str,
    author: str,
    prompt_text: str,
    session_id: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert prompt to prompts table (synchronous).
    """
    prompt_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO prompts (
                    id, agent_id, task_slug, author, prompt_text, session_id, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
                (prompt_id, agent_id, task_slug, author, prompt_text, session_id),
            )
            conn.commit()

    return prompt_id


async def insert_prompt(
    agent_id: uuid.UUID,
    task_slug: str,
    author: str,
    prompt_text: str,
    session_id: Optional[str] = None,
) -> uuid.UUID:
    """
    Insert prompt to prompts table (async wrapper).
    """
    return await asyncio.to_thread(_insert_prompt_sync, agent_id, task_slug, author, prompt_text, session_id)


# ═══════════════════════════════════════════════════════════
# SYSTEM LOGS OPERATIONS
# ═══════════════════════════════════════════════════════════


def _insert_system_log_sync(
    level: str,
    message: str,
    file_path: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Insert a system log entry (synchronous).
    """
    log_id = uuid.uuid4()

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO system_logs (
                    id, file_path, adw_id, adw_step, level, message, metadata, timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """,
                (
                    log_id,
                    file_path,
                    adw_id,
                    adw_step,
                    level,
                    message,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

    return log_id


async def insert_system_log(
    level: str,
    message: str,
    file_path: Optional[str] = None,
    adw_id: Optional[str] = None,
    adw_step: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> uuid.UUID:
    """
    Insert a system log entry (async wrapper).
    """
    return await asyncio.to_thread(
        _insert_system_log_sync,
        level,
        message,
        file_path,
        adw_id,
        adw_step,
        metadata
    )


# ═══════════════════════════════════════════════════════════
# EVENT STREAM FUNCTIONS
# ═══════════════════════════════════════════════════════════


def _list_agent_logs_sync(
    orchestrator_agent_id: uuid.UUID, limit: int = DEFAULT_AGENT_LOG_LIMIT, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get all agent logs for agents belonging to this orchestrator (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT al.id, al.agent_id, al.session_id, al.task_slug, al.adw_id, al.adw_step,
                       al.entry_index, al.event_category, al.event_type, al.content, al.payload,
                       al.summary, al.timestamp,
                       a.name as agent_name
                FROM agent_logs al
                LEFT JOIN agents a ON al.agent_id = a.id
                WHERE a.orchestrator_agent_id = %s
                ORDER BY al.timestamp DESC
                LIMIT %s OFFSET %s
            """,
                (orchestrator_agent_id, limit, offset),
            )

            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if isinstance(result.get("payload"), str):
                    result["payload"] = json.loads(result["payload"])
                results.append(result)
            return results


async def list_agent_logs(
    orchestrator_agent_id: uuid.UUID, limit: int = DEFAULT_AGENT_LOG_LIMIT, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get all agent logs for agents belonging to this orchestrator (async wrapper).
    """
    return await asyncio.to_thread(_list_agent_logs_sync, orchestrator_agent_id, limit, offset)


def _list_system_logs_sync(
    limit: int = DEFAULT_SYSTEM_LOG_LIMIT,
    offset: int = 0,
    message_contains: Optional[str] = None,
    level: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get system logs with optional filtering (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Build dynamic query with filters
            query = """
                SELECT id, file_path, adw_id, level, message, summary, metadata, timestamp
                FROM system_logs
                WHERE 1=1
            """
            params = []

            # Add message filter if provided
            if message_contains and message_contains.strip():
                query += " AND message ILIKE %s"
                params.append(f"%{message_contains}%")

            # Add level filter if provided
            if level and level.strip():
                query += " AND level = %s"
                params.append(level.upper())

            # Add ordering and pagination
            query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(query, tuple(params))
            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                results.append(result)
            return results


async def list_system_logs(
    limit: int = DEFAULT_SYSTEM_LOG_LIMIT,
    offset: int = 0,
    message_contains: Optional[str] = None,
    level: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get system logs with optional filtering (async wrapper).
    """
    return await asyncio.to_thread(_list_system_logs_sync, limit, offset, message_contains, level)


def _get_orchestrator_action_blocks_sync(
    orchestrator_agent_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get orchestrator action blocks from system_logs (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT id, level, message, summary, metadata, timestamp
                FROM system_logs
                WHERE metadata->>'orchestrator_agent_id' = %s
                AND metadata->>'type' IN ('thinking_block', 'tool_use_block')
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
            """

            cur.execute(query, (str(orchestrator_agent_id), limit, offset))
            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                results.append(result)
            return results


async def get_orchestrator_action_blocks(
    orchestrator_agent_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get orchestrator action blocks from system_logs (async wrapper).
    """
    return await asyncio.to_thread(_get_orchestrator_action_blocks_sync, orchestrator_agent_id, limit, offset)


def _list_orchestrator_chat_sync(
    orchestrator_agent_id: Optional[uuid.UUID] = None,
    limit: int = DEFAULT_AGENT_LOG_LIMIT,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get orchestrator chat logs (synchronous).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if orchestrator_agent_id:
                cur.execute(
                    """
                    SELECT id, created_at, updated_at, orchestrator_agent_id,
                           sender_type, receiver_type, message, agent_id, metadata
                    FROM orchestrator_chat
                    WHERE orchestrator_agent_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """,
                    (orchestrator_agent_id, limit, offset),
                )
            else:
                cur.execute(
                    """
                    SELECT id, created_at, updated_at, orchestrator_agent_id,
                           sender_type, receiver_type, message, agent_id, metadata
                    FROM orchestrator_chat
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """,
                    (limit, offset),
                )

            rows = cur.fetchall()

            results = []
            for row in rows:
                result = dict(row)
                if isinstance(result.get("metadata"), str):
                    result["metadata"] = json.loads(result["metadata"])
                results.append(result)
            return results


async def list_orchestrator_chat(
    orchestrator_agent_id: Optional[uuid.UUID] = None,
    limit: int = DEFAULT_AGENT_LOG_LIMIT,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get orchestrator chat logs (async wrapper).
    """
    return await asyncio.to_thread(_list_orchestrator_chat_sync, orchestrator_agent_id, limit, offset)
