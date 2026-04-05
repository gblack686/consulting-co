# Claude Code Configuration

> Intelligent development environment with knowledge management

## Overview

This `.claude/` directory contains a **complete development intelligence platform** with three integrated systems:

### Knowledge Management
- **Obsidian Integration**: File-based markdown knowledge vault
- **Graphiti Integration**: Temporal knowledge graph with Neo4j
- **Dual-Layer Knowledge**: Unified search across both systems

### Complete Observability
- **Langfuse**: Complete observability (LLM tracking, distributed tracing, cost tracking, token usage, prompt analytics, performance profiling, error tracking)

### Automation
- **Skills & Commands**: Reusable workflows and shortcuts
- **Hooks**: Automatic session management and logging
- **Agents**: Specialized AI assistants for different tasks

## Quick Links

### Getting Started (Choose Your Path)

**Path 1: Obsidian Only** (Simple, 10 min)
- [OBSIDIAN_QUICK_START.md](OBSIDIAN_QUICK_START.md)
- Cost: $0/month
- Best for: Basic knowledge management

**Path 2: Obsidian + Graphiti** (Advanced, 30 min)
- [OBSIDIAN_GRAPHITI_QUICK_START.md](OBSIDIAN_GRAPHITI_QUICK_START.md)
- Cost: $10-50/month
- Best for: Automatic pattern discovery

**Path 3: Complete Stack** (Full Platform, 30 min) ⭐ **RECOMMENDED**
- [COMPLETE_STACK_QUICK_START.md](COMPLETE_STACK_QUICK_START.md)
- Cost: $10-50/month
- Best for: Full observability + knowledge management

### Full Documentation
- **Simplified Observability**: [SIMPLIFIED_OBSERVABILITY.md](SIMPLIFIED_OBSERVABILITY.md) ⭐ **NEW**
- **Obsidian + Graphiti**: [OBSIDIAN_GRAPHITI_INTEGRATION.md](OBSIDIAN_GRAPHITI_INTEGRATION.md)
- **Obsidian Only**: [OBSIDIAN_INTEGRATION_PLAN.md](OBSIDIAN_INTEGRATION_PLAN.md)

## What's Available

### 📁 Skills

#### obsidian-vault
Comprehensive Obsidian vault management.

**Capabilities:**
- Create, read, search notes
- Template-based note generation
- Daily notes automation
- Architecture Decision Records (ADRs)
- Learning notes and task tracking

**Docs:** [skills/obsidian-vault/README.md](skills/obsidian-vault/README.md)

#### knowledge-sync
Unified knowledge management across Obsidian and Graphiti.

**Capabilities:**
- Bidirectional sync (Obsidian ↔ Graphiti)
- Unified search across both systems
- Automatic entity extraction
- Knowledge graph insights

**Docs:** [skills/knowledge-sync/SKILL.md](skills/knowledge-sync/SKILL.md)

#### revstar-quickstart-workflow
RevStar QuickStart project methodology.

**Capabilities:**
- Project scoping and planning
- AWS architecture design
- Multi-agent workflows
- Deployment automation

**Docs:** [skills/revstar-quickstart-workflow/README.md](skills/revstar-quickstart-workflow/README.md)

### ⌨️ Commands

| Command | Description | Skill |
|---------|-------------|-------|
| `/note-create [title] [category]` | Create Obsidian note | obsidian-vault |
| `/note-search [query]` | Search Obsidian vault | obsidian-vault |
| `/decision-log [title]` | Create ADR | obsidian-vault |
| `/daily-note` | Open today's note | obsidian-vault |
| `/search [query]` | Unified search (Obs + Graphiti) | knowledge-sync |
| `/sync-to-graph [note]` | Sync note to Graphiti | knowledge-sync |
| `/graph-insights` | Generate insights from graph | knowledge-sync |

### 🪝 Hooks

Hooks automatically run at specific points in your workflow.

#### Available Hooks
- **SessionStart**: Load daily note + graph context
- **Stop**: Log session to notes + graph
- **SessionEnd**: Extract learnings, bidirectional sync
- **PreToolUse**: Capture decisions before major changes

**Status:** Configured but not enabled by default. See setup guides.

## Integration Paths

### Path 1: Obsidian Only (Simple)

**Time to setup:** 10 minutes
**Monthly cost:** $0
**Systems:** Obsidian

**Best for:**
- Getting started with knowledge management
- Simple note-taking and organization
- Manual documentation
- Small teams

**Setup:** Follow [OBSIDIAN_QUICK_START.md](OBSIDIAN_QUICK_START.md)

### Path 2: Obsidian + Graphiti (Advanced)

**Time to setup:** 30 minutes
**Monthly cost:** $10-50 (OpenAI API)
**Systems:** Obsidian + Graphiti

**Best for:**
- Automatic knowledge extraction
- Pattern discovery across sessions
- Semantic search and relationships
- Large knowledge bases

**Setup:** Follow [OBSIDIAN_GRAPHITI_QUICK_START.md](OBSIDIAN_GRAPHITI_QUICK_START.md)

### Path 3: Complete Stack (Full Platform) ⭐ **RECOMMENDED**

**Time to setup:** 30 minutes
**Monthly cost:** $10-50 (OpenAI API)
**Systems:** Obsidian + Graphiti + Langfuse

**Best for:**
- Full development intelligence platform
- Cost tracking and optimization
- Performance profiling
- Complete session visibility
- Production-grade workflows

**What you get:**
- 📄 All knowledge management features
- 📊 Complete observability (LLM tracking + distributed tracing)
- 📈 Session analytics and reports
- 🎯 Performance insights
- 💰 Cost optimization

**Setup:** Follow [COMPLETE_STACK_QUICK_START.md](COMPLETE_STACK_QUICK_START.md)

## Architecture

### Obsidian Layer (File-Based)
```
Obsidian Vault/
├── Projects/
│   └── consulting-co/
│       ├── Daily Notes/        # Automated daily journals
│       ├── Decisions/          # ADRs and architecture decisions
│       ├── Learnings/          # Knowledge notes
│       ├── Tasks/              # Task tracking
│       └── Meetings/           # Meeting notes
```

### Graphiti Layer (Graph-Based)
```
Neo4j Knowledge Graph
├── Episodes (Nodes)            # Session events and decisions
├── Entities (Nodes)            # Extracted concepts (Tech, Decisions)
├── Relationships (Edges)       # Connections between entities
└── Temporal Index              # Time-based queries
```

### Unified Search
```
User Query
    ↓
┌─────────────────────┐
│  Unified Search     │
└─────────────────────┘
    ↓           ↓
📄 Obsidian  🔗 Graphiti
(Full-text)  (Semantic + Graph)
    ↓           ↓
┌─────────────────────┐
│  Merged Results     │
│  (Weighted Ranking) │
└─────────────────────┘
```

## Configuration Files

### Essential
- `.claude/skills/obsidian-vault/config/vault-settings.json` - Vault path and settings
- `.claude/skills/knowledge-sync/config/sync-settings.json` - Sync configuration
- `.env` - Credentials (NEO4J_*, OPENAI_API_KEY)

### Optional
- `.claude/hooks/session-start/*.sh` - Session startup automation
- `.claude/hooks/session-end/*.py` - Session cleanup and logging

## Daily Workflow Example

```bash
# Morning - Start session
claude
# ✓ Today's daily note created
# ✓ Last 7 days context loaded from graph
# ✓ Pending tasks displayed

# Work - Search past solutions
/search "authentication implementation"
# 📄 3 notes from Obsidian
# 🔗 5 entities + 8 relationships from Graphiti

# Work - Make decision
/decision-log "Use Auth0 for SSO"
# ✓ ADR created in Obsidian
# ✓ Synced to Graphiti with entity extraction

# End of day
stop
# ✓ Session logged to daily note
# ✓ Learnings extracted and synced
# ✓ Knowledge graph updated
```

## Use Cases

### Use Case 1: Architectural Decision Making
Search past decisions → Load context → Make new decision → Auto-document

**Commands:**
```bash
/search "database choices"
/decision-log "PostgreSQL for User Data"
```

### Use Case 2: Weekly Knowledge Synthesis
Generate insights from graph → Review patterns → Document learnings

**Commands:**
```bash
/graph-insights
# Review generated note in Obsidian
# Edit and expand insights
# Auto-syncs back to graph
```

### Use Case 3: Context Recovery
Search both layers → Load complete historical context → Continue work

**Commands:**
```bash
/search "feature X implementation"
/load-context 1,2,3
# Full context from 3 months ago restored
```

## Performance

**Search Latency:**
- Obsidian only: < 1s
- Graphiti only: 1-2s
- Unified search: 2-3s

**Sync Latency:**
- Note → Graphiti: 3-5s
- Graph → Obsidian: 10-15s (weekly batch)

**Storage:**
- Obsidian: ~1MB per 100 notes
- Neo4j: ~10MB per 1000 episodes

## Cost Breakdown

### Infrastructure
- **Neo4j Local**: Free
- **Neo4j Aura**: $0-65/month
- **Obsidian**: Free (Sync is $8/month optional)

### API Costs
- **OpenAI (gpt-4o-mini)**:
  - Light: $10-20/month (100 notes/week)
  - Medium: $50-100/month (500 notes/week)
  - Heavy: $150-300/month (1000+ notes/week)

**Recommended Starting Budget:** $10-20/month (local Neo4j + light usage)

## Troubleshooting

### Common Issues

**Neo4j Connection Failed**
```bash
# Check Neo4j is running
neo4j status
neo4j start

# Verify credentials
cat .env | grep NEO4J
```

**Obsidian Vault Not Found**
- Check `vaultPath` in `vault-settings.json`
- Use absolute paths with forward slashes
- Verify folder exists

**Sync Not Working**
```bash
# Check logs
tail -f .claude/logs/knowledge-sync.log

# Test components
/sync-to-graph "Test" --verbose
```

**Search Returns No Results**
- Verify both Neo4j and Obsidian are accessible
- Rebuild index: `/vault-sync --rebuild`
- Check search weights in config

## Next Steps

### For New Users
1. Start with [OBSIDIAN_QUICK_START.md](OBSIDIAN_QUICK_START.md)
2. Use basic commands for 1 week
3. Evaluate if you need Graphiti layer
4. Upgrade to dual-layer if desired

### For Advanced Users
1. Go directly to [OBSIDIAN_GRAPHITI_QUICK_START.md](OBSIDIAN_GRAPHITI_QUICK_START.md)
2. Set up both layers immediately
3. Configure hooks for automation
4. Customize sync settings

## Development

### Adding Custom Commands
Create `.claude/commands/your-command.md`:
```markdown
# /your-command

Description of command...

## Usage
...
```

### Adding Custom Skills
Create `.claude/skills/your-skill/SKILL.md`:
```markdown
# Your Skill

Description...

## Capabilities
...
```

### Customizing Sync
Edit `.claude/skills/knowledge-sync/config/sync-settings.json`:
- Adjust sync triggers
- Change search weights
- Add custom entity types
- Configure insights frequency

## Resources

### Internal Docs
- [VIBE Planning Framework](../specs/core-guides/VIBE-PLANNING-FRAMEWORK.md)
- [Obsidian Vault Skill](skills/obsidian-vault/README.md)
- [Knowledge Sync Skill](skills/knowledge-sync/SKILL.md)

### External Resources
- [Claude Code Docs](https://docs.claude.com/claude-code)
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Obsidian Documentation](https://obsidian.md/)

### Your Existing Projects
You have working Graphiti implementations in:
- `../aws/RevStar/quickstarts/quickstart-board-director/`
- `../aws/RevStar/quickstarts/quickstart-compcorrect/`
- `../aws/RevStar/quickstarts/quickstart-nexus/`

Can copy patterns from these!

## Support

**Getting Help:**
1. Check relevant quick-start guide
2. Review integration plan
3. Check logs in `.claude/logs/`
4. Test components individually

**Common Commands for Debugging:**
```bash
# Test Obsidian
/note-create "Debug Test"

# Test Graphiti
python -c "from graphiti_core import Graphiti; print('OK')"

# Test unified search
/search test --verbose

# View logs
tail -f .claude/logs/*.log
```

## Version

**Version:** 2.0 - Simplified (3 systems)
**Last Updated:** November 13, 2025
**Claude Code Version:** 1.0+

---

**Ready to get started? Pick your path:**
- Simple: [OBSIDIAN_QUICK_START.md](OBSIDIAN_QUICK_START.md)
- Advanced: [OBSIDIAN_GRAPHITI_QUICK_START.md](OBSIDIAN_GRAPHITI_QUICK_START.md)
- Complete: [COMPLETE_STACK_QUICK_START.md](COMPLETE_STACK_QUICK_START.md) ⭐
