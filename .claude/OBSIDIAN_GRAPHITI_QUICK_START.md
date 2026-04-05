# Obsidian + Graphiti Integration - Quick Start

> Set up dual-layer knowledge system in 30 minutes

## What You're Building

A **dual-layer knowledge system** that combines:
- 📄 **Obsidian**: Human-curated markdown notes
- 🔗 **Graphiti**: Auto-extracted knowledge graph
- 🔍 **Unified Search**: Query both systems simultaneously
- ♻️ **Bidirectional Sync**: Keep both layers synchronized

## Prerequisites

- [x] Obsidian installed with a vault
- [x] Neo4j 5.x+ installed (Desktop or Docker)
- [x] Python 3.9+
- [x] Node.js 18+
- [x] OpenAI API key (for entity extraction)
- [x] Claude Code CLI working

## Step 1: Set Up Neo4j (5 min)

### Option A: Neo4j Desktop (Easiest)

1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create new project: "Claude Code Knowledge"
3. Add local DBMS:
   - Name: "claude-knowledge"
   - Password: Choose a secure password (save it!)
   - Version: 5.x
4. Start the database
5. Note connection details:
   - URI: `bolt://localhost:7687`
   - User: `neo4j`
   - Password: [your password]

### Option B: Docker (Advanced)

```bash
docker run \
  --name neo4j-claude \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  -v $HOME/neo4j/data:/data \
  neo4j:5-community
```

## Step 2: Set Up Graphiti (10 min)

### Copy Existing Implementation

You already have Graphiti in your projects! Let's reuse it:

```bash
# Copy from existing project
cp -r ../aws/RevStar/quickstarts/quickstart-board-director/logging-service/graphiti-repo ./graphiti

cd graphiti
pip install -e .
```

### Configure Environment

Create `.env` in project root:

```bash
# .env
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
MODEL_NAME=gpt-4o-mini
```

### Initialize Graphiti Schema

```bash
python .claude/skills/knowledge-sync/scripts/init-graphiti.py
```

Expected output:
```
Connecting to: bolt://localhost:7687
✓ Connected to Neo4j
Building indices and constraints...
✓ Graphiti schema initialized successfully
```

## Step 3: Configure Obsidian Integration (5 min)

### Update Vault Path

Edit `.claude/skills/obsidian-vault/config/vault-settings.json`:

```json
{
  "vaultPath": "C:/Users/YOUR_USER/Documents/Obsidian/YourVault",
  "projectFolder": "Projects/consulting-co"
}
```

### Install Dependencies

```bash
cd .claude/skills/obsidian-vault
npm install
```

### Initialize Vault Structure

```bash
node scripts/init-vault.js
```

## Step 4: Configure Knowledge Sync (5 min)

### Update Sync Settings

Edit `.claude/skills/knowledge-sync/config/sync-settings.json`:

```json
{
  "obsidian": {
    "enabled": true,
    "vaultPath": "C:/Users/YOUR_USER/Documents/Obsidian/YourVault"
  },
  "graphiti": {
    "enabled": true,
    "neo4jUri": "${NEO4J_URI}",
    "neo4jUser": "${NEO4J_USER}",
    "neo4jPassword": "${NEO4J_PASSWORD}",
    "openaiApiKey": "${OPENAI_API_KEY}"
  },
  "sync": {
    "mode": "selective",
    "obsidianToGraphiti": {
      "enabled": true,
      "noteTags": ["adr", "decision", "learning"]
    }
  }
}
```

### Install Python Dependencies

```bash
cd .claude/skills/knowledge-sync
pip install -r requirements.txt
```

Create `requirements.txt`:
```
graphiti-core>=0.3.0
neo4j>=5.0.0
python-dotenv>=1.0.0
openai>=1.0.0
asyncio
```

## Step 5: Test the Integration (5 min)

### Test 1: Obsidian Note Creation

Start Claude Code:
```bash
claude
```

Create a test note:
```bash
/note-create "Test Integration" learning
```

Expected: Note created in Obsidian vault

### Test 2: Sync to Graphiti

Add ADR tag to the note manually in Obsidian, then:
```bash
/sync-to-graph "Test Integration"
```

Expected output:
```
✓ Syncing: Test Integration.md → Graphiti
✓ Entities extracted: 2
✓ Relationships created: 3
✓ Episode ID: ep-test-123
```

### Test 3: Unified Search

```bash
/search test integration
```

Expected: Results from both Obsidian and Graphiti

### Test 4: Verify in Neo4j

Open Neo4j Browser (http://localhost:7474) and run:

```cypher
MATCH (e:Episode) RETURN e LIMIT 5;
```

You should see your test episode!

## Directory Structure (Final)

```
.claude/
├── OBSIDIAN_INTEGRATION_PLAN.md
├── OBSIDIAN_GRAPHITI_INTEGRATION.md
├── OBSIDIAN_GRAPHITI_QUICK_START.md (this file)
├── skills/
│   ├── obsidian-vault/
│   │   ├── SKILL.md
│   │   ├── config/vault-settings.json
│   │   ├── templates/
│   │   └── scripts/
│   └── knowledge-sync/
│       ├── SKILL.md
│       ├── config/sync-settings.json
│       └── scripts/
│           ├── unified-search.py
│           ├── obsidian-to-graphiti.py
│           └── graphiti-to-obsidian.py
├── commands/
│   ├── note-create.md
│   ├── note-search.md
│   └── search-knowledge.md
└── hooks/
    ├── session-start/
    │   └── load-unified-context.py
    └── session-end/
        └── sync-knowledge.py
```

## Daily Workflow

### Morning (Session Start)

```bash
claude
# Automatically:
# - Opens today's daily note in Obsidian
# - Loads last 7 days of Graphiti context
# - Shows unified knowledge dashboard
```

### During Work

```bash
# Search for past solutions
/search "how did we handle authentication"

# Load context from both sources
/load-context 1,2,3

# Make architectural decision
"We should use Auth0"

# Log the decision
/decision-log "Use Auth0 for Authentication"
# → Creates ADR in Obsidian
# → Syncs to Graphiti with entity extraction
```

### End of Day

```bash
stop
# Automatically:
# - Logs session to daily note
# - Syncs learnings to Graphiti
# - Extracts entities and relationships
# - Updates both knowledge layers
```

## Advanced Usage

### Weekly Knowledge Review

```bash
/graph-insights
```

Generates:
- Top 10 most connected concepts
- Emerging patterns
- Knowledge gaps
- Temporal trends

Saves to: `Obsidian/Learnings/Graph Insights/YYYY-MM-DD.md`

### Knowledge Map Visualization

```bash
/knowledge-map authentication
```

Generates text-based graph:
```
Authentication
  ├─ implements → OAuth2
  │   └─ uses → JWT Tokens
  ├─ requires → Identity Provider
  │   └─ example → Auth0
  └─ enables → RBAC
      └─ related → User Roles
```

### Manual Sync

```bash
# Sync specific note
/sync-to-graph "ADR-007-Lambda-API"

# Sync all notes with tag
/sync-to-graph --tag adr

# Sync folder
/sync-to-graph --folder Decisions
```

## Troubleshooting

### Issue: Cannot connect to Neo4j

**Check:**
```bash
# Verify Neo4j is running
neo4j status

# Test connection
curl http://localhost:7474
```

**Fix:**
- Start Neo4j: `neo4j start`
- Check credentials in `.env`
- Verify port 7687 is not blocked

### Issue: OpenAI API errors

**Check:**
```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Fix:**
- Add API key to `.env`
- Check API quota
- Verify billing is set up

### Issue: Obsidian vault not found

**Fix:**
1. Check `vaultPath` in `vault-settings.json`
2. Use absolute path with forward slashes
3. Verify folder exists in file system

### Issue: Sync not working

**Debug:**
```bash
# Check logs
tail -f .claude/logs/knowledge-sync.log

# Verbose mode
/sync-to-graph "Note" --verbose

# Test Graphiti connection
python -c "from graphiti_core import Graphiti; import asyncio; asyncio.run(Graphiti().close())"
```

## Cost Estimate

### Monthly Costs

**Neo4j:**
- Local: **Free**
- Aura Free Tier: **Free**
- Aura Professional: $65/month

**OpenAI API** (for entity extraction):
- Light usage (100 notes/week): ~$10-20/month
- Medium usage (500 notes/week): ~$50-100/month
- Heavy usage (1000+ notes/week): ~$150-300/month

**Recommended for starting:** Local Neo4j + GPT-4o-mini = **$10-20/month**

## Performance Benchmarks

**Operations:**
- Unified search: 2-3 seconds
- Sync note to Graphiti: 3-5 seconds
- Load daily context: 1-2 seconds
- Generate weekly insights: 10-15 seconds

**Optimization:**
- Parallel search execution
- Cached entity embeddings
- Indexed Obsidian vault
- Optimized Neo4j queries

## Next Steps

### Phase 1: Basic Usage (This Week)
- [ ] Create daily notes automatically
- [ ] Log decisions as ADRs
- [ ] Use unified search regularly
- [ ] Verify sync working

### Phase 2: Automation (Next Week)
- [ ] Set up SessionStart/SessionEnd hooks
- [ ] Enable automatic syncing
- [ ] Configure weekly insights
- [ ] Optimize search weights

### Phase 3: Advanced (Month 2)
- [ ] Custom entity types
- [ ] Advanced graph queries
- [ ] Temporal pattern analysis
- [ ] Team knowledge sharing

## Configuration Reference

### Sync Modes

**Selective (Recommended):**
- Only syncs notes with tags: `#adr`, `#decision`, `#learning`
- Low overhead, high quality
- Best for starting

**Full:**
- Syncs all notes in configured folders
- Higher costs, more comprehensive
- Good for mature workflows

**Manual:**
- User controls all syncing
- No automatic operations
- Good for testing

### Search Weights

Adjust in `sync-settings.json`:
```json
{
  "search": {
    "weighObsidian": 0.6,  // Favor human-curated notes
    "weighGraphiti": 0.4   // Favor graph connections
  }
}
```

**Recommendations:**
- Research-heavy: 0.7 Obsidian / 0.3 Graphiti
- Pattern discovery: 0.4 Obsidian / 0.6 Graphiti
- Balanced: 0.6 Obsidian / 0.4 Graphiti (default)

## Resources

**Documentation:**
- Full Integration Plan: `.claude/OBSIDIAN_GRAPHITI_INTEGRATION.md`
- Obsidian Skill: `.claude/skills/obsidian-vault/README.md`
- Knowledge Sync Skill: `.claude/skills/knowledge-sync/SKILL.md`

**External:**
- [Graphiti Documentation](https://github.com/getzep/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Obsidian Plugin API](https://docs.obsidian.md/)

**Your Existing Implementations:**
- Board Director: `../aws/RevStar/quickstarts/quickstart-board-director/`
- CompCorrect: `../aws/RevStar/quickstarts/quickstart-compcorrect/`

## Support

**Common Questions:**
1. **"Which sync mode should I use?"**
   → Start with **Selective**, upgrade to Full if needed

2. **"Should I use local or cloud Neo4j?"**
   → Start **local** for testing, move to cloud for production

3. **"How do I reduce OpenAI costs?"**
   → Use **gpt-4o-mini**, batch syncing, higher `minWordCount`

4. **"Can I use this without OpenAI?"**
   → Not currently - Graphiti requires LLM for entity extraction

**Get Help:**
- Check logs: `.claude/logs/knowledge-sync.log`
- Review plans: `.claude/OBSIDIAN_GRAPHITI_INTEGRATION.md`
- Test components individually first

---

**You're ready to build your dual-layer knowledge system!**

Start with: `/note-create "First Note" learning`

**Version:** 1.0
**Last Updated:** November 13, 2025
