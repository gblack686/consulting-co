#!/usr/bin/env python3
"""
Orchestrator 3 Stream Backend
FastAPI server for managing orchestrator agent workflows with PostgreSQL backend
"""

import asyncio
import argparse
import os
import sys
import uuid

# Fix Windows asyncio DNS resolution issues
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import time

from rich.table import Table
from rich.console import Console

# Import our custom modules
from modules import config
from modules.logger import get_logger
from modules.websocket_manager import get_websocket_manager
from modules import database
from modules.orchestrator_service import OrchestratorService, get_orchestrator_tools
from modules.agent_manager import AgentManager
from modules.orch_database_models import OrchestratorAgent

logger = get_logger()
ws_manager = get_websocket_manager()
console = Console()  # For startup table display only

# Parse CLI arguments before creating app
parser = argparse.ArgumentParser(description="Orchestrator 3 Stream Backend")
parser.add_argument(
    "--session", type=str, help="Resume existing orchestrator session (session ID)"
)
parser.add_argument(
    "--cwd", type=str, help="Set working directory for orchestrator and agents"
)
args, unknown = parser.parse_known_args()

# Store parsed args for lifespan
CLI_SESSION_ID = args.session
CLI_WORKING_DIR = args.cwd

# Set working directory (use CLI arg or default from config)
if CLI_WORKING_DIR:
    config.set_working_dir(CLI_WORKING_DIR)
else:
    # Use default from ORCHESTRATOR_WORKING_DIR env var or config
    logger.info(f"Using default working directory: {config.get_working_dir()}")


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.startup(
        {
            "Service": "Orchestrator 3 Stream Backend",
            "Description": "PostgreSQL-backed multi-agent orchestration",
            "Backend URL": config.BACKEND_URL,
            "WebSocket URL": config.WEBSOCKET_URL,
            "Database": "PostgreSQL (NeonDB)",
            "Logs Directory": str(config.LOG_DIR),
            "Working Directory": config.get_working_dir(),
        }
    )

    # Initialize database connection pool
    logger.info("Initializing database connection pool...")
    await database.init_pool(database_url=config.DATABASE_URL)
    logger.success("Database connection pool initialized")

    # Validate or load orchestrator
    if CLI_SESSION_ID:
        logger.info(f"Looking up orchestrator with session: {CLI_SESSION_ID}")
        orchestrator_data = await database.get_orchestrator_by_session(CLI_SESSION_ID)

        if not orchestrator_data:
            logger.error(f"❌ Session ID not found: {CLI_SESSION_ID}")
            logger.info("Checking if this is a legacy session or orchestrator ID...")

            # Try to find any orchestrator for debugging
            all_orchestrators = await database.get_orchestrator()
            if all_orchestrators:
                logger.info(f"Found orchestrator in database:")
                logger.info(f"  ID: {all_orchestrators.get('id')}")
                logger.info(f"  Session ID: {all_orchestrators.get('session_id')}")
                logger.info(f"\nTo resume, use: --session {all_orchestrators.get('session_id')}")

            raise ValueError(
                f"Session ID '{CLI_SESSION_ID}' not found in orchestrator_agents.session_id.\n\n"
                f"This usually happens when:\n"
                f"  1. The session_id has not been set yet (run without --session first)\n"
                f"  2. Database tables were recreated (data loss)\n"
                f"  3. Session ID was mistyped\n\n"
                f"Solution: Remove the --session argument to start a fresh session."
            )

        # Parse to Pydantic model
        orchestrator = OrchestratorAgent(**orchestrator_data)
        logger.success(f"✅ Resumed orchestrator with session: {CLI_SESSION_ID}")
        logger.info(f"  Orchestrator ID: {orchestrator.id}")
        logger.info(
            f"  Total tokens: {orchestrator.input_tokens + orchestrator.output_tokens}"
        )
        logger.info(f"  Total cost: ${orchestrator.total_cost:.4f}")
    else:
        # No --session provided: Always create new orchestrator
        logger.info("Creating new orchestrator session...")

        # Read system prompt from file
        system_prompt_content = Path(config.ORCHESTRATOR_SYSTEM_PROMPT_PATH).read_text()

        orchestrator_data = await database.create_new_orchestrator(
            system_prompt=system_prompt_content,
            working_dir=config.get_working_dir(),
        )
        # Parse to Pydantic model
        orchestrator = OrchestratorAgent(**orchestrator_data)
        logger.success(f"✅ New orchestrator created: {orchestrator.id}")
        logger.info(f"  Session ID: {orchestrator.session_id or 'Not set yet (will be set after first interaction)'}")
        logger.info(f"  Status: {orchestrator.status}")

    # Initialize agent manager (scoped to this orchestrator)
    logger.info("Initializing agent manager...")
    agent_manager = AgentManager(
        orchestrator_agent_id=orchestrator.id,
        ws_manager=ws_manager,
        logger=logger,
        working_dir=config.get_working_dir()
    )
    logger.success(f"Agent manager initialized for orchestrator {orchestrator.id}")

    # Initialize orchestrator service with agent manager
    logger.info("Initializing orchestrator service...")
    orchestrator_service = OrchestratorService(
        ws_manager=ws_manager,
        logger=logger,
        agent_manager=agent_manager,
        session_id=CLI_SESSION_ID or orchestrator.session_id,
        working_dir=config.get_working_dir(),
    )

    # Store in app state for access in endpoints
    app.state.orchestrator_service = orchestrator_service
    app.state.orchestrator = orchestrator

    logger.success("Backend initialization complete")

    yield  # Server runs

    # Shutdown
    logger.info("Closing database connection pool...")
    await database.close_pool()
    logger.shutdown()


# Create FastAPI app with lifespan
app = FastAPI(title="Orchestrator 3 Stream API", version="1.0.0", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # From .env configuration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════


class LoadChatRequest(BaseModel):
    """Request model for loading chat history"""

    orchestrator_agent_id: str
    limit: Optional[int] = 50


class SendChatRequest(BaseModel):
    """Request model for sending chat message"""

    message: str
    orchestrator_agent_id: str


class ChangeWorkingDirRequest(BaseModel):
    """Request model for changing working directory"""

    working_dir: str


# ═══════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.http_request("GET", "/health", 200)
    return {
        "status": "healthy",
        "service": "orchestrator-3-stream",
        "websocket_connections": ws_manager.get_connection_count(),
    }


@app.get("/get_orchestrator")
async def get_orchestrator_info():
    """
    Get orchestrator agent information including system metadata.

    Fetches fresh data from database to ensure session_id is always current.
    Returns orchestrator ID, session, costs, metadata, slash commands, and templates.
    """
    try:
        logger.http_request("GET", "/get_orchestrator")

        # Refresh orchestrator from database to get current session_id
        orchestrator_id = app.state.orchestrator.id
        orchestrator_data = await database.get_orchestrator_by_id(orchestrator_id)

        if not orchestrator_data:
            logger.error(f"Orchestrator not found in database: {orchestrator_id}")
            raise HTTPException(status_code=404, detail="Orchestrator not found")

        # Update app.state with fresh data (keeps in-memory cache synchronized)
        orchestrator = OrchestratorAgent(**orchestrator_data)
        app.state.orchestrator = orchestrator

        # Discover slash commands
        slash_commands = discover_slash_commands(config.get_working_dir())

        # Get agent templates from SubagentRegistry
        from modules.subagent_loader import SubagentRegistry
        registry = SubagentRegistry(config.get_working_dir(), logger)
        templates = registry.list_templates()

        # Get orchestrator tools
        orchestrator_tools = get_orchestrator_tools()

        # Prepare metadata with fallback for system_message_info
        metadata = orchestrator.metadata or {}

        # If system_message_info doesn't exist, create fallback from current state
        if not metadata.get("system_message_info"):
            metadata["system_message_info"] = {
                "session_id": orchestrator.session_id,
                "cwd": orchestrator.working_dir or config.get_working_dir(),
                "captured_at": None,  # Indicates this is fallback data
                "subtype": "fallback"  # Indicates this wasn't from a SystemMessage
            }

        logger.http_request("GET", "/get_orchestrator", 200)
        return {
            "status": "success",
            "orchestrator": {
                "id": str(orchestrator.id),
                "session_id": orchestrator.session_id,
                "status": orchestrator.status,
                "working_dir": orchestrator.working_dir,
                "input_tokens": orchestrator.input_tokens,
                "output_tokens": orchestrator.output_tokens,
                "total_cost": float(orchestrator.total_cost),
                "metadata": metadata,  # Include metadata with fallback
            },
            "slash_commands": slash_commands,  # List of available commands
            "agent_templates": templates,      # List of available templates
            "orchestrator_tools": orchestrator_tools,  # NEW: List of management tools
        }
    except Exception as e:
        logger.error(f"Failed to get orchestrator info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_headers")
async def get_headers():
    """
    Get header information for the frontend.

    Returns:
        - cwd: Current working directory for orchestrator and agents
    """
    try:
        logger.http_request("GET", "/get_headers")

        cwd = config.get_working_dir()

        logger.http_request("GET", "/get_headers", 200)
        return {"status": "success", "cwd": cwd}
    except Exception as e:
        logger.error(f"Failed to get headers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/browse_folder")
async def browse_folder():
    """
    Open a native folder picker dialog and return the selected path.

    Uses tkinter to display a folder selection dialog on the server machine.
    This is useful for local development where the backend runs on the same machine.

    Returns:
        - status: success/cancelled/error
        - path: Selected folder path (if success)
    """
    import threading
    import queue

    result_queue = queue.Queue()

    def open_dialog():
        try:
            import tkinter as tk
            from tkinter import filedialog

            # Create root window with proper Windows focus handling
            root = tk.Tk()
            root.withdraw()

            # Multiple focus techniques for Windows compatibility
            root.attributes('-topmost', True)
            root.lift()
            root.focus_force()
            root.update()

            # Open folder selection dialog with parent set
            folder_path = filedialog.askdirectory(
                parent=root,
                title="Select Working Directory",
                initialdir=config.get_working_dir()
            )

            root.destroy()

            if folder_path:
                result_queue.put({"status": "success", "path": folder_path})
            else:
                result_queue.put({"status": "cancelled", "path": None})
        except Exception as e:
            result_queue.put({"status": "error", "error": str(e)})

    # Run tkinter in a separate thread to avoid blocking
    dialog_thread = threading.Thread(target=open_dialog)
    dialog_thread.start()
    dialog_thread.join(timeout=60)  # Wait up to 60 seconds

    if result_queue.empty():
        return {"status": "error", "error": "Dialog timed out"}

    return result_queue.get()


@app.post("/change_working_dir")
async def change_working_dir(request: ChangeWorkingDirRequest):
    """
    Change the working directory and fully reconnect the orchestrator.

    This endpoint:
    1. Validates the new directory exists
    2. Updates the config working directory
    3. Creates a NEW orchestrator agent with the new working directory
    4. Re-discovers slash commands and agent templates
    5. Returns new orchestrator info + commands/templates
    6. Broadcasts change via WebSocket

    Returns:
        - status: success/error
        - orchestrator: New orchestrator info
        - slash_commands: Discovered slash commands
        - agent_templates: Available agent templates
        - orchestrator_tools: Available orchestrator tools
    """
    try:
        logger.http_request("POST", "/change_working_dir")
        new_dir = request.working_dir

        # 1. Validate the path exists
        if not os.path.isdir(new_dir):
            logger.error(f"Directory does not exist: {new_dir}")
            raise HTTPException(
                status_code=400,
                detail=f"Directory does not exist: {new_dir}"
            )

        logger.info(f"Changing working directory to: {new_dir}")

        # 2. Update config
        config.set_working_dir(new_dir)

        # 3. Create new orchestrator with new session
        system_prompt_content = Path(config.ORCHESTRATOR_SYSTEM_PROMPT_PATH).read_text()

        orchestrator_data = await database.create_new_orchestrator(
            system_prompt=system_prompt_content,
            working_dir=new_dir,
        )
        # Parse to Pydantic model
        new_orchestrator = OrchestratorAgent(**orchestrator_data)
        logger.success(f"✅ New orchestrator created: {new_orchestrator.id}")
        logger.info(f"  Working directory: {new_dir}")

        # 4. Initialize new agent manager and orchestrator service
        new_agent_manager = AgentManager(
            orchestrator_agent_id=new_orchestrator.id,
            ws_manager=ws_manager,
            logger=logger,
            working_dir=new_dir
        )

        new_orchestrator_service = OrchestratorService(
            ws_manager=ws_manager,
            logger=logger,
            agent_manager=new_agent_manager,
            session_id=new_orchestrator.session_id,
            working_dir=new_dir,
        )

        # Update app state with new services
        app.state.orchestrator_service = new_orchestrator_service
        app.state.orchestrator = new_orchestrator

        # 5. Re-discover slash commands and templates
        slash_commands = discover_slash_commands(new_dir)

        from modules.subagent_loader import SubagentRegistry
        registry = SubagentRegistry(new_dir, logger)
        templates = registry.list_templates()

        orchestrator_tools = get_orchestrator_tools()

        # 6. Run validation test - send a simple message to verify orchestrator works
        validation_result = {"success": False, "message": "Not tested"}
        try:
            logger.info("🧪 Running validation test on new orchestrator...")

            # Run a quick validation by checking if the session can be initialized
            test_result = await new_orchestrator_service.validate_connection()
            if test_result:
                validation_result = {"success": True, "message": "Orchestrator validated successfully"}
                logger.success("✅ Orchestrator validation passed")
            else:
                validation_result = {"success": False, "message": "Validation returned false"}
                logger.warning("⚠️ Orchestrator validation failed - orchestrator may need manual testing")
        except Exception as validation_error:
            validation_result = {"success": False, "message": str(validation_error)}
            logger.warning(f"⚠️ Orchestrator validation error: {validation_error}")
            # Don't fail the whole request - orchestrator is created, just validation failed

        # 7. Broadcast change via WebSocket
        await ws_manager.broadcast({
            "type": "working_dir_changed",
            "data": {
                "working_dir": new_dir,
                "orchestrator_id": str(new_orchestrator.id),
                "session_id": new_orchestrator.session_id,
                "validation": validation_result,
            }
        })

        logger.http_request("POST", "/change_working_dir", 200)
        return {
            "status": "success",
            "message": f"Working directory changed to: {new_dir}",
            "validation": validation_result,
            "orchestrator": {
                "id": str(new_orchestrator.id),
                "session_id": new_orchestrator.session_id,
                "status": new_orchestrator.status,
                "working_dir": new_orchestrator.working_dir,
                "input_tokens": new_orchestrator.input_tokens,
                "output_tokens": new_orchestrator.output_tokens,
                "total_cost": float(new_orchestrator.total_cost),
                "metadata": new_orchestrator.metadata or {},
            },
            "slash_commands": slash_commands,
            "agent_templates": templates,
            "orchestrator_tools": orchestrator_tools,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change working directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# SLASH COMMAND DISCOVERY
# ═══════════════════════════════════════════════════════════

# Import slash command discovery from parser module
from modules.slash_command_parser import discover_slash_commands


class OpenFileRequest(BaseModel):
    """Request model for opening a file in IDE"""
    file_path: str


@app.post("/api/open-file")
async def open_file_in_ide(request: OpenFileRequest):
    """
    Open a file in the configured IDE (Cursor or VS Code).

    Opens the file using the IDE command specified in config.IDE_COMMAND.
    """
    try:
        import subprocess

        logger.http_request("POST", "/api/open-file")

        if not config.IDE_ENABLED:
            logger.http_request("POST", "/api/open-file", 403)
            return {
                "status": "error",
                "message": "IDE integration is disabled in configuration"
            }

        file_path = request.file_path

        # Validate file exists
        if not os.path.exists(file_path):
            logger.http_request("POST", "/api/open-file", 404)
            return {"status": "error", "message": f"File not found: {file_path}"}

        # Build IDE command
        ide_cmd = config.IDE_COMMAND
        full_command = [ide_cmd, file_path]

        logger.info(f"Opening file in {ide_cmd}: {file_path}")

        # Execute IDE command
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.http_request("POST", "/api/open-file", 200)
            return {
                "status": "success",
                "message": f"Opened {file_path} in {ide_cmd}",
                "file_path": file_path
            }
        else:
            logger.error(f"Failed to open file in IDE: {result.stderr}")
            logger.http_request("POST", "/api/open-file", 500)
            return {
                "status": "error",
                "message": f"Failed to open file in IDE: {result.stderr}"
            }

    except subprocess.TimeoutExpired:
        logger.error("IDE command timed out")
        logger.http_request("POST", "/api/open-file", 500)
        return {"status": "error", "message": "IDE command timed out"}
    except FileNotFoundError:
        logger.error(f"IDE command not found: {config.IDE_COMMAND}")
        logger.http_request("POST", "/api/open-file", 500)
        return {
            "status": "error",
            "message": f"IDE command not found: {config.IDE_COMMAND}. Please ensure it's installed and in PATH."
        }
    except Exception as e:
        logger.error(f"Failed to open file in IDE: {e}")
        logger.http_request("POST", "/api/open-file", 500)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/load_chat")
async def load_chat(request: LoadChatRequest):
    """
    Load chat history for orchestrator agent.

    Returns:
        - messages: List of chat messages
        - turn_count: Total number of messages
    """
    try:
        logger.http_request("POST", "/load_chat")

        service: OrchestratorService = app.state.orchestrator_service
        result = await service.load_chat_history(
            orchestrator_agent_id=request.orchestrator_agent_id, limit=request.limit
        )

        logger.http_request("POST", "/load_chat", 200)
        return {
            "status": "success",
            "messages": result["messages"],
            "turn_count": result["turn_count"],
        }

    except Exception as e:
        logger.error(f"Failed to load chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_chat")
async def send_chat(request: SendChatRequest):
    """
    Send message to orchestrator agent.

    Message is processed with streaming via WebSocket.
    This endpoint returns immediately after starting execution.

    Returns:
        - status: success/error
        - message: Confirmation message
    """
    try:
        logger.http_request("POST", "/send_chat")

        service: OrchestratorService = app.state.orchestrator_service

        # Process message asynchronously (streaming via WebSocket)
        asyncio.create_task(
            service.process_user_message(
                user_message=request.message,
                orchestrator_agent_id=request.orchestrator_agent_id,
            )
        )

        logger.http_request("POST", "/send_chat", 200)
        return {
            "status": "success",
            "message": "Message received, processing with streaming",
        }

    except Exception as e:
        logger.error(f"Failed to send chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_events")
async def get_events_endpoint(
    agent_id: Optional[str] = None,
    task_slug: Optional[str] = None,
    event_types: str = "all",
    limit: int = 50,
    offset: int = 0,
):
    """
    Get events from all sources for EventStream component.

    Query params:
        - agent_id: Optional filter by agent UUID
        - task_slug: Optional filter by task
        - event_types: Comma-separated list or "all" (default: "all")
        - limit: Max events to return (default 50)
        - offset: Pagination offset (default 0)

    Returns:
        - status: success/error
        - events: List of unified events with sourceType field
        - count: Total event count
    """
    try:
        logger.http_request("GET", "/get_events")

        # Parse event types (default: agent_logs and orchestrator_chat only, no system_logs)
        requested_types = (
            event_types.split(",")
            if event_types != "all"
            else ["agent_logs", "orchestrator_chat"]
        )

        all_events = []

        # Fetch agent logs
        if "agent_logs" in requested_types:
            agent_uuid = uuid.UUID(agent_id) if agent_id else None
            if agent_uuid:
                agent_logs = await database.get_agent_logs(
                    agent_id=agent_uuid, task_slug=task_slug, limit=limit, offset=offset
                )
            else:
                agent_logs = await database.list_agent_logs(
                    orchestrator_agent_id=app.state.orchestrator.id,
                    limit=limit,
                    offset=offset
                )

            # Add sourceType field
            for log in agent_logs:
                log["sourceType"] = "agent_log"
                all_events.append(log)

        # Fetch system logs
        if "system_logs" in requested_types:
            system_logs = await database.list_system_logs(limit=limit, offset=offset)
            for log in system_logs:
                log["sourceType"] = "system_log"
                all_events.append(log)

        # Fetch orchestrator chat (filtered by current orchestrator)
        if "orchestrator_chat" in requested_types:
            chat_logs = await database.list_orchestrator_chat(
                orchestrator_agent_id=app.state.orchestrator.id,
                limit=limit,
                offset=offset
            )
            for log in chat_logs:
                log["sourceType"] = "orchestrator_chat"
                all_events.append(log)

        # Sort by timestamp (newest first for limiting)
        all_events.sort(
            key=lambda x: x.get("timestamp") or x.get("created_at"), reverse=True
        )

        # Apply limit to get most recent events
        all_events = all_events[:limit]

        # Reverse to show oldest at top, newest at bottom
        all_events.reverse()

        # Convert UUIDs and datetimes to strings for JSON
        for event in all_events:
            for key, value in list(event.items()):
                if isinstance(value, uuid.UUID):
                    event[key] = str(value)
                elif hasattr(value, "isoformat"):
                    event[key] = value.isoformat()

        logger.http_request("GET", "/get_events", 200)
        return {"status": "success", "events": all_events, "count": len(all_events)}

    except Exception as e:
        logger.error(f"Failed to get events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_agents")
async def list_agents_endpoint():
    """
    List all active agents for sidebar display.

    Returns:
        - status: success/error
        - agents: List of agent objects enriched with log_count from agent_logs table
    """
    try:
        logger.http_request("GET", "/list_agents")

        agents = await database.list_agents(
            orchestrator_agent_id=app.state.orchestrator.id,
            archived=False
        )

        # Serialize Pydantic models to dicts
        agents_data = [agent.model_dump() for agent in agents]

        # Enrich each agent with log count from agent_logs table
        from psycopg2.extras import RealDictCursor
        with database.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for agent_data in agents_data:
                    agent_id = agent_data["id"]

                    # Count logs for this agent from agent_logs table
                    cur.execute(
                        "SELECT COUNT(*) FROM agent_logs WHERE agent_id = %s", (agent_id,)
                    )
                    result = cur.fetchone()
                    agent_data["log_count"] = result["count"] if result else 0

        logger.http_request("GET", "/list_agents", 200)
        return {"status": "success", "agents": agents_data}

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ADW DISPATCH ENDPOINTS (Hybrid Orchestrator)
# ═══════════════════════════════════════════════════════════

class ADWDispatchRequest(BaseModel):
    """Request model for ADW dispatch"""
    task: str
    working_dir: Optional[str] = None
    force_mode: Optional[str] = None  # "local", "github", or None for auto


class ADWStatusResponse(BaseModel):
    """Response model for ADW status"""
    run_id: Optional[int] = None
    status: str
    conclusion: Optional[str] = None
    url: Optional[str] = None
    started_at: Optional[str] = None


@app.post("/api/adw/dispatch-github")
async def dispatch_github_adw(request: ADWDispatchRequest):
    """
    Dispatch ADW to GitHub Actions for Opus-level execution.

    This triggers the adw-plan-build-review.yml workflow which:
    1. Runs the Plan phase (Opus)
    2. Runs the Build phase (Opus)
    3. Runs the Review phase (Opus)
    4. Creates artifacts and commits changes

    Returns:
        - status: success/error
        - workflow_url: URL to monitor the workflow
        - run_id: GitHub Actions run ID
    """
    import subprocess

    try:
        logger.http_request("POST", "/api/adw/dispatch-github")

        # Get GitHub config from environment
        repo = os.environ.get("GITHUB_REPO", "gblack686/consulting-co")
        workflow = os.environ.get("GITHUB_WORKFLOW", "adw-plan-build-review.yml")
        working_dir = request.working_dir or config.get_working_dir()

        # Trigger GitHub Actions workflow
        cmd = [
            "gh", "workflow", "run", workflow,
            "--repo", repo,
            "-f", f"task={request.task}",
            "-f", f"working_dir={working_dir}"
        ]

        logger.info(f"Triggering GitHub Actions ADW: {request.task[:50]}...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            workflow_url = f"https://github.com/{repo}/actions"

            # Broadcast to WebSocket clients
            await ws_manager.broadcast({
                "type": "adw_dispatched",
                "data": {
                    "mode": "github",
                    "task": request.task,
                    "workflow_url": workflow_url
                }
            })

            logger.http_request("POST", "/api/adw/dispatch-github", 200)
            return {
                "status": "success",
                "message": "GitHub Actions workflow triggered",
                "workflow_url": workflow_url,
                "task": request.task
            }
        else:
            logger.error(f"GitHub Actions dispatch failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to trigger workflow: {result.stderr}"
            )

    except subprocess.TimeoutExpired:
        logger.error("GitHub Actions dispatch timed out")
        raise HTTPException(status_code=504, detail="GitHub CLI timed out")
    except Exception as e:
        logger.error(f"Failed to dispatch GitHub ADW: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adw/github-status/{run_id}")
async def get_github_adw_status(run_id: int):
    """
    Get status of a GitHub Actions workflow run.

    Args:
        run_id: GitHub Actions run ID

    Returns:
        - status: queued, in_progress, completed
        - conclusion: success, failure, cancelled (if completed)
        - url: Link to the workflow run
    """
    import subprocess

    try:
        logger.http_request("GET", f"/api/adw/github-status/{run_id}")

        repo = os.environ.get("GITHUB_REPO", "gblack686/consulting-co")

        cmd = [
            "gh", "run", "view", str(run_id),
            "--repo", repo,
            "--json", "status,conclusion,url,startedAt,updatedAt"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            logger.http_request("GET", f"/api/adw/github-status/{run_id}", 200)
            return {
                "status": "success",
                "run": {
                    "run_id": run_id,
                    "status": data.get("status"),
                    "conclusion": data.get("conclusion"),
                    "url": data.get("url"),
                    "started_at": data.get("startedAt"),
                    "updated_at": data.get("updatedAt")
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    except Exception as e:
        logger.error(f"Failed to get GitHub ADW status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/adw/github-runs")
async def list_github_adw_runs(limit: int = 10):
    """
    List recent GitHub Actions ADW workflow runs.

    Args:
        limit: Maximum number of runs to return (default 10)

    Returns:
        - runs: List of recent workflow runs
    """
    import subprocess

    try:
        logger.http_request("GET", "/api/adw/github-runs")

        repo = os.environ.get("GITHUB_REPO", "gblack686/consulting-co")
        workflow = os.environ.get("GITHUB_WORKFLOW", "adw-plan-build-review.yml")

        cmd = [
            "gh", "run", "list",
            "--repo", repo,
            "--workflow", workflow,
            "--limit", str(limit),
            "--json", "databaseId,number,status,conclusion,startedAt,url"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            runs = json.loads(result.stdout)
            logger.http_request("GET", "/api/adw/github-runs", 200)
            return {
                "status": "success",
                "runs": runs
            }
        else:
            return {"status": "success", "runs": []}

    except Exception as e:
        logger.error(f"Failed to list GitHub ADW runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adw/dispatch-local")
async def dispatch_local_adw(request: ADWDispatchRequest):
    """
    Dispatch ADW to local Haiku execution.

    For simpler tasks that don't require Opus-level reasoning.

    Returns:
        - status: success/error
        - task_id: Local task identifier
    """
    try:
        logger.http_request("POST", "/api/adw/dispatch-local")

        working_dir = request.working_dir or config.get_working_dir()

        # Create agent via the agent manager
        service = app.state.orchestrator_service

        # Dispatch via orchestrator chat (will use Haiku)
        asyncio.create_task(
            service.process_user_message(
                user_message=f"[Local ADW] {request.task}",
                orchestrator_agent_id=str(app.state.orchestrator.id),
            )
        )

        # Broadcast to WebSocket clients
        await ws_manager.broadcast({
            "type": "adw_dispatched",
            "data": {
                "mode": "local",
                "task": request.task
            }
        })

        logger.http_request("POST", "/api/adw/dispatch-local", 200)
        return {
            "status": "success",
            "message": "Local ADW dispatched",
            "task": request.task,
            "mode": "local_haiku"
        }

    except Exception as e:
        logger.error(f"Failed to dispatch local ADW: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adw/auto-route")
async def auto_route_adw(request: ADWDispatchRequest):
    """
    Auto-route ADW based on task complexity.

    Analyzes the task and routes to:
    - Local Haiku: Simple tasks (<5000 tokens)
    - GitHub Actions Opus: Complex tasks (>20000 tokens)

    Returns:
        - status: success/error
        - routed_to: "local" or "github"
        - complexity: estimated complexity
    """
    try:
        logger.http_request("POST", "/api/adw/auto-route")

        task = request.task.lower()

        # Simple complexity estimation
        high_keywords = ["refactor", "implement", "architect", "migrate", "redesign"]
        low_keywords = ["typo", "comment", "rename", "format", "lint", "fix"]

        is_complex = any(kw in task for kw in high_keywords)
        is_simple = any(kw in task for kw in low_keywords)

        # Estimate tokens based on task length and keywords
        base_tokens = len(task.split()) * 100
        if is_complex:
            estimated_tokens = base_tokens * 3
        elif is_simple:
            estimated_tokens = base_tokens * 0.5
        else:
            estimated_tokens = base_tokens * 1.5

        # Route decision
        if request.force_mode == "local":
            routed_to = "local"
        elif request.force_mode == "github":
            routed_to = "github"
        elif estimated_tokens < 5000 or is_simple:
            routed_to = "local"
        elif estimated_tokens > 20000 or is_complex:
            routed_to = "github"
        else:
            routed_to = "local"  # Default to local for responsiveness

        # Dispatch to appropriate handler
        if routed_to == "github":
            result = await dispatch_github_adw(request)
        else:
            result = await dispatch_local_adw(request)

        logger.http_request("POST", "/api/adw/auto-route", 200)
        return {
            **result,
            "routed_to": routed_to,
            "estimated_tokens": int(estimated_tokens),
            "complexity": "high" if is_complex else ("low" if is_simple else "medium")
        }

    except Exception as e:
        logger.error(f"Failed to auto-route ADW: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates and chat messages"""

    await ws_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()

            # Log received message
            if data:
                logger.debug(f"📥 Received WebSocket message: {data[:100]}")

                # Try to parse as JSON for structured messages
                try:
                    message = json.loads(data)

                    # Route message based on type
                    if isinstance(message, dict) and "type" in message:
                        msg_type = message.get("type")
                        # Log unknown message types for future event handlers
                        logger.debug(f"Received WebSocket message type: {msg_type}")

                except json.JSONDecodeError:
                    # Not JSON, treat as plain text (keep alive ping)
                    pass

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    # Display startup banner
    table = Table(
        title="Orchestrator 3 Stream Configuration",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Backend URL", config.BACKEND_URL)
    table.add_row("WebSocket URL", config.WEBSOCKET_URL)
    table.add_row("Database", "PostgreSQL (NeonDB)")

    console.print(table)

    # Run the server with config ports
    uvicorn.run(app, host=config.BACKEND_HOST, port=config.BACKEND_PORT)
