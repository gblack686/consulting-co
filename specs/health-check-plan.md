# Implementation Plan: Health Check Endpoint with Timestamp

## Objective

Enhance the existing health check endpoint at `/health` to include a JSON response with status and timestamp. The orchestrator backend already has a health check endpoint, but it lacks a timestamp field which is essential for monitoring, debugging, and verifying service uptime.

## Requirements

1. Add an ISO 8601 formatted timestamp to the health check response
2. Maintain backward compatibility with existing fields (`status`, `service`, `websocket_connections`)
3. Follow existing code patterns and conventions in the codebase
4. The endpoint should require no authentication
5. Response should be JSON format

## Current State Analysis

**File:** `C:\Users\gblac\OneDrive\Desktop\tac\orchestrator-agent-with-adws\apps\orchestrator_3_stream\backend\main.py`

**Lines:** 220-228

**Current Implementation:**
```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.http_request("GET", "/health", 200)
    return {
        "status": "healthy",
        "service": "orchestrator-3-stream",
        "websocket_connections": ws_manager.get_connection_count(),
    }
```

## Technical Approach

Add ISO 8601 timestamp using Python's `datetime` module. The pattern `datetime.now().isoformat()` is already established throughout the codebase (see `websocket_manager.py`).

**New Response Example:**
```json
{
    "status": "healthy",
    "service": "orchestrator-3-stream",
    "timestamp": "2026-01-16T18:30:45.123456",
    "websocket_connections": 2
}
```

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/main.py` | Modify | Add datetime import and timestamp field |

## Step-by-Step Tasks

### Task 1: Add datetime import
Add `from datetime import datetime` to the imports section (around line 18)

### Task 2: Modify health check endpoint
Add the `timestamp` field to the return dictionary at line 227

**After:**
```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.http_request("GET", "/health", 200)
    return {
        "status": "healthy",
        "service": "orchestrator-3-stream",
        "timestamp": datetime.now().isoformat(),
        "websocket_connections": ws_manager.get_connection_count(),
    }
```

## Acceptance Criteria

| Criterion | Verification Method |
|-----------|---------------------|
| Status field present | GET /health, check JSON |
| Timestamp field present | GET /health, parse timestamp |
| Service field present | GET /health, check JSON |
| WebSocket count present | GET /health, check JSON |
| Response is JSON | Check response headers |
| HTTP 200 OK | GET /health, check status |
| Timestamp format valid | Parse with datetime.fromisoformat() |

## Risk Assessment

- **Breaking change risk:** Low - Adding field is non-breaking
- **Performance impact:** None - datetime.now() is negligible
