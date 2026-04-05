# Observability-Graphiti-Obsidian Integration Test Suite

Comprehensive testing for the integration between Claude Code observability, Graphiti knowledge graph, and Obsidian note generation.

## Test Structure

```
tests/
├── unit/                          # Unit tests (no external dependencies)
│   ├── test_observe_to_graphiti.py       # Event transformation & Neo4j writes
│   ├── test_agent_progress_tracker.py    # Metric calculations
│   └── test_obsidian_exporter.py         # Note generation & formatting
│
├── integration/                   # Integration tests (requires live services)
│   └── test_integration_end_to_end.py    # Complete data flow testing
│
├── performance/                   # Performance benchmarks
│   └── test_performance_benchmarks.py    # Latency & throughput tests
│
├── compatibility/                 # Backwards compatibility
│   ├── test_backwards_compatibility.py   # Existing systems preserved
│   └── test_format_validation.py         # Config file validation
│
└── fixtures/                      # Test data fixtures
    └── sample_events.json                # Sample event payloads
```

## Prerequisites

### Services Required

1. **Neo4j** (for integration tests)
   - URI: `bolt://localhost:7687`
   - Username: `neo4j`
   - Password: Set in `.env` file

2. **Observability Server** (for integration tests)
   - URL: `http://localhost:4000`
   - Start with: `cd observability/apps/server && npm run dev`

3. **Python Dependencies**
   ```bash
   uv pip install pytest pytest-benchmark neo4j python-dotenv requests pyyaml jsonschema
   ```

## Running Tests

### Run All Tests

```bash
# From .claude directory
cd /c/Users/gblac/OneDrive/Desktop/consulting-co/.claude

# Run all tests
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only (no external dependencies)
pytest tests/unit/ -v

# Integration tests (requires Neo4j + observability server)
pytest tests/integration/ -v

# Performance benchmarks
pytest tests/performance/ -v --benchmark-only

# Compatibility tests
pytest tests/compatibility/ -v
```

### Run Individual Test Files

```bash
# Test observe_to_graphiti hook
pytest tests/unit/test_observe_to_graphiti.py -v

# Test agent progress tracker
pytest tests/unit/test_agent_progress_tracker.py -v

# Test end-to-end integration
pytest tests/integration/test_integration_end_to_end.py -v
```

## Test Scenarios

### Scenario 1: Single Tool Execution
**File**: `tests/integration/test_integration_end_to_end.py::TestEndToEndDataFlow::test_single_tool_execution_flow`

**Tests**:
- PreToolUse event creates Session + Tool nodes
- PostToolUse event updates Tool with latency
- Data persists in Neo4j

**Expected Result**:
```
Session node: {id: "test-session-123", status: "active"}
Tool node: {name: "Read", status: "completed", latency_ms: 2667}
Relationship: (Session)-[:EXECUTED]->(Tool)
```

### Scenario 2: Multi-Tool Session
**File**: `tests/integration/test_integration_end_to_end.py::TestEndToEndDataFlow::test_multi_tool_session_flow`

**Tests**:
- Multiple tools tracked in single session
- Average latency calculated correctly
- All tools linked to session

**Expected Result**:
```
3 Tool nodes created
Average latency: ~2000ms
Session has 3 EXECUTED relationships
```

### Scenario 3: Subagent Execution
**File**: `tests/integration/test_integration_end_to_end.py::TestEndToEndDataFlow::test_subagent_execution_flow`

**Tests**:
- Parent-child session relationship created
- Subagent marked as completed
- SPAWNED relationship established

**Expected Result**:
```
(ParentSession)-[:SPAWNED]->(SubagentSession)
SubagentSession.status = "completed"
```

### Scenario 4: Entity Extraction
**File**: `tests/integration/test_integration_end_to_end.py::TestEndToEndDataFlow::test_entity_extraction_flow`

**Tests**:
- Entities extracted from tool output
- Entity nodes created in Neo4j
- Entities linked to tools via DISCOVERED

**Expected Result**:
```
Tool output contains: "def process_data", "class UserRepository"
Entities created: {name: "process_data", type: "function"}, {name: "UserRepository", type: "class"}
Relationships: (Tool)-[:DISCOVERED]->(Entity)
```

## Performance Thresholds

### Event Processing
- **Target**: < 500ms per event
- **Critical**: < 1000ms per event

### Bulk Processing
- **Target**: < 5s for 100 events
- **Critical**: < 10s for 100 events
- **Throughput**: > 20 events/second

### Database Queries
- **Session Query**: < 100ms
- **Tool Aggregation**: < 200ms
- **Entity Discovery**: < 150ms
- **Subagent Hierarchy**: < 250ms

### Metric Calculation
- **Target**: < 100ms
- **Critical**: < 250ms

### Note Generation
- **Target**: < 1000ms
- **Critical**: < 2000ms

## Backwards Compatibility Checks

### Hooks Preserved
- ✓ `log_to_langfuse.py` - Langfuse integration
- ✓ `log_to_graphiti.py` - Original Graphiti integration
- ✓ All observability hooks (10 files)

### Configuration Valid
- ✓ `settings.local.json` is valid JSON
- ✓ All hook types registered correctly
- ✓ Environment variables configured

### No Conflicts
- ✓ No duplicate hook registrations
- ✓ Services use different ports
- ✓ Data isolated (separate databases)

## Test Reports

After running tests, generate reports:

```bash
# Generate HTML report
pytest tests/ -v --html=test_report.html --self-contained-html

# Generate JUnit XML report
pytest tests/ -v --junitxml=test_results.xml

# Generate coverage report
pytest tests/ -v --cov=hooks --cov=scripts --cov-report=html
```

## Troubleshooting

### Neo4j Connection Failed
```
Error: Failed to connect to bolt://localhost:7687
```

**Solution**:
1. Check Neo4j is running: `docker ps` or check Neo4j Desktop
2. Verify credentials in `.env` file
3. Test connection: `neo4j-admin ping`

### Observability Server Not Running
```
Error: Connection refused to http://localhost:4000
```

**Solution**:
1. Start observability server:
   ```bash
   cd observability/apps/server
   npm run dev
   ```
2. Verify server is running: `curl http://localhost:4000/events`

### Import Errors
```
ModuleNotFoundError: No module named 'neo4j'
```

**Solution**:
```bash
uv pip install neo4j python-dotenv pytest
```

### Test Failures Due to Stale Data
```
AssertionError: Expected 0 sessions, found 5
```

**Solution**:
Clean Neo4j database:
```cypher
MATCH (s:Session {source_app: 'test-app'})
DETACH DELETE s
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      neo4j:
        image: neo4j:5.15
        env:
          NEO4J_AUTH: neo4j/testpassword
        ports:
          - 7687:7687

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install pytest neo4j python-dotenv

      - name: Run tests
        env:
          NEO4J_URI: bolt://localhost:7687
          NEO4J_USER: neo4j
          NEO4J_PASSWORD: testpassword
        run: |
          pytest .claude/tests/ -v
```

## Contributing

When adding new tests:

1. **Unit tests** should not require external services
2. **Integration tests** should clean up after themselves
3. **Performance tests** should use `pytest-benchmark`
4. **Compatibility tests** should verify backwards compatibility

### Test Naming Convention

```python
def test_<feature>_<scenario>_<expected_outcome>(self):
    """Brief description of what this test verifies."""
    pass
```

### Example:

```python
def test_session_creation_with_valid_event_creates_node(self):
    """Verify Session node is created when valid event is processed."""
    # Arrange
    event = {...}

    # Act
    process_event(event)

    # Assert
    assert session_exists_in_neo4j(event['session_id'])
```

## Test Coverage Goals

- **Unit Tests**: > 80% code coverage
- **Integration Tests**: All critical paths tested
- **Performance Tests**: All thresholds validated
- **Compatibility Tests**: All existing features verified

## Next Steps

After tests pass:

1. Review test reports for any warnings
2. Check performance benchmarks against thresholds
3. Verify backwards compatibility passes
4. Generate final test summary report
5. Document any identified issues
