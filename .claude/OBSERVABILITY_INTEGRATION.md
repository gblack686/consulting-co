# Complete Observability + Knowledge Integration

**Date:** November 13, 2025
**Systems:** Obsidian + Graphiti + Langfuse + OpenTelemetry
**Goal:** Full-stack observability with knowledge management

---

## Executive Summary

This integration combines **four powerful systems** to create a comprehensive development intelligence platform:

### The Four Pillars

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Session                       │
└──────┬────────────┬────────────┬────────────┬───────────────┘
       │            │            │            │
       ▼            ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Obsidian │ │ Graphiti │ │ Langfuse │ │ OpenTel  │
│  (Notes) │ │  (Graph) │ │  (LLM)   │ │ (Traces) │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                  │
          ┌───────▼────────┐
          │  Unified View  │
          │   (Dashboard)  │
          └────────────────┘
```

### What Each System Provides

**📄 Obsidian** - Human-Curated Knowledge
- Markdown notes with rich formatting
- Manual organization and linking
- Architecture Decision Records (ADRs)
- Learning notes and task tracking

**🔗 Graphiti** - Automatic Knowledge Graph
- Entity and relationship extraction
- Temporal knowledge graph (Neo4j)
- Semantic search capabilities
- Pattern and trend detection

**📊 Langfuse** - LLM Observability
- Trace all Claude interactions
- Track token usage and costs
- Monitor prompt performance
- Session analytics

**🔍 OpenTelemetry** - Distributed Tracing
- End-to-end request tracing
- Performance profiling
- Error tracking
- Service dependency mapping

---

## Architecture Overview

### Data Flow

```
Session Start
     ↓
1. OTEL: Create root span
2. Langfuse: Create session trace
3. Obsidian: Load daily note
4. Graphiti: Load recent context
     ↓
User Prompt
     ↓
5. OTEL: Create prompt span
6. Langfuse: Log user message
7. Search: Obsidian + Graphiti (both traced)
     ↓
Claude Response
     ↓
8. OTEL: Create generation span
9. Langfuse: Log LLM generation (tokens, cost)
10. Tool Use (traced by OTEL + Langfuse)
     ↓
Session End
     ↓
11. Extract learnings → Obsidian + Graphiti
12. Langfuse: Flush session
13. OTEL: Close root span
14. Generate session report
```

### System Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                       Knowledge Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Obsidian ←→ Graphiti                                       │
│  (Bidirectional Sync)                                        │
│  - ADRs → Episodes                                          │
│  - Graph Insights → Notes                                    │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ Knowledge Queries
                           │
┌─────────────────────────────────────────────────────────────┐
│                    Observability Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Langfuse (LLM) ←→ OpenTelemetry (Tracing)                 │
│  - Langfuse traces embedded in OTEL spans                   │
│  - OTEL context propagated to Langfuse                      │
│  - Unified trace IDs                                         │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │ Analytics
                           │
┌─────────────────────────────────────────────────────────────┐
│                      Analytics Layer                         │
├─────────────────────────────────────────────────────────────┤
│  - Session metrics (duration, tokens, cost)                 │
│  - Knowledge utilization (search patterns)                   │
│  - Performance profiling (latency breakdown)                 │
│  - Cost optimization insights                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Obsidian ↔ Graphiti (Knowledge Sync)

**Implemented:** See `.claude/OBSIDIAN_GRAPHITI_INTEGRATION.md`

**Key Features:**
- Bidirectional sync
- Unified search
- Automatic entity extraction
- Pattern discovery

### 2. Langfuse + OpenTelemetry (Observability)

**NEW Integration:**

```python
# Hook example: Pre Tool Use
import json
from opentelemetry import trace
from utils.langfuse_client import get_langfuse_client

# Get OTEL tracer
tracer = trace.get_tracer(__name__)

# Get Langfuse client
langfuse = get_langfuse_client()

# Read hook data
hook_data = json.load(sys.stdin)
tool_name = hook_data.get("tool_name")
tool_input = hook_data.get("tool_input")
session_id = hook_data.get("session_id")

# Create OTEL span
with tracer.start_as_current_span(f"tool.{tool_name}") as span:
    span.set_attribute("tool.name", tool_name)
    span.set_attribute("session.id", session_id)

    # Create Langfuse trace (linked to OTEL)
    langfuse_trace = langfuse.trace_event(
        name=f"tool_{tool_name}",
        input_data=tool_input,
        session_id=session_id,
        metadata={"otel_span_id": span.get_span_context().span_id}
    )
```

### 3. Graphiti + OpenTelemetry (Graph Tracing)

**Already Supported by Graphiti:**

```python
from opentelemetry import trace
from graphiti_core import Graphiti

# Setup OTEL
tracer = trace.get_tracer(__name__)

# Pass tracer to Graphiti
graphiti = Graphiti(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    tracer=tracer,  # Graphiti auto-traces all operations
    trace_span_prefix="graphiti"
)

# All Graphiti operations now traced:
# - add_episode() → span
# - search() → span
# - build_indices_and_constraints() → span
```

### 4. Unified Session Context

**Links all systems together:**

```python
class SessionContext:
    """Unified context across all systems."""

    def __init__(self, session_id: str):
        self.session_id = session_id

        # OTEL root span
        self.tracer = trace.get_tracer(__name__)
        self.root_span = self.tracer.start_span(f"session.{session_id}")

        # Langfuse session
        self.langfuse = get_langfuse_client()
        self.langfuse_trace_id = None

        # Obsidian
        self.daily_note = None

        # Graphiti
        self.graphiti = None

    def start(self):
        """Initialize session across all systems."""
        with self.root_span:
            # Create Langfuse session trace
            self.langfuse_trace_id = self.langfuse.trace_event(
                name="session_start",
                session_id=self.session_id,
                metadata={"otel_trace_id": self.root_span.get_span_context().trace_id}
            )

            # Load Obsidian daily note (traced)
            with self.tracer.start_as_current_span("obsidian.load_daily_note"):
                self.daily_note = load_daily_note()

            # Initialize Graphiti with tracing
            self.graphiti = Graphiti(tracer=self.tracer)
```

---

## Implementation Details

### Directory Structure

```
.claude/
├── OBSERVABILITY_INTEGRATION.md       # This file
├── observability/
│   ├── config/
│   │   ├── langfuse.json              # Langfuse configuration
│   │   ├── otel-config.yaml           # OpenTelemetry exporters
│   │   └── unified-settings.json      # Combined settings
│   ├── utils/
│   │   ├── langfuse_client.py         # From nexus (copy)
│   │   ├── otel_tracer.py             # OTEL setup
│   │   ├── session_context.py         # Unified context
│   │   └── metrics_collector.py       # Analytics
│   └── dashboards/
│       ├── session-report.html        # Session summary
│       └── analytics.html             # Long-term analytics
├── hooks/
│   ├── session-start/
│   │   └── init-observability.py      # Start OTEL + Langfuse
│   ├── pre-tool-use/
│   │   └── trace-tool.py              # Trace tool execution
│   ├── post-tool-use/
│   │   └── log-tool-result.py         # Log results
│   ├── stop/
│   │   └── log-session.py             # Quick session log
│   └── session-end/
│       └── generate-report.py         # Full session report
└── skills/
    └── knowledge-sync/                 # Existing
        └── scripts/
            └── unified-search.py       # Now with OTEL tracing
```

### Configuration Files

#### `.claude/observability/config/langfuse.json`

```json
{
  "enabled": true,
  "host": "http://localhost:3000",
  "publicKey": "${LANGFUSE_PUBLIC_KEY}",
  "secretKey": "${LANGFUSE_SECRET_KEY}",
  "features": {
    "tracePrompts": true,
    "traceGenerations": true,
    "traceTools": true,
    "trackCosts": true,
    "trackLatency": true
  },
  "sampling": {
    "rate": 1.0,
    "minDuration": 0
  }
}
```

#### `.claude/observability/config/otel-config.yaml`

```yaml
exporters:
  # Console exporter for debugging
  console:
    enabled: true

  # OTLP exporter (for backends like Jaeger, Tempo, etc.)
  otlp:
    enabled: false
    endpoint: "http://localhost:4318"
    protocol: "http/protobuf"

  # Zipkin exporter
  zipkin:
    enabled: false
    endpoint: "http://localhost:9411/api/v2/spans"

processors:
  batch:
    timeout: 10s
    send_batch_size: 512

  resource:
    attributes:
      service.name: "claude-code"
      service.version: "1.0"
      deployment.environment: "local"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [console, otlp]
```

#### `.claude/observability/config/unified-settings.json`

```json
{
  "observability": {
    "enabled": true,
    "langfuse": {
      "enabled": true,
      "configPath": ".claude/observability/config/langfuse.json"
    },
    "opentelemetry": {
      "enabled": true,
      "configPath": ".claude/observability/config/otel-config.yaml"
    }
  },
  "knowledge": {
    "obsidian": {
      "enabled": true,
      "traced": true
    },
    "graphiti": {
      "enabled": true,
      "traced": true
    }
  },
  "analytics": {
    "generateSessionReport": true,
    "sessionReportPath": ".claude/reports/sessions/",
    "collectMetrics": true,
    "metricsPath": ".claude/metrics/",
    "retentionDays": 90
  },
  "performance": {
    "asyncTracing": true,
    "batchSize": 100,
    "flushInterval": 30
  }
}
```

---

## Hooks Implementation

### SessionStart Hook

**File:** `.claude/hooks/session-start/init-observability.py`

```python
#!/usr/bin/env python3
"""
Initialize observability stack on session start.
Sets up OTEL + Langfuse + loads knowledge context.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "observability" / "utils"))

from langfuse_client import get_langfuse_client
from session_context import SessionContext

async def main():
    # Read hook data
    hook_data = json.load(sys.stdin)
    session_id = hook_data.get("session_id", "unknown")

    # Setup OpenTelemetry
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)

    # Start root span
    with tracer.start_as_current_span(f"session.{session_id}") as root_span:
        root_span.set_attribute("session.id", session_id)
        root_span.set_attribute("start_time", datetime.now().isoformat())

        # Initialize Langfuse
        langfuse = get_langfuse_client()

        # Create session trace in Langfuse
        langfuse.trace_event(
            name="session_start",
            input_data={"session_id": session_id},
            session_id=session_id,
            metadata={
                "otel_trace_id": format(root_span.get_span_context().trace_id, "032x"),
                "otel_span_id": format(root_span.get_span_context().span_id, "016x")
            },
            tags=["session", "start"]
        )

        # Load Obsidian context (traced)
        with tracer.start_as_current_span("obsidian.load_context"):
            # Load daily note
            print("📄 Loading Obsidian daily note...")
            # (Implementation here)

        # Load Graphiti context (traced)
        with tracer.start_as_current_span("graphiti.load_context"):
            print("🔗 Loading Graphiti knowledge graph context...")
            # (Implementation here)

        # Save session context
        context = SessionContext(
            session_id=session_id,
            otel_trace_id=root_span.get_span_context().trace_id,
            langfuse_trace_id="trace_" + session_id
        )
        context.save()

        print(f"\n✓ Observability initialized for session: {session_id}")
        print(f"  - OTEL Trace ID: {format(root_span.get_span_context().trace_id, '032x')}")
        print(f"  - Langfuse Session: {session_id}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### PreToolUse Hook

**File:** `.claude/hooks/pre-tool-use/trace-tool.py`

```python
#!/usr/bin/env python3
"""
Trace tool execution with OTEL + Langfuse.
"""

import json
import sys
from pathlib import Path
from opentelemetry import trace

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "observability" / "utils"))

from langfuse_client import get_langfuse_client
from session_context import SessionContext

def main():
    hook_data = json.load(sys.stdin)

    tool_name = hook_data.get("tool_name")
    tool_input = hook_data.get("tool_input", {})
    session_id = hook_data.get("session_id")

    # Load session context
    context = SessionContext.load(session_id)

    # Get tracer
    tracer = trace.get_tracer(__name__)

    # Create OTEL span
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        span.set_attribute("session.id", session_id)

        # Extract key parameters
        for key, value in tool_input.items():
            if isinstance(value, (str, int, float, bool)):
                span.set_attribute(f"tool.input.{key}", value)

        # Log to Langfuse
        langfuse = get_langfuse_client()
        langfuse.span(
            trace_id=context.langfuse_trace_id,
            name=f"tool_{tool_name}",
            input_data={"tool": tool_name, "input": tool_input},
            metadata={
                "otel_span_id": format(span.get_span_context().span_id, "016x")
            }
        )

        print(f"[TRACE] Tool: {tool_name}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

### SessionEnd Hook

**File:** `.claude/hooks/session-end/generate-report.py`

```python
#!/usr/bin/env python3
"""
Generate comprehensive session report from all systems.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "observability" / "utils"))

from langfuse_client import get_langfuse_client
from session_context import SessionContext
from metrics_collector import collect_session_metrics

async def main():
    hook_data = json.load(sys.stdin)
    session_id = hook_data.get("session_id")

    # Load session context
    context = SessionContext.load(session_id)

    # Collect metrics from all sources
    metrics = await collect_session_metrics(session_id, context)

    # Generate report
    report = generate_session_report(metrics)

    # Save to Obsidian
    save_to_obsidian(report, session_id)

    # Flush Langfuse
    langfuse = get_langfuse_client()
    langfuse.flush()

    # Display summary
    print(f"\n{'='*60}")
    print(f"Session Report: {session_id}")
    print(f"{'='*60}")
    print(f"Duration: {metrics['duration']:.2f}s")
    print(f"Prompts: {metrics['prompt_count']}")
    print(f"Tools Used: {metrics['tool_count']}")
    print(f"Tokens: {metrics['total_tokens']} (${metrics['estimated_cost']:.4f})")
    print(f"Knowledge Searches: {metrics['search_count']}")
    print(f"Notes Created: {metrics['notes_created']}")
    print(f"Graph Episodes: {metrics['episodes_created']}")
    print(f"\n📊 Full report: .claude/reports/sessions/{session_id}.md")
    print(f"="*60)

def generate_session_report(metrics):
    """Generate markdown report."""
    return f"""# Session Report

**Session ID:** {metrics['session_id']}
**Date:** {metrics['date']}
**Duration:** {metrics['duration']:.2f}s

## Activity Summary

- **Prompts:** {metrics['prompt_count']}
- **Tool Calls:** {metrics['tool_count']}
- **Searches:** {metrics['search_count']}

## LLM Usage

- **Total Tokens:** {metrics['total_tokens']:,}
  - Prompt: {metrics['prompt_tokens']:,}
  - Completion: {metrics['completion_tokens']:,}
- **Estimated Cost:** ${metrics['estimated_cost']:.4f}
- **Model:** {metrics['model']}

## Knowledge Management

### Obsidian
- Notes Created: {metrics['notes_created']}
- Notes Updated: {metrics['notes_updated']}
- Searches: {metrics['obsidian_searches']}

### Graphiti
- Episodes Created: {metrics['episodes_created']}
- Entities Extracted: {metrics['entities_extracted']}
- Relationships Created: {metrics['relationships_created']}

## Performance

- **Average Response Time:** {metrics['avg_response_time']:.2f}s
- **Tool Execution Time:** {metrics['tool_time']:.2f}s
- **Search Time:** {metrics['search_time']:.2f}s

## Traces

- **OTEL Trace ID:** {metrics['otel_trace_id']}
- **Langfuse Session:** {metrics['langfuse_session_url']}

---

*Generated by Claude Code Observability*
"""

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Unified Search with Tracing

Update the existing unified search to include telemetry:

```python
# .claude/skills/knowledge-sync/scripts/unified-search.py

from opentelemetry import trace
from utils.langfuse_client import get_langfuse_client

class UnifiedSearch:
    def __init__(self, config: Dict):
        self.config = config
        self.tracer = trace.get_tracer(__name__)
        self.langfuse = get_langfuse_client()

    async def search(self, query: str, session_id: str) -> List[Dict]:
        """Search with full tracing."""

        with self.tracer.start_as_current_span("unified_search") as span:
            span.set_attribute("query", query)
            span.set_attribute("session.id", session_id)

            # Log to Langfuse
            search_trace = self.langfuse.trace_event(
                name="unified_search",
                input_data={"query": query},
                session_id=session_id
            )

            # Search both systems (each traced)
            with self.tracer.start_as_current_span("search.obsidian"):
                obsidian_results = await self._search_obsidian(query)
                span.set_attribute("results.obsidian", len(obsidian_results))

            with self.tracer.start_as_current_span("search.graphiti"):
                graphiti_results = await self._search_graphiti(query)
                span.set_attribute("results.graphiti", len(graphiti_results))

            # Merge
            with self.tracer.start_as_current_span("search.merge"):
                merged = self._merge_results(obsidian_results, graphiti_results)

            # Update Langfuse with results
            self.langfuse.span(
                trace_id=search_trace,
                name="search_complete",
                output_data={"total_results": len(merged)}
            )

            return merged
```

---

## Analytics & Dashboards

### Session Metrics Collection

**File:** `.claude/observability/utils/metrics_collector.py`

```python
"""
Collect metrics from all observability sources.
"""

from typing import Dict, Any
from datetime import datetime
import asyncio

async def collect_session_metrics(
    session_id: str,
    context: 'SessionContext'
) -> Dict[str, Any]:
    """
    Aggregate metrics from:
    - Langfuse (LLM usage, costs)
    - OTEL (performance, latency)
    - Obsidian (notes created/updated)
    - Graphiti (episodes, entities)
    """

    metrics = {
        "session_id": session_id,
        "date": datetime.now().isoformat(),
        "duration": 0,
        "prompt_count": 0,
        "tool_count": 0,
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "estimated_cost": 0.0,
        "search_count": 0,
        "notes_created": 0,
        "notes_updated": 0,
        "episodes_created": 0,
        "entities_extracted": 0,
        "relationships_created": 0,
        "avg_response_time": 0.0,
        "tool_time": 0.0,
        "search_time": 0.0
    }

    # Collect from each source in parallel
    results = await asyncio.gather(
        collect_langfuse_metrics(session_id),
        collect_otel_metrics(context.otel_trace_id),
        collect_obsidian_metrics(session_id),
        collect_graphiti_metrics(session_id)
    )

    # Merge results
    for result in results:
        metrics.update(result)

    return metrics
```

### Cost Tracking

```python
# Cost calculation from Langfuse data
PRICING = {
    "claude-sonnet-4-5": {
        "input": 3.00 / 1_000_000,   # $3 per 1M tokens
        "output": 15.00 / 1_000_000   # $15 per 1M tokens
    },
    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,
        "output": 0.60 / 1_000_000
    }
}

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate estimated cost based on model and tokens."""
    pricing = PRICING.get(model, PRICING["claude-sonnet-4-5"])
    cost = (prompt_tokens * pricing["input"]) + (completion_tokens * pricing["output"])
    return cost
```

---

## Benefits of Full Integration

### 1. Complete Visibility

**Before:**
- ❌ Don't know why responses are slow
- ❌ Don't know token usage per session
- ❌ Can't trace knowledge queries
- ❌ No cost breakdown

**After:**
- ✅ See exact latency breakdown (OTEL)
- ✅ Track tokens and costs (Langfuse)
- ✅ Trace every knowledge lookup (OTEL + Langfuse)
- ✅ Detailed cost attribution per session

### 2. Knowledge + Observability Synergy

**Unified Search Performance:**
```
/search authentication

OTEL Trace:
  ├─ unified_search (2.3s total)
  │   ├─ search.obsidian (0.8s) ← File search
  │   ├─ search.graphiti (1.2s) ← Graph query
  │   │   ├─ semantic_search (0.9s) ← OpenAI embedding
  │   │   └─ graph_traversal (0.3s) ← Neo4j query
  │   └─ search.merge (0.3s) ← Result merging

Langfuse Trace:
  - Tokens: 1,245 ($0.0037)
  - Cost breakdown:
    - Obsidian search: $0
    - Graphiti embedding: $0.0015 (500 tokens)
    - Graph entities: extracted 3 entities
```

### 3. Cost Optimization

**Track expensive operations:**
```
Session Cost Report:

Total: $0.45

Breakdown:
  - LLM Generations: $0.35 (77%)
  - Graphiti Extractions: $0.08 (18%)
  - Embeddings: $0.02 (5%)

Optimization Opportunities:
  ⚠️ High extraction cost - consider caching
  ⚠️ Multiple searches for same query - add cache
```

### 4. Performance Profiling

**Identify bottlenecks:**
```
Session Performance:

Slowest Operations:
  1. Graphiti search: 2.1s (semantic embedding)
  2. Neo4j query: 0.9s (complex traversal)
  3. Obsidian search: 0.7s (vault size)

Recommendations:
  - Cache Graphiti embeddings
  - Optimize Neo4j indices
  - Index Obsidian vault
```

---

## Setup Instructions

### Phase 1: Langfuse (LLM Observability)

**1. Install Langfuse locally (Docker):**

```bash
# Clone langfuse
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Start with docker-compose
docker-compose up -d
```

Access at: http://localhost:3000

**2. Get API keys:**
- Sign up at http://localhost:3000
- Create new project
- Copy Public Key and Secret Key

**3. Configure:**

Create `.claude/observability/langfuse/.env`:
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
ENABLE_LANGFUSE=true
```

**4. Copy client from nexus:**

```bash
cp ../claude-repos/quickstart-nexus-claude/hooks/utils/langfuse_client.py \
   .claude/observability/utils/
```

**5. Test:**

```bash
python .claude/observability/utils/test_langfuse.py
# Should see trace in Langfuse dashboard
```

### Phase 2: OpenTelemetry (Distributed Tracing)

**1. Install Python packages:**

```bash
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp
```

**2. Choose exporter:**

**Option A: Console (Development)**
```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
# Logs to stdout - good for debugging
```

**Option B: Jaeger (Production)**
```bash
# Run Jaeger locally
docker run -d \
  --name jaeger \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

Access at: http://localhost:16686

**3. Configure OTEL:**

Edit `.claude/observability/config/otel-config.yaml` (created earlier)

### Phase 3: Integrate with Existing Systems

**1. Update Graphiti initialization:**

```python
# In knowledge-sync scripts
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

graphiti = Graphiti(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
    tracer=tracer  # Enable OTEL tracing
)
```

**2. Install hooks:**

```bash
# Copy hooks to .claude/hooks/
cp observability/hooks/* .claude/hooks/
```

**3. Test end-to-end:**

```bash
claude  # Start session
/search test  # Trigger unified search with tracing
stop  # Generate session report
```

Check:
- Langfuse dashboard: http://localhost:3000
- OTEL traces: console or Jaeger
- Session report: `.claude/reports/sessions/[session-id].md`

---

## Cost Estimates

### Infrastructure

**Langfuse:**
- Self-hosted (Docker): Free
- Cloud (langfuse.com): $0-99/month

**OpenTelemetry:**
- Self-hosted: Free
- Jaeger: Free (open source)
- Commercial backends (Datadog, New Relic): $15-100/month

**Total Infrastructure:** $0-100/month

### API Costs (No Change)

Same as before:
- OpenAI for Graphiti: $10-300/month
- No additional cost for observability

**Total Monthly:** $10-400/month

---

## Roadmap

### Phase 1: Foundation (Week 1)
- [x] Langfuse client integration
- [x] OTEL basic setup
- [ ] SessionStart/SessionEnd hooks
- [ ] Basic metrics collection

### Phase 2: Full Tracing (Week 2)
- [ ] PreToolUse/PostToolUse hooks
- [ ] Unified search tracing
- [ ] Graphiti OTEL integration
- [ ] Cost tracking

### Phase 3: Analytics (Week 3)
- [ ] Session report generation
- [ ] Metrics aggregation
- [ ] Cost optimization insights
- [ ] Performance profiling

### Phase 4: Dashboards (Week 4)
- [ ] Real-time session dashboard
- [ ] Historical analytics
- [ ] Cost forecasting
- [ ] Pattern detection

---

## Success Metrics

**Observability Coverage:**
- [ ] 100% of LLM calls traced (Langfuse)
- [ ] 100% of tool uses traced (OTEL + Langfuse)
- [ ] 100% of knowledge searches traced
- [ ] Session reports generated automatically

**Performance:**
- [ ] Trace overhead < 50ms per operation
- [ ] Session report generation < 2s
- [ ] Real-time cost tracking
- [ ] Latency breakdown available

**Value Delivered:**
- [ ] Identify cost optimization opportunities (>20% savings)
- [ ] Reduce search latency (>30% improvement)
- [ ] Detect performance regressions automatically
- [ ] Track knowledge utilization patterns

---

**Ready to build the full observability stack!**

**Version:** 1.0
**Last Updated:** November 13, 2025
