# Complete Stack Architecture

> Visual guide to the three-system integration

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User                                     │
│                    (Claude Code CLI)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code Session                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Knowledge    │  │Observability │  │ Automation   │         │
│  │ Management   │  │ (Complete)   │  │ & Workflows  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Knowledge Layer │  │Observability Layer│  │Automation Layer  │
│                  │  │                  │  │                  │
│  ┌─────┐ ┌─────┐│  │   ┌─────────┐   │  │ ┌─────┐ ┌─────┐ │
│  │Obs- │ │Gra- ││  │   │Langfuse │   │  │ │Skill│ │Hook │ │
│  │idian│ │phiti││  │   │(LLM +   │   │  │ │s    │ │s    │ │
│  └─────┘ └─────┘│  │   │ Tracing)│   │  │ └─────┘ └─────┘ │
└──────────────────┘  │   └─────────┘   │  └──────────────────┘
        │             └──────────────────┘           │
        ▼                      ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Data Stores    │  │   Dashboards     │  │    Scripts       │
│                  │  │                  │  │                  │
│  • Vault (MD)    │  │  • Langfuse UI   │  │  • Python        │
│  • Neo4j (Graph) │  │  • Neo4j Browser │  │  • Node.js       │
│                  │  │                  │  │  • Bash          │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## Knowledge Management Flow

```
User Creates Note
        │
        ▼
┌───────────────────┐
│  Obsidian Vault   │
│  (Markdown File)  │
└───────────────────┘
        │
        │ (if tagged #adr, #decision, #learning)
        │
        ▼
┌───────────────────┐
│   Sync Trigger    │
│  (Hook or Manual) │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Entity Extractor │ ←── OpenAI API
│  (GPT-4o-mini)    │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Graphiti Core    │
│  (Knowledge Graph)│
└───────────────────┘
        │
        ▼
┌───────────────────┐
│     Neo4j         │
│  (Graph Storage)  │
└───────────────────┘
        │
        │ (weekly insights)
        │
        ▼
┌───────────────────┐
│  Generated Note   │ ──→ Back to Obsidian
│  (Graph Insights) │
└───────────────────┘
```

---

## Unified Search Flow

```
User Query: "authentication"
        │
        ▼
┌───────────────────┐
│  Unified Search   │
│    Coordinator    │
└───────────────────┘
        │
        ├─────────────────┬─────────────────┐
        ▼                 ▼                 │
┌──────────────┐  ┌──────────────┐        │
│   Obsidian   │  │   Graphiti   │        │
│   Search     │  │   Search     │        │
└──────────────┘  └──────────────┘        │
        │                 │                 │
        │                 ▼                 │
        │         ┌──────────────┐         │
        │         │   OpenAI     │         │
        │         │  (Embeddings)│         │
        │         └──────────────┘         │
        │                 │                 │
        ▼                 ▼                 │
┌──────────────┐  ┌──────────────┐        │
│  File-based  │  │  Graph Query │        │
│   Results    │  │   Results    │        │
└──────────────┘  └──────────────┘        │
        │                 │                 │
        └────────┬────────┘                 │
                 ▼                          │
        ┌──────────────┐                   │
        │ Merge & Rank │                   │
        │  (60/40 mix) │                   │
        └──────────────┘                   │
                 │                          │
                 ▼                          ▼
        ┌─────────────────────────────────────┐
        │      Unified Results Display        │
        │  📄 Obsidian (3) | 🔗 Graphiti (5) │
        └─────────────────────────────────────┘
```

---

## Observability Flow (Session)

```
Session Start
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Langfuse   │  │   Langfuse   │  │  Knowledge   │
│ (Root Trace) │  │  (Session)   │  │  Loading     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │ User Prompt  │
                  └──────────────┘
                           │
        ├──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Langfuse:    │  │ Langfuse:    │  │  Claude LLM  │
│ Start Span   │  │ Log Message  │  │  Generation  │
└──────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │  Tool Usage  │
                  └──────────────┘
                           │
        ├──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Langfuse:    │  │ Langfuse:    │  │  Execute     │
│ Tool Span    │  │ Log Tool Use │  │  Tool        │
└──────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │  Session End │
                  └──────────────┘
                           │
        ├──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Langfuse:    │  │ Langfuse:    │  │  Generate    │
│ Close Trace  │  │ Flush Events │  │  Report      │
└──────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │Session Report│
                  │  (Markdown)  │
                  └──────────────┘
```

---

## Data Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      File System                             │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Obsidian Vault/
        │    └─── Projects/consulting-co/
        │         ├─── Daily Notes/
        │         │    └─── 2025-11-13.md
        │         ├─── Decisions/
        │         │    └─── ADR-007-Lambda.md
        │         ├─── Learnings/
        │         │    ├─── Authentication.md
        │         │    └─── Graph Insights/
        │         │         └─── Weekly-2025-W46.md
        │         └─── Tasks/
        │              └─── SSL-Setup.md
        │
        └─── .claude/
             ├─── reports/sessions/
             │    └─── session-abc123.md
             ├─── metrics/
             │    └─── daily-2025-11-13.json
             └─── logs/
                  ├─── obsidian-operations.log
                  └─── knowledge-sync.log

┌─────────────────────────────────────────────────────────────┐
│                      Neo4j Database                          │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Episodes (Nodes)
        │    ├─── [Episode: "ADR-007-Lambda"]
        │    │    ├─── name: "ADR-007-Lambda"
        │    │    ├─── content: "..."
        │    │    ├─── created_at: 2025-11-13
        │    │    └─── source: "Obsidian"
        │    └─── ...
        │
        ├─── Entities (Nodes)
        │    ├─── [Entity: "AWS Lambda"]
        │    │    ├─── type: "Technology"
        │    │    ├─── name: "AWS Lambda"
        │    │    └─── connections: 12
        │    ├─── [Entity: "Serverless"]
        │    └─── ...
        │
        └─── Relationships (Edges)
             ├─── [Lambda]-[:IMPLEMENTS]->[Serverless]
             ├─── [ADR-007]-[:USES]->[Lambda]
             └─── ...

┌─────────────────────────────────────────────────────────────┐
│                   Langfuse Database                          │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Traces
        │    ├─── trace_session-abc123
        │    │    ├─── session_id: "session-abc123"
        │    │    ├─── start_time: ...
        │    │    ├─── spans: [...]
        │    │    └─── cost: $0.34
        │    └─── ...
        │
        ├─── Generations
        │    ├─── gen_123
        │    │    ├─── model: "claude-sonnet-4-5"
        │    │    ├─── input_tokens: 1234
        │    │    ├─── output_tokens: 567
        │    │    └─── latency: 2.3s
        │    └─── ...
        │
        └─── Sessions
             ├─── session-abc123
             └─── ...

```

---

## Hook Execution Flow

```
┌──────────────────────────────────────────────────────────┐
│                     Session Lifecycle                     │
└──────────────────────────────────────────────────────────┘

1. SessionStart Hook
   ├─── Create Langfuse session trace
   ├─── Load Obsidian daily note
   └─── Query Graphiti (last 7 days)

2. User Prompt Submitted
   ├─── (No hook)
   └─── Logged by Langfuse automatically

3. PreToolUse Hook
   ├─── Start Langfuse span
   ├─── Log tool parameters
   └─── Record timestamp

4. Tool Execution
   ├─── Execute tool
   └─── Capture output

5. PostToolUse Hook
   ├─── End Langfuse span
   ├─── Log result to Langfuse
   └─── Track duration

6. Stop Hook
   ├─── Quick session summary
   ├─── Update daily note
   └─── Log to Obsidian

7. SessionEnd Hook
   ├─── Extract learnings
   ├─── Sync to Graphiti
   ├─── Flush Langfuse
   ├─── Close all spans
   └─── Generate session report
```

---

## Cost & Performance Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Cost Tracking                           │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Langfuse
        │    ├─── Per-generation costs
        │    │    ├─── Input tokens × $0.000003
        │    │    └─── Output tokens × $0.000015
        │    └─── Session aggregation
        │
        ├─── Graphiti
        │    ├─── Entity extraction costs
        │    │    └─── OpenAI API calls
        │    └─── Embedding costs
        │         └─── text-embedding-3-small
        │
        └─── Reports
             └─── .claude/metrics/costs-YYYY-MM.json

┌─────────────────────────────────────────────────────────────┐
│                   Performance Tracking                       │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Langfuse Spans
        │    ├─── Latency per operation
        │    ├─── Service dependencies
        │    ├─── Error rates
        │    ├─── LLM latency
        │    ├─── Token throughput
        │    └─── Cache hit rates
        │
        └─── Custom Metrics
             ├─── Search performance
             ├─── Sync duration
             └─── Hook overhead
```

---

## Security & Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    Credential Storage                        │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── .env (Project Root)
        │    ├─── OPENAI_API_KEY
        │    ├─── NEO4J_PASSWORD
        │    └─── (Other credentials)
        │
        ├─── .claude/observability/langfuse/.env
        │    ├─── LANGFUSE_PUBLIC_KEY
        │    └─── LANGFUSE_SECRET_KEY
        │
        └─── .gitignore
             ├─── .env
             ├─── **/.env
             └─── .claude/observability/langfuse/.env

┌─────────────────────────────────────────────────────────────┐
│                      Data Isolation                          │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Obsidian
        │    ├─── .claudeignore patterns
        │    ├─── allowedFolders: [...]
        │    └─── deniedFolders: ["Private", ...]
        │
        ├─── Graphiti
        │    ├─── Separate Neo4j database
        │    └─── Project-specific namespace
        │
        └─── Langfuse
             ├─── Project-based isolation
             └─── Session-based filtering
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                         │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Docker Desktop
        │    ├─── neo4j-claude (7474, 7687)
        │    └─── langfuse (3000)
        │         ├─── web
        │         ├─── worker
        │         └─── postgres
        │
        ├─── Obsidian Desktop App
        │    └─── Local vault
        │
        └─── Claude Code CLI
             └─── Python/Node scripts

┌─────────────────────────────────────────────────────────────┐
│                  Production (Optional)                       │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Neo4j Aura (Cloud)
        │    └─── Managed Neo4j instance
        │
        └─── Langfuse Cloud
             └─── https://cloud.langfuse.com
```

---

## Communication Protocols

```
┌─────────────────────────────────────────────────────────────┐
│                   Protocol Overview                          │
└─────────────────────────────────────────────────────────────┘

Obsidian ←→ Scripts
    Protocol: File I/O
    Format: Markdown + YAML frontmatter
    Ops: Read, Write, List, Search

Scripts ←→ Neo4j
    Protocol: Bolt (binary)
    Port: 7687
    Format: Cypher queries
    Ops: MATCH, CREATE, MERGE

Scripts ←→ Graphiti
    Protocol: Python API
    Format: Graphiti objects
    Ops: add_episode, search, etc.

Scripts ←→ Langfuse
    Protocol: HTTP REST
    Port: 3000
    Format: JSON
    Ops: trace, span, generation, events

Claude Code ←→ Hooks
    Protocol: stdin/stdout
    Format: JSON
    Ops: Hook events + responses
```

---

## Failure Modes & Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                    Failure Handling                          │
└─────────────────────────────────────────────────────────────┘

Neo4j Down
    ├─── Graphiti operations fail gracefully
    ├─── Obsidian still works
    ├─── OTEL/Langfuse still log
    └─── Resume when Neo4j back up

Langfuse Down
    ├─── Observability degrades
    ├─── Knowledge management unaffected
    ├─── Session reports still generated
    └─── Logs accumulate locally

OpenAI API Error
    ├─── Entity extraction fails
    ├─── Sync halts for that note
    ├─── Manual retry available
    └─── Obsidian not affected

Disk Full
    ├─── New notes fail
    ├─── Logs rotate automatically
    ├─── Alert user
    └─── Cleanup old reports

Network Partition
    ├─── Local operations continue
    ├─── External APIs fail
    ├─── Queue for retry
    └─── Resume when network returns
```

---

## Scaling Considerations

```
Small Scale (1 user, 100 notes/month)
    ├─── All local Docker
    ├─── Single Neo4j instance
    └─── Langfuse local

Medium Scale (1-5 users, 1000 notes/month)
    ├─── Neo4j Aura (cloud)
    ├─── Langfuse cloud
    └─── Shared vault (git)

Large Scale (5+ users, 5000+ notes/month)
    ├─── Neo4j cluster
    ├─── Langfuse enterprise
    └─── Separate vaults per team
```

---

**This architecture supports all three integration paths:**
- Path 1: Obsidian layer only
- Path 2: Knowledge layer (Obsidian + Graphiti)
- Path 3: Complete stack (all three systems)

**Start simple, scale as needed!**

**Version:** 2.0 - Simplified
**Last Updated:** November 13, 2025
