# Quick Start Guide - Observability-Graphiti-Obsidian Integration

Get the integration running in 5 minutes.

---

## Prerequisites Checklist

- [ ] Python 3.11+ installed
- [ ] `uv` package manager installed
- [ ] Neo4j database running
- [ ] Observability server running (optional for first test)

---

## Step 1: Environment Setup (2 minutes)

### 1.1 Create .env file

Create or update `.env` in project root:

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-actual-password

# Obsidian Vault (optional)
OBSIDIAN_VAULT_PATH=./observability/notes

# Project Name
PROJECT_NAME=consulting-co
```

### 1.2 Verify Neo4j is running

```bash
# Check Neo4j status
neo4j status

# If not running, start it
neo4j start

# Test connection
cypher-shell -a bolt://localhost:7687 -u neo4j -p your-password
```

---

## Step 2: Run Integration Test (2 minutes)

### 2.1 Run test script

```bash
cd C:\Users\gblac\OneDrive\Desktop\consulting-co

uv run .claude/scripts/test_integration.py
```

### 2.2 Expected Output

```
============================================================
      Observability-Graphiti-Obsidian Integration Test
============================================================

============================================================
                 Testing Neo4j Connection
============================================================

✓ Connected to Neo4j at bolt://localhost:7687

============================================================
            Testing Observability Database
============================================================

⚠ Observability database not found at ...
⚠ This is OK if observability server hasn't run yet

============================================================
              Testing observe_to_graphiti.py
============================================================

✓ observe_to_graphiti.py executed successfully
  ✓ Processed 0 events to Neo4j

============================================================
            Testing agent_progress_tracker.py
============================================================

✓ agent_progress_tracker.py executed successfully
  ⚠ No metrics found for test-integration:12345678

============================================================
              Testing obsidian_exporter.py
============================================================

✓ obsidian_exporter.py executed successfully
  ✓ Exported session note to observability/notes/sessions/...

============================================================
                  Verifying Neo4j Data
============================================================

✓ Found 1 test session(s) in Neo4j
  Latest session: test-20251115-...
  Tools: 0, Tier: fast

============================================================
               Verifying Obsidian Notes
============================================================

✓ Found 1 test session note(s)
  Latest note: test-integration_12345678.md

============================================================
                     Test Summary
============================================================

Tests Passed: 7/7

  neo4j                          ✓ PASS
  observability_db               ✓ PASS
  observe_to_graphiti            ✓ PASS
  agent_progress_tracker         ✓ PASS
  obsidian_exporter              ✓ PASS
  neo4j_data                     ✓ PASS
  obsidian_notes                 ✓ PASS

All tests passed!
```

---

## Step 3: Verify Output (1 minute)

### 3.1 Check Neo4j

```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p your-password
```

Run query:
```cypher
MATCH (s:Session {source_app: 'test-integration'})
RETURN s.id, s.status, s.performance_tier
LIMIT 1;
```

Expected: One test session returned.

### 3.2 Check Obsidian Notes

```bash
ls observability/notes/sessions/test-integration_*.md
```

Expected: One or more test session notes.

Open the note to verify:
```bash
cat observability/notes/sessions/test-integration_*.md
```

---

## Step 4: Test with Real Session (Optional)

### 4.1 Make sure hooks are registered

Verify `settings.local.json` contains:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {"command": "uv run .claude/hooks/observe_to_graphiti.py"},
          {"command": "uv run .claude/scripts/agent_progress_tracker.py"},
          {"command": "uv run .claude/scripts/obsidian_exporter.py"}
        ]
      }
    ]
  }
}
```

### 4.2 Run a Claude session

```bash
# Start Claude Code
claude

# Do some work (use tools like Read, Write, Bash)
# ...

# End session
exit
```

### 4.3 Check results

**Neo4j:**
```cypher
MATCH (s:Session)
WHERE s.source_app = 'consulting-co'
ORDER BY s.start_time DESC
LIMIT 1
RETURN s;
```

**Obsidian:**
```bash
ls -lt observability/notes/sessions/ | head
```

---

## Troubleshooting

### Test Failed: Neo4j Connection

**Error**: `Neo4j connection failed`

**Fix**:
1. Start Neo4j: `neo4j start`
2. Check password in `.env`
3. Verify URI: `bolt://localhost:7687`

### Test Failed: Script Execution

**Error**: `Script failed with return code 1`

**Fix**:
1. Check script exists: `ls .claude/hooks/observe_to_graphiti.py`
2. Verify uv is installed: `uv --version`
3. Check Python version: `python --version` (need 3.11+)

### No Data in Neo4j

**Issue**: Tests pass but no data appears

**Fix**:
1. Run test again: `uv run .claude/scripts/test_integration.py`
2. Check Neo4j logs for errors
3. Verify scripts have write permissions

### Obsidian Notes Not Created

**Issue**: No session notes in vault

**Fix**:
1. Check vault path exists: `mkdir -p observability/notes/sessions`
2. Verify OBSIDIAN_VAULT_PATH in `.env`
3. Check write permissions

---

## Next Steps

### 1. Explore Neo4j Data

Open Neo4j Browser: `http://localhost:7474`

Run queries:
```cypher
// All sessions
MATCH (s:Session)
RETURN s
LIMIT 10

// Session with tools
MATCH (s:Session)-[:EXECUTED]->(t:Tool)
RETURN s, t
LIMIT 20

// Discovered entities
MATCH (t:Tool)-[:DISCOVERED]->(e:Entity)
RETURN t, e
LIMIT 20
```

### 2. Browse Obsidian Vault

Open Obsidian and point to: `observability/notes/`

Navigate:
- `sessions/` - Individual session notes
- `daily/` - Daily summaries

Use Graph View to see relationships.

### 3. Customize Configuration

Edit config files:
- `.claude/config/observability.yaml` - Event processing
- `.claude/config/graphiti.yaml` - Neo4j schema
- `.claude/config/obsidian.yaml` - Note format

### 4. Add Custom Entity Extraction

Edit `.claude/hooks/observe_to_graphiti.py`:

```python
def extract_entities_from_tool_output(output: str, tool_name: str) -> List[dict]:
    entities = []

    # Add your custom extraction
    if tool_name == 'YourTool':
        # Extract your entities
        pass

    return entities
```

### 5. Customize Note Template

Edit `.claude/scripts/obsidian_exporter.py`:

```python
def generate_session_note(data: Dict) -> str:
    # Your custom template
    note = "# Your Format\n\n"
    # ...
    return note
```

---

## Clean Up Test Data

After verifying integration works, clean up test data:

### Neo4j
```cypher
MATCH (s:Session {source_app: 'test-integration'})
DETACH DELETE s;
```

### Obsidian
```bash
rm observability/notes/sessions/test-integration_*.md
```

---

## Usage Examples

### Query Slow Sessions

```cypher
MATCH (s:Session)
WHERE s.performance_tier = 'slow'
RETURN s.id, s.avg_tool_latency, s.total_tools
ORDER BY s.avg_tool_latency DESC
LIMIT 5;
```

### Find Sessions Working on Specific Files

```cypher
MATCH (e:Entity {name: 'config.yaml'})<-[:DISCOVERED]-(t:Tool)<-[:EXECUTED]-(s:Session)
RETURN s.id, s.source_app, s.start_time
ORDER BY s.start_time DESC;
```

### Session Subagent Hierarchy

```cypher
MATCH path = (parent:Session)-[:SPAWNED*]->(child:Session)
WHERE parent.id = 'your-session-id'
RETURN path;
```

### Most Used Tools

```cypher
MATCH (t:Tool)
WITH t.name as tool, count(*) as usage, avg(t.latency_ms) as avg_latency
RETURN tool, usage, avg_latency
ORDER BY usage DESC
LIMIT 10;
```

---

## Getting Help

1. **Read full documentation**: `.claude/context/implementation/OBSERVABILITY_GRAPHITI_OBSIDIAN_INTEGRATION.md`
2. **Check test output**: Look for error messages
3. **Verify environment**: Check `.env` file
4. **Review logs**: Scripts print to stderr

---

## Success Criteria

You know it's working when:

✓ Test script passes all tests
✓ Neo4j has Session nodes with metrics
✓ Obsidian vault has session notes
✓ Notes have timeline, entities, metrics
✓ Daily summaries are updated
✓ Real Claude sessions appear automatically

---

**Ready to start?**

```bash
# 1. Update .env with your Neo4j password
# 2. Run test
uv run .claude/scripts/test_integration.py

# 3. If all pass, you're ready!
claude  # Start using Claude Code normally
```

The integration will run automatically after each session.
