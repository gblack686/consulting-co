# Complete Stack Quick Start

> Obsidian + Graphiti + Langfuse in 30 minutes

## What You're Building

A **comprehensive development intelligence platform** with:

```
📄 Obsidian → Human-curated knowledge (markdown notes)
🔗 Graphiti → Auto-extracted knowledge graph (Neo4j)
📊 Langfuse → Complete observability (LLM tracking + distributed tracing)
```

**Result:** Full visibility into your development workflow with persistent knowledge management.

---

## Prerequisites

- [ ] Windows 10/11 or Mac/Linux
- [ ] Python 3.9+
- [ ] Node.js 18+
- [ ] Docker Desktop (for Langfuse, Neo4j)
- [ ] OpenAI API key
- [ ] Obsidian installed
- [ ] Claude Code CLI working

---

## Step 1: Install Infrastructure (10 min)

### 1.1 Neo4j (for Graphiti)

**Option A: Docker (Recommended)**

```bash
docker run -d \
  --name neo4j-claude \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  -v neo4j_data:/data \
  neo4j:5-community
```

**Option B: Neo4j Desktop**

Download from https://neo4j.com/download/

### 1.2 Langfuse (for LLM Observability)

```bash
# Clone Langfuse
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Start with Docker Compose
docker-compose up -d
```

Access at: http://localhost:3000

**Get API Keys:**
1. Sign up at http://localhost:3000
2. Create new project: "Claude Code"
3. Copy **Public Key** and **Secret Key**

---

## Step 2: Configure Environment (10 min)

### 2.1 Create `.env` in Project Root

```bash
# .env (in consulting-co/)

# OpenAI (for Graphiti entity extraction)
OPENAI_API_KEY=sk-...

# Neo4j (for Graphiti)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password

# Langfuse (for complete observability)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=http://localhost:3000
ENABLE_LANGFUSE=true
```

### 2.2 Install Python Dependencies

```bash
# In project root
pip install \
  graphiti-core \
  neo4j \
  langfuse \
  python-dotenv
```

### 2.3 Install Node Dependencies

```bash
cd .claude/skills/obsidian-vault
npm install
```

---

## Step 3: Configure Obsidian (5 min)

### 3.1 Update Vault Path

Edit `.claude/skills/obsidian-vault/config/vault-settings.json`:

```json
{
  "vaultPath": "C:/Users/YOUR_USER/Documents/Obsidian/YourVault",
  "projectFolder": "Projects/consulting-co"
}
```

### 3.2 Initialize Vault Structure

```bash
node .claude/skills/obsidian-vault/scripts/init-vault.js
```

Expected output:
```
✓ Created: Projects/consulting-co/Daily Notes/
✓ Created: Projects/consulting-co/Decisions/
✓ Created: Projects/consulting-co/Learnings/
✓ Vault initialization complete!
```

---

## Step 4: Configure Graphiti (5 min)

### 4.1 Copy Existing Implementation

You already have Graphiti! Let's reuse it:

```bash
# Copy from board-director project
cp -r ../aws/RevStar/quickstarts/quickstart-board-director/logging-service/graphiti-repo \
      ./graphiti

cd graphiti
pip install -e .
```

### 4.2 Initialize Schema

```bash
# Create init script
cat > init_graphiti.py << 'EOF'
import asyncio
import os
from graphiti_core import Graphiti

async def main():
    graphiti = Graphiti(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    await graphiti.build_indices_and_constraints()
    print("✓ Graphiti schema initialized")
    await graphiti.close()

asyncio.run(main())
EOF

python init_graphiti.py
```

---

## Step 5: Configure Langfuse Integration (5 min)

### 5.1 Create Observability Directory

```bash
mkdir -p .claude/observability/utils
mkdir -p .claude/observability/config
mkdir -p .claude/observability/langfuse
```

### 5.2 Copy Langfuse Client from Nexus

```bash
# Copy existing implementation
cp ../claude-repos/quickstart-nexus-claude/hooks/utils/langfuse_client.py \
   .claude/observability/utils/

cp ../claude-repos/quickstart-nexus-claude/langfuse/.env \
   .claude/observability/langfuse/.env
```

### 5.3 Update Langfuse .env

Edit `.claude/observability/langfuse/.env`:

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...  # From Step 1.2
LANGFUSE_SECRET_KEY=sk-lf-...  # From Step 1.2
LANGFUSE_BASE_URL=http://localhost:3000
ENABLE_LANGFUSE=true
```

### 5.4 Test Langfuse

```bash
cat > test_langfuse.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.claude/observability/utils')))

from langfuse_client import get_langfuse_client

client = get_langfuse_client()
print(f"Langfuse enabled: {client.enabled}")

if client.enabled:
    trace = client.trace_event(
        name="test_trace",
        input_data={"test": "data"},
        session_id="test",
        tags=["test"]
    )
    client.flush()
    print("✓ Test trace sent! Check Langfuse dashboard")
else:
    print("✗ Langfuse not enabled")
EOF

python test_langfuse.py
```

Check: http://localhost:3000 - You should see a test trace!

---

## Step 6: Test Each Layer (5 min)

Start Claude Code:

```bash
claude
```

### Test 1: Obsidian

```bash
/note-create "Test Note" learning
```

Expected: Note created in Obsidian vault

### Test 2: Obsidian Search

```bash
/note-search test
```

Expected: Finds the test note

### Test 3: Graphiti Sync

```bash
/sync-to-graph "Test Note"
```

Expected:
```
✓ Syncing: Test Note.md → Graphiti
✓ Entities extracted: 2
✓ Episode ID: ep-test-123
```

Verify in Neo4j Browser (http://localhost:7474):
```cypher
MATCH (e:Episode) RETURN e LIMIT 5;
```

### Test 4: Unified Search

```bash
/search test
```

Expected: Results from both Obsidian AND Graphiti

### Test 5: Langfuse Tracing

Run any command, then check Langfuse dashboard (http://localhost:3000)

You should see traces appearing!

---

## System Verification Checklist

- [ ] **Neo4j**: Running at http://localhost:7474
- [ ] **Langfuse**: Running at http://localhost:3000
- [ ] **Obsidian**: Vault initialized with project folders
- [ ] **Graphiti**: Schema initialized in Neo4j
- [ ] **Langfuse Client**: Test trace visible in dashboard
- [ ] **All Commands**: `/note-create`, `/note-search`, `/search`, `/sync-to-graph` working

---

## Daily Workflow

### Morning (Session Start)

```bash
claude
```

**What happens automatically:**
1. ✅ Creates today's daily note (Obsidian)
2. ✅ Loads last 7 days context (Graphiti)
3. ✅ Initializes Langfuse session (complete observability)

**You see:**
```
📊 Session Observability Initialized

Session ID: session-abc123
  - Langfuse: http://localhost:3000/project/1/traces/session-abc123
  - Tracing: Enabled (LLM + distributed tracing)

📚 Knowledge Context Loaded
  - Obsidian: Daily Note 2025-11-13
  - Graphiti: 12 episodes from last 7 days
  - Pending Tasks: 3
```

### During Work

**Search for past solutions:**

```bash
/search "how did we handle authentication"
```

**Behind the scenes:**
- 📄 Searches Obsidian vault (full-text)
- 🔗 Queries Graphiti graph (semantic + relationships)
- 📊 Langfuse traces both searches + logs cost

**Make architectural decision:**

```bash
/decision-log "Use Auth0 for SSO"
```

**Behind the scenes:**
- 📝 Creates ADR in Obsidian
- 🔗 Syncs to Graphiti (entities: Auth0, SSO, OAuth)
- 📊 Langfuse tracks end-to-end + extraction cost

### End of Day

```bash
stop
```

**What happens automatically:**
1. ✅ Logs session to daily note
2. ✅ Extracts learnings → Graphiti + Obsidian
3. ✅ Flushes Langfuse traces
4. ✅ Generates session report

**You see:**
```
=============================================================
Session Report: session-abc123
=============================================================
Duration: 3,245s (54 min)
Prompts: 23
Tools Used: 47
Tokens: 45,234 ($0.34)
Knowledge Searches: 8
Notes Created: 2
Graph Episodes: 5

📊 Full report: .claude/reports/sessions/session-abc123.md
📈 Langfuse: http://localhost:3000/project/1/traces/session-abc123
🔍 Performance: Available in Langfuse trace view
=============================================================
```

---

## Dashboards Overview

### Langfuse Dashboard (http://localhost:3000)

**What you can see:**
- All LLM generations with prompts/responses
- Token usage per generation
- Cost breakdown by session
- Latency distribution and timing
- Error rates and tracking
- Most expensive prompts
- Distributed traces (end-to-end request flow)
- Nested span visualization (tool calls, searches, etc.)
- Performance bottlenecks

**Use cases:**
- "Why was yesterday's session so expensive?"
- "Which prompts use the most tokens?"
- "How much did Graphiti extractions cost this week?"
- "Why is unified search slow?"
- "What's taking so long in Graphiti?"
- "Where are the errors coming from?"

### Neo4j Browser (http://localhost:7474)

**What you can see:**
- Full knowledge graph visualization
- Entities and relationships
- Temporal queries
- Graph patterns

**Use cases:**
- "Show me all decisions related to authentication"
- "What concepts are most connected?"
- "How has our architecture evolved?"

### Obsidian (Your Vault)

**What you can see:**
- All notes in markdown
- Daily journals
- ADRs and decisions
- Learnings and tasks
- Graph view (Obsidian's built-in)

**Use cases:**
- Manual editing and curation
- Reading formatted documentation
- Visual graph exploration
- Linking related concepts

---

## Troubleshooting

### Issue: Neo4j connection failed

**Check:**
```bash
docker ps | grep neo4j
# Should show neo4j-claude running
```

**Fix:**
```bash
docker start neo4j-claude
# Or restart
docker restart neo4j-claude
```

### Issue: Langfuse not recording traces

**Check:**
```bash
docker ps | grep langfuse
# Should show langfuse containers running

echo $ENABLE_LANGFUSE
# Should output: true
```

**Fix:**
```bash
cd langfuse
docker-compose restart

# Check .claude/observability/langfuse/.env
cat .claude/observability/langfuse/.env
```

### Issue: Obsidian vault not found

**Fix:**
1. Check path in `vault-settings.json`
2. Use absolute path with forward slashes
3. Create vault in Obsidian first

### Issue: Import errors

**Fix:**
```bash
# Install all dependencies
pip install -r requirements.txt

# requirements.txt
cat > requirements.txt << 'EOF'
graphiti-core>=0.3.0
neo4j>=5.0.0
langfuse>=2.0.0
python-dotenv>=1.0.0
asyncio
EOF

pip install -r requirements.txt
```

---

## Cost Breakdown

### Infrastructure (Monthly)

| Service | Hosting | Cost |
|---------|---------|------|
| Neo4j | Local Docker | **Free** |
| Langfuse | Local Docker | **Free** |
| Obsidian | Desktop App | **Free** |
| **Total Infrastructure** | | **$0** |

### API Costs (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| OpenAI (Graphiti) | 100 notes/week | **$10-20** |
| OpenAI (Graphiti) | 500 notes/week | **$50-100** |
| OpenAI (Graphiti) | 1000+ notes/week | **$150-300** |

**No additional cost for observability!** Langfuse doesn't call external APIs.

**Recommended Budget:** $10-20/month (light Graphiti usage)

---

## Performance Benchmarks

**Operations:**
- Unified search: 2-3s
- Sync to Graphiti: 3-5s
- Daily note creation: < 0.5s
- Session report: 1-2s

**Overhead:**
- Langfuse tracing: ~10-20ms per operation
- Total overhead: < 30ms per operation

**Storage:**
- Obsidian: ~1MB per 100 notes
- Neo4j: ~10MB per 1000 episodes
- Langfuse: ~50MB per 1000 traces

---

## Next Steps

### Week 1: Basic Usage
- [ ] Create daily notes automatically
- [ ] Log decisions as ADRs
- [ ] Use unified search regularly
- [ ] Review Langfuse dashboard weekly

### Week 2: Automation
- [ ] Set up SessionStart/SessionEnd hooks
- [ ] Enable automatic syncing
- [ ] Configure cost alerts
- [ ] Optimize search performance

### Week 3: Advanced Features
- [ ] Weekly knowledge synthesis
- [ ] Cost optimization analysis
- [ ] Performance profiling
- [ ] Custom entity types

### Week 4: Refinement
- [ ] Tune search weights
- [ ] Customize templates
- [ ] Add custom metrics
- [ ] Team knowledge sharing

---

## Quick Reference

### Commands

```bash
# Knowledge Management
/note-create [title] [category]  # Create Obsidian note
/note-search [query]              # Search Obsidian only
/search [query]                   # Unified search (Obs + Graphiti)
/sync-to-graph [note]             # Sync note to Graphiti
/decision-log [title]             # Create ADR
/daily-note                       # Open today's note
/graph-insights                   # Generate insights from graph

# Observability
# (Automatic via hooks - no commands needed)
```

### Dashboards

```bash
# Langfuse (Complete Observability)
http://localhost:3000

# Neo4j (Knowledge Graph)
http://localhost:7474

# Obsidian (Notes)
# Open in Obsidian app
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
ENABLE_LANGFUSE=true
```

---

## Resources

**Documentation:**
- Simplified Architecture: `.claude/SIMPLIFIED_OBSERVABILITY.md`
- Obsidian + Graphiti: `.claude/OBSIDIAN_GRAPHITI_INTEGRATION.md`
- Obsidian Only: `.claude/OBSIDIAN_INTEGRATION_PLAN.md`

**External:**
- Langfuse: https://langfuse.com/docs
- Graphiti: https://github.com/getzep/graphiti
- Neo4j: https://neo4j.com/docs/

**Your Projects:**
- Board Director: `../aws/RevStar/quickstarts/quickstart-board-director/`
- Nexus (Langfuse): `../claude-repos/quickstart-nexus-claude/`

---

**You now have a complete development intelligence platform!**

**Start with:** `claude` → Creates daily note + initializes observability

**Version:** 2.0 - Simplified
**Last Updated:** November 13, 2025
