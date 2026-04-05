---
description: Search the Neo4j knowledge graph for entities, episodes, or concepts
---

Search the Neo4j/Graphiti knowledge graph for the term or concept the user specifies.

If no search term is provided, ask: "What would you like to search for in your knowledge graph?"

Once you have the search term, query Neo4j to find:

1. **Matching Entities**: Any entities with names or summaries containing the search term
2. **Related Episodes**: Episodes that mention the search term
3. **Connections**: What other concepts are connected to this term
4. **Timeline**: When this concept first appeared and how it evolved
5. **Context**: Full summaries and descriptions

Display results in a structured format:
- Entity matches with summaries
- Episode matches with timestamps
- Related concepts (network neighbors)
- Suggested Obsidian links to create

Example: `/obsidian-search langfuse` or `/obsidian-search authentication`
