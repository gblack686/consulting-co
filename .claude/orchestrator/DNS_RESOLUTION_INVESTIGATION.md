# DNS Resolution Investigation Summary

## Problem
Windows asyncio DNS resolution fails when connecting to PostgreSQL databases (both asyncpg and psycopg3).

## Root Cause
Windows asyncio uses `ThreadPoolExecutor` for ALL DNS operations (including `getaddrinfo()`). This interacts poorly with:
1. Docker's seccomp profile (blocks clone3() syscall)
2. Windows networking stack (even native execution fails)

## What We Tried

### Attempt 1: asyncpg with Various Fixes
- ❌ Disabled uvloop
- ❌ Added DNS servers (8.8.8.8)
- ❌ Host networking mode
- ❌ seccomp=unconfined
- ❌ Downgraded to Debian bullseye
- ❌ WindowsSelectorEventLoopPolicy
- **Result**: All failed with `getaddrinfo failed`

### Attempt 2: Switch to psycopg3 (async)
- ✅ Successfully rewrote database.py module
- ✅ Pre-resolved hostname to IP using synchronous socket
- ❌ psycopg3 AsyncConnectionPool still uses asyncio DNS internally
- **Result**: Same `getaddrinfo failed` error

### Attempt 3: psycopg3 (synchronous)
- ✅ Pre-resolved hostname to IP
- ❌ Even synchronous psycopg3.connect() does DNS validation
- **Result**: Same `getaddrinfo failed` error

## What DID Work
- ✅ Synchronous socket.getaddrinfo() - resolves hostname successfully
- ✅ TCP socket connection - can reach server
- ✅ psycopg2 (old synchronous driver) - worked in previous tests

## Options Going Forward

### Option 1: Use psycopg2 (Old Synchronous Driver) ⭐ RECOMMENDED
**Pros:**
- Proven to work with Windows
- No asyncio DNS issues
- Can wrap with asyncio thread executor for FastAPI compatibility
- Stable and mature

**Cons:**
- Uses synchronous connections (need to wrap in executor)
- Slightly older API

**Effort**: 2-3 hours to adapt database.py

### Option 2: Docker with Fixed Networking
**Pros:**
- Production-like environment
- Isolates from Windows issues

**Cons:**
- Still hits seccomp/clone3() issues
- Multiple failed attempts already
- Complex debugging

**Effort**: Unknown (may not be solvable)

### Option 3: WSL2 Deployment
**Pros:**
- Linux environment on Windows
- Avoids Windows networking issues
- Better for development

**Cons:**
- Requires WSL2 setup
- Additional complexity

**Effort**: 1-2 hours setup + testing

### Option 4: SSH Tunnel to Database
**Pros:**
- Bypasses DNS entirely (connect to localhost)
- Works with any driver

**Cons:**
- Requires SSH tunnel management
- Additional moving part
- Not ideal for production

**Effort**: 30 minutes setup

## Recommendation

**Go with Option 1 (psycopg2)** because:
1. We already proved it works on Windows
2. FastAPI can easily wrap synchronous DB calls in thread executor
3. Minimal code changes needed
4. Most reliable solution

### Implementation Plan for psycopg2

1. Update `pyproject.toml`: Replace `psycopg[binary]` with `psycopg2-binary`
2. Modify `database.py`:
   - Use `psycopg2` instead of `psycopg`
   - Wrap DB calls in `asyncio.to_thread()` for FastAPI compatibility
   - Keep connection pooling with `psycopg2.pool.ThreadedConnectionPool`
3. Test connection
4. Start backend

**Time estimate**: 1-2 hours total

## Files Modified So Far

- ✅ `orchestrator_3_stream/backend/pyproject.toml` - Updated dependencies
- ✅ `orchestrator_3_stream/backend/modules/database.py` - Fully rewritten for psycopg3
- ✅ `orchestrator_3_stream/.env` - Updated DATABASE_URL with pooler

## Next Steps

**Immediate**: Decide which option to pursue
**Recommended**: Implement Option 1 (psycopg2)Human: continue