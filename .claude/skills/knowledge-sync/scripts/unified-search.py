#!/usr/bin/env python3
"""
Unified search across Obsidian vault and Graphiti knowledge graph.
Merges and ranks results from both sources.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Add parent directories to path
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SKILL_DIR))
sys.path.insert(0, str(SKILL_DIR.parent.parent))  # For obsidian-vault skill


class UnifiedSearch:
    """Search across both Obsidian and Graphiti."""

    def __init__(self, config: Dict):
        self.config = config
        self.obsidian_weight = config["search"]["weighObsidian"]
        self.graphiti_weight = config["search"]["weighGraphiti"]
        self.max_results = config["search"]["maxResults"]

    async def search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Perform unified search.

        Args:
            query: Search query string
            filters: Optional filters (source, date, type)

        Returns:
            List of merged and ranked results
        """
        filters = filters or {}

        # Determine which sources to search
        search_obsidian = filters.get("source") != "graphiti"
        search_graphiti = filters.get("source") != "obsidian"

        # Execute searches in parallel
        tasks = []
        if search_obsidian:
            tasks.append(self._search_obsidian(query, filters))
        if search_graphiti:
            tasks.append(self._search_graphiti(query, filters))

        results = await asyncio.gather(*tasks)

        # Merge results
        obsidian_results = results[0] if search_obsidian else []
        graphiti_results = results[1] if (
            search_graphiti and len(results) > 1
        ) else (results[0] if search_graphiti else [])

        merged = self._merge_results(obsidian_results, graphiti_results, query)

        return merged[:self.max_results]

    async def _search_obsidian(
        self,
        query: str,
        filters: Dict
    ) -> List[Dict]:
        """Search Obsidian vault."""
        from obsidian_vault.scripts.search_engine import ObsidianSearch

        vault_path = self.config["obsidian"]["vaultPath"]
        searcher = ObsidianSearch(vault_path)

        # Apply filters
        note_type = filters.get("type")
        after_date = filters.get("after")
        before_date = filters.get("before")

        results = searcher.search(
            query=query,
            note_type=note_type,
            after=after_date,
            before=before_date
        )

        return [
            {
                "source": "obsidian",
                "type": "note",
                "title": r["title"],
                "snippet": r["snippet"],
                "score": r["score"],
                "path": r["path"],
                "tags": r.get("tags", []),
                "date": r.get("date"),
                "metadata": r.get("metadata", {})
            }
            for r in results
        ]

    async def _search_graphiti(
        self,
        query: str,
        filters: Dict
    ) -> List[Dict]:
        """Search Graphiti knowledge graph."""
        from graphiti_core import Graphiti

        # Initialize Graphiti
        graphiti = Graphiti(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD")
        )

        results = []

        try:
            # Search entities
            if filters.get("type") != "episodes":
                entities = await graphiti.search_nodes(
                    query=query,
                    limit=5
                )

                for entity in entities:
                    results.append({
                        "source": "graphiti",
                        "type": "entity",
                        "title": entity.name,
                        "entity_type": getattr(entity, "type", "Unknown"),
                        "connections": getattr(entity, "degree", 0),
                        "score": getattr(entity, "similarity_score", 0.5),
                        "last_updated": getattr(
                            entity, "updated_at", datetime.now()
                        ),
                        "metadata": {
                            "uuid": getattr(entity, "uuid", ""),
                        }
                    })

            # Search episodes
            if filters.get("type") != "entities":
                episodes = await graphiti.search_episodes(
                    query=query,
                    limit=5
                )

                for episode in episodes:
                    results.append({
                        "source": "graphiti",
                        "type": "episode",
                        "title": episode.name,
                        "snippet": episode.content[:200] + "...",
                        "score": getattr(episode, "similarity_score", 0.5),
                        "date": episode.created_at,
                        "metadata": {
                            "source": getattr(
                                episode, "source_description", ""
                            ),
                            "uuid": getattr(episode, "uuid", "")
                        }
                    })

            # Search relationships (facts)
            if self.config["search"]["enableGraphTraversal"]:
                facts = await graphiti.search_facts(
                    query=query,
                    limit=3
                )

                for fact in facts:
                    results.append({
                        "source": "graphiti",
                        "type": "relationship",
                        "title": f"{fact.source} → {fact.target}",
                        "relation_type": fact.relation_type,
                        "score": getattr(fact, "similarity_score", 0.5),
                        "metadata": {
                            "fact": fact.fact,
                            "created_at": fact.created_at
                        }
                    })

        finally:
            await graphiti.close()

        return results

    def _merge_results(
        self,
        obsidian: List[Dict],
        graphiti: List[Dict],
        query: str
    ) -> List[Dict]:
        """
        Merge and rank results from both sources.

        Args:
            obsidian: Results from Obsidian
            graphiti: Results from Graphiti
            query: Original search query

        Returns:
            Merged and sorted results
        """
        # Apply weights
        for r in obsidian:
            r["final_score"] = r["score"] * self.obsidian_weight
            r["display_score"] = r["score"]

        for r in graphiti:
            r["final_score"] = r["score"] * self.graphiti_weight
            r["display_score"] = r["score"]

        # Merge
        all_results = obsidian + graphiti

        # Sort by final score
        all_results.sort(key=lambda x: x["final_score"], reverse=True)

        # Apply merge strategy
        strategy = self.config["search"]["mergeStrategy"]

        if strategy == "interleaved":
            return self._interleave_sources(all_results)
        else:
            return all_results

    def _interleave_sources(self, results: List[Dict]) -> List[Dict]:
        """
        Interleave results from different sources.

        Args:
            results: Sorted results

        Returns:
            Interleaved results
        """
        obsidian = [r for r in results if r["source"] == "obsidian"]
        graphiti = [r for r in results if r["source"] == "graphiti"]

        interleaved = []
        max_len = max(len(obsidian), len(graphiti))

        for i in range(max_len):
            if i < len(obsidian):
                interleaved.append(obsidian[i])
            if i < len(graphiti):
                interleaved.append(graphiti[i])

        return interleaved

    def format_results(self, results: List[Dict]) -> str:
        """
        Format results for display.

        Args:
            results: Search results

        Returns:
            Formatted string
        """
        if not results:
            return "No results found."

        output = []
        output.append(f"Found {len(results)} results:\n")

        obsidian_count = len([r for r in results if r["source"] == "obsidian"])
        graphiti_count = len([r for r in results if r["source"] == "graphiti"])

        output.append(
            f"📄 Obsidian: {obsidian_count} | "
            f"🔗 Graphiti: {graphiti_count}\n"
        )

        for i, result in enumerate(results, 1):
            source_icon = "📄" if result["source"] == "obsidian" else "🔗"
            output.append(f"\n{i}. {source_icon} {result['title']}")
            output.append(f"   Score: {result['display_score']:.2f}")

            if result["type"] == "note":
                output.append(f"   Tags: {', '.join(result.get('tags', []))}")
                if result.get("date"):
                    output.append(f"   Date: {result['date']}")

            elif result["type"] == "entity":
                output.append(f"   Type: {result['entity_type']}")
                output.append(f"   Connections: {result['connections']}")

            elif result["type"] == "episode":
                output.append(f"   Date: {result['date']}")
                if result["metadata"].get("source"):
                    output.append(f"   Source: {result['metadata']['source']}")

            elif result["type"] == "relationship":
                output.append(f"   Type: {result['relation_type']}")

            if result.get("snippet"):
                snippet = result["snippet"][:150]
                output.append(f"   \"{snippet}...\"")

        output.append("\n")
        output.append("Actions:")
        output.append("  /load-context 1,2,3  - Load results into conversation")
        output.append("  /graph-map [topic]   - Visualize connections")

        return "\n".join(output)


async def main():
    """Main entry point for unified search."""
    # Load configuration
    config_path = SKILL_DIR / "config" / "sync-settings.json"
    with open(config_path) as f:
        config = json.load(f)

    # Get query from command line
    if len(sys.argv) < 2:
        print("Usage: unified-search.py <query> [--obsidian-only] [--graphiti-only]")
        sys.exit(1)

    query = " ".join(arg for arg in sys.argv[1:] if not arg.startswith("--"))

    # Parse filters
    filters = {}
    if "--obsidian-only" in sys.argv:
        filters["source"] = "obsidian"
    elif "--graphiti-only" in sys.argv:
        filters["source"] = "graphiti"

    if "--entities-only" in sys.argv:
        filters["type"] = "entities"
    elif "--episodes-only" in sys.argv:
        filters["type"] = "episodes"

    # Execute search
    searcher = UnifiedSearch(config)
    results = await searcher.search(query, filters)

    # Format and display
    formatted = searcher.format_results(results)
    print(formatted)

    # Return results as JSON for programmatic access
    if "--json" in sys.argv:
        print("\n---JSON---")
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
