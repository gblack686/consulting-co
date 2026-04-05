# Obsidian Integration Commands

These slash commands integrate your Claude Code activity with Obsidian through Neo4j/Graphiti knowledge graph.

## 📊 Summary Generation

### `/obsidian-daily`
Generate today's daily activity summary.

**What it does:**
- Runs the daily summary generator
- Creates markdown report in Obsidian vault
- Shows conversation count, entities extracted, and top concepts

**Output:** `~/obsidian-vault/daily-notes/[today]-claude-activity.md`

**Example:**
```
/obsidian-daily
```

---

### `/obsidian-summary [DATE]`
Generate a daily summary for a specific date.

**What it does:**
- Generates summary for any past date
- Same format as daily summary
- Useful for backfilling or reviewing past activity

**Format:** `YYYY-MM-DD`

**Example:**
```
/obsidian-summary 2025-11-13
```

---

### `/obsidian-weekly`
Generate a weekly summary for the past 7 days.

**What it does:**
- Aggregates 7 days of activity
- Shows trends and patterns
- Identifies most active days and top concepts
- Compares week-over-week if data exists

**Output:** `~/obsidian-vault/weekly-notes/[week-of-DATE]-claude-activity.md`

**Example:**
```
/obsidian-weekly
```

---

## 🔍 Knowledge Graph Exploration

### `/obsidian-search [TERM]`
Search the knowledge graph for entities and episodes.

**What it does:**
- Searches entity names and summaries
- Finds related episodes
- Shows connections and relationships
- Displays timeline of concept evolution

**Example:**
```
/obsidian-search langfuse
/obsidian-search authentication
```

---

### `/obsidian-graph [CONCEPT]`
Visualize connections for a specific concept.

**What it does:**
- Creates Mermaid diagram of connections
- Shows direct and indirect relationships
- Ranks by connection strength
- Identifies clusters and patterns

**Example:**
```
/obsidian-graph graphiti
/obsidian-graph api-design
```

---

## 📈 Statistics & Analytics

### `/obsidian-stats`
Show comprehensive knowledge graph statistics.

**What it does:**
- Total episodes and entities
- Knowledge density metrics
- Top concepts by connection count
- Project breakdown
- Recent activity (24h, 7d)
- Growth trends

**Example:**
```
/obsidian-stats
```

---

### `/obsidian-episodes`
List recent episodes from the knowledge graph.

**What it does:**
- Shows 10 most recent episodes
- Includes timestamps and project names
- Total episode count
- Identifies activity patterns

**Example:**
```
/obsidian-episodes
```

---

## 🔧 Utilities

### `/obsidian-schema`
Inspect Neo4j database schema.

**What it does:**
- Shows Entity node properties
- Shows Episodic node properties
- Explains property usage
- Suggests useful queries

**Example:**
```
/obsidian-schema
```

---

### `/obsidian-view [DATE]`
View an existing Obsidian summary.

**What it does:**
- Reads and displays an existing summary
- Defaults to today if no date provided
- Offers to generate if file doesn't exist

**Example:**
```
/obsidian-view
/obsidian-view 2025-11-13
```

---

### `/obsidian-export`
Export knowledge graph to Obsidian vault files.

**What it does:**
- Creates individual markdown files for each entity
- Creates individual markdown files for each episode
- Generates index files
- Adds proper Obsidian links and backlinks

**Output:**
- `~/obsidian-vault/entities/*.md`
- `~/obsidian-vault/episodes/*.md`
- Index files with navigation

**Example:**
```
/obsidian-export
```

---

## 🎯 Quick Reference

| Command | Purpose | Output Location |
|---------|---------|-----------------|
| `/obsidian-daily` | Today's summary | `daily-notes/[today].md` |
| `/obsidian-summary` | Specific date summary | `daily-notes/[date].md` |
| `/obsidian-weekly` | 7-day summary | `weekly-notes/[week].md` |
| `/obsidian-search` | Find concepts | Console output |
| `/obsidian-graph` | Visualize connections | Mermaid diagram |
| `/obsidian-stats` | Overall statistics | Console output |
| `/obsidian-episodes` | List recent activity | Console output |
| `/obsidian-schema` | Database structure | Console output |
| `/obsidian-view` | Read summary | Console output |
| `/obsidian-export` | Bulk export | `entities/`, `episodes/` |

---

## 🚀 Common Workflows

### Daily Review
```
/obsidian-daily
/obsidian-view
```

### Weekly Planning
```
/obsidian-weekly
/obsidian-stats
```

### Research a Topic
```
/obsidian-search [topic]
/obsidian-graph [topic]
```

### Knowledge Base Setup
```
/obsidian-export
```
Then open your Obsidian vault to explore the graph view!

---

## 📁 File Structure

```
~/obsidian-vault/
├── daily-notes/
│   └── YYYY-MM-DD-claude-activity.md
├── weekly-notes/
│   └── week-of-YYYY-MM-DD-claude-activity.md
├── entities/
│   ├── README.md
│   └── [entity-name].md
└── episodes/
    ├── README.md
    └── [episode-name].md
```

---

## 🔗 Related Documentation

- **Scripts:** `.claude/scripts/generate_daily_summary.py`
- **Usage Guide:** `.claude/OBSIDIAN_DAILY_SUMMARY.md`
- **Vision:** `.claude/NEXT_LEVEL_VISION.md`
- **Hooks:** `.claude/hooks/log_to_graphiti.py`

---

## 💡 Tips

1. **Run daily summaries automatically** - Set up a cron job or Task Scheduler
2. **Use search before creating** - Check if a concept exists before starting new work
3. **Review stats weekly** - Track your knowledge growth over time
4. **Export periodically** - Keep your Obsidian vault in sync with the knowledge graph
5. **Explore the graph** - Use `/obsidian-graph` to discover unexpected connections

---

**Created:** 2025-11-14
**Commands:** 10 slash commands for Obsidian integration
**Purpose:** Bridge Claude Code, Neo4j/Graphiti, and Obsidian for your AI second brain
