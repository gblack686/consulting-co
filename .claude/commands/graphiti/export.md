---
description: Export knowledge graph data to Obsidian vault as individual note files
---

Export entities and episodes from Neo4j to individual Obsidian markdown files.

This command will:

1. **Export Entities** to `~/obsidian-vault/entities/`:
   - One markdown file per entity
   - Format: `[entity-name].md`
   - Include: summary, labels, creation date, connections
   - Add backlinks to related entities

2. **Export Episodes** to `~/obsidian-vault/episodes/`:
   - One markdown file per episode
   - Format: `[episode-name].md`
   - Include: content, timestamp, source, extracted entities
   - Add links to entity notes

3. **Create Index Files**:
   - `~/obsidian-vault/entities/README.md` - Entity index
   - `~/obsidian-vault/episodes/README.md` - Episode index
   - Both sorted by connection count or date

4. **Generate Graph View**:
   - Create a graph overview showing connections
   - Use Obsidian's graph view format with proper linking

Ask for confirmation before proceeding:
"This will create [X] entity files and [Y] episode files in your Obsidian vault. Continue? (yes/no)"

After export, show:
- Number of files created
- Location of files
- Suggested Obsidian vault settings for optimal viewing
