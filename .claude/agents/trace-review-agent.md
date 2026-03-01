# Trace Review Agent 🔍

*Periodic session analysis and insights extraction*

---

## Purpose

The Trace Review Agent automatically analyzes session traces every 10 turns to extract patterns, identify issues, and generate insights about the conversation flow.

---

## Capabilities

1. **Pattern Detection**: Identifies recurring themes and tool usage patterns
2. **Issue Identification**: Spots errors, bottlenecks, and inefficiencies
3. **Progress Tracking**: Monitors task completion and goal advancement
4. **Insight Generation**: Produces actionable recommendations

---

## Trigger Mechanism

- **Frequency**: Every 10 turns (configurable)
- **Trigger**: Automatic via turn counter in stop hook
- **Data Source**: Session transcript + Langfuse traces + Neo4j graph

---

## Analysis Process

1. **Fetch Recent Turns**: Retrieve last 10 turns from turn_counter.db
2. **Load Trace Data**: Pull Langfuse traces for the session
3. **Extract Patterns**: Analyze tool usage, message flow, token consumption
4. **Generate Insights**: Use Claude Sonnet to synthesize findings
5. **Store Results**: Save to `.claude/data/reviews/{session_id}/review_{turn}.md`

---

## Output Format

```markdown
# Session Review - Turn {turn_number}
**Session ID**: {session_id}
**Timestamp**: {timestamp}
**Turns Analyzed**: {start_turn} - {end_turn}

## Summary
{high-level overview of the session}

## Key Patterns
- {pattern 1}
- {pattern 2}
- {pattern 3}

## Tool Usage
- Most Used: {tool_name} ({count} times)
- Average Latency: {latency}ms
- Token Consumption: {input}/{output} tokens

## Issues Detected
- {issue 1}
- {issue 2}

## Recommendations
1. {recommendation 1}
2. {recommendation 2}

## Next Steps
- {suggested next action}
```

---

## Configuration

**Environment Variables**:
- `REVIEW_INTERVAL`: Number of turns between reviews (default: 10)
- `REVIEW_MODEL`: Claude model to use (default: claude-3-5-sonnet)
- `ENABLE_TRACE_REVIEW`: Enable/disable reviews (default: true)

---

## Integration Points

| Component | Purpose | Method |
|-----------|---------|--------|
| turn_counter.py | Turn tracking | SQLite query |
| Langfuse | Trace data | API/SDK |
| Neo4j | Graph context | Cypher query |
| mini-doc-agent | Recording | Agent call |

---

## Files

- **Agent Script**: `.claude/hooks/trace_review_agent.py`
- **Output Directory**: `.claude/data/reviews/{session_id}/`
- **Turn Counter**: `.claude/hooks/utils/turn_counter.py`

---

## Status

✅ **Active** - Automatically triggered every 10 turns

---

**Last Updated**: 2025-12-13
