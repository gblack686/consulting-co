#!/usr/bin/env python3
"""
AI-Agent-KB Unified Search Interface

Combines two search approaches:
1. Graphiti knowledge graph - for conceptual queries, relationships, mental models
2. Supabase vector index - for finding specific components (commands, skills, etc.)

Usage:
    # Interactive search
    python kb_search.py "how to create a git commit"

    # Programmatic usage
    from kb_search import search_kb
    results = search_kb("how to create a git commit")

    # Search specific tier
    python kb_search.py --vector-only "commit command"
    python kb_search.py --graphiti-only "TAC methodology relationships"

    # Filter by type
    python kb_search.py --type command "git"
    python kb_search.py --folder skills "diagram"
"""

import os
import sys
import json
import argparse
import asyncio
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

# Third-party imports
try:
    from openai import OpenAI
    from supabase import create_client, Client
    import boto3
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install openai supabase boto3")
    sys.exit(1)

# Optional Graphiti import
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
GRAPHITI_URL = os.getenv("GRAPHITI_URL", "bolt://localhost:7687")


@dataclass
class SearchResult:
    """Unified search result from any source."""
    source: str  # "vector" or "graphiti"
    id: str
    name: str
    type: str
    summary: str
    file_path: Optional[str] = None
    similarity: Optional[float] = None
    relationships: Optional[list] = None


def get_supabase_credentials() -> tuple[str, str]:
    """Get Supabase credentials from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(
            SecretId="gbautomation/infrastructure/supabase"
        )
        secret = json.loads(response["SecretString"])
        return secret["url"], secret["service_key"]
    except Exception:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        return url, key


def get_openai_client() -> OpenAI:
    """Initialize OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(
                SecretId="gbautomation/infrastructure/openai"
            )
            secret = json.loads(response["SecretString"])
            api_key = secret.get("api_key") or secret.get("OPENAI_API_KEY")
        except Exception:
            pass

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set")

    return OpenAI(api_key=api_key)


def generate_embedding(openai_client: OpenAI, text: str) -> list[float]:
    """Generate embedding for a single query."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


def search_vector_index(
    supabase: Client,
    openai_client: OpenAI,
    query: str,
    top_k: int = 10,
    threshold: float = 0.5,
    folder_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
) -> list[SearchResult]:
    """Search Supabase vector index for matching KB entries."""
    # Generate query embedding
    query_embedding = generate_embedding(openai_client, query)
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Build SQL query directly (avoids PostgREST schema cache issues)
    sql = f"""
    SELECT
        id,
        file_path,
        folder,
        type,
        name,
        summary,
        tags,
        1 - (embedding <=> '{embedding_str}'::vector(1536)) AS similarity
    FROM kb_index
    WHERE 1 - (embedding <=> '{embedding_str}'::vector(1536)) > {threshold}
    """

    if folder_filter:
        sql += f" AND folder = '{folder_filter}'"
    if type_filter:
        sql += f" AND type = '{type_filter}'"

    sql += f" ORDER BY embedding <=> '{embedding_str}'::vector(1536) LIMIT {top_k}"

    # Use Management API to execute SQL
    import boto3
    import httpx

    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId="gbautomation/infrastructure/supabase")
    secret = json.loads(response["SecretString"])
    token = secret.get("access_token")

    url = "https://api.supabase.com/v1/projects/unickqnwfheaczccvgbw/database/query"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = httpx.post(url, headers=headers, json={"query": sql}, timeout=30.0)
    rows = resp.json() if resp.status_code == 201 else []

    results = []
    for row in rows:
        results.append(SearchResult(
            source="vector",
            id=row["id"],
            name=row["name"],
            type=row["type"],
            summary=row["summary"],
            file_path=row["file_path"],
            similarity=row["similarity"],
        ))

    return results


async def search_graphiti(
    query: str,
    top_k: int = 10,
) -> list[SearchResult]:
    """Search Graphiti knowledge graph for concepts and relationships."""
    if not GRAPHITI_AVAILABLE:
        return []

    try:
        graphiti = Graphiti(GRAPHITI_URL)
        await graphiti.build_indices()

        # Search for relevant facts/relationships
        search_results = await graphiti.search(query, num_results=top_k)

        results = []
        for fact in search_results:
            # Extract relationship info if available
            relationships = []
            if hasattr(fact, 'triplets'):
                for triplet in fact.triplets:
                    relationships.append({
                        "source": triplet.source.name if triplet.source else None,
                        "relation": triplet.relation.name if triplet.relation else None,
                        "target": triplet.target.name if triplet.target else None,
                    })

            results.append(SearchResult(
                source="graphiti",
                id=str(fact.uuid) if hasattr(fact, 'uuid') else str(hash(fact.fact)),
                name=fact.fact[:100] if hasattr(fact, 'fact') else str(fact)[:100],
                type="concept",
                summary=fact.fact if hasattr(fact, 'fact') else str(fact),
                relationships=relationships if relationships else None,
            ))

        await graphiti.close()
        return results

    except Exception as e:
        print(f"{YELLOW}Graphiti search unavailable: {e}{RESET}")
        return []


def search_kb(
    query: str,
    top_k: int = 10,
    vector_only: bool = False,
    graphiti_only: bool = False,
    folder_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    threshold: float = 0.5,
) -> list[SearchResult]:
    """
    Unified KB search combining vector index and knowledge graph.

    Args:
        query: Natural language search query
        top_k: Maximum results per source
        vector_only: Only search vector index
        graphiti_only: Only search Graphiti
        folder_filter: Filter vector results by folder
        type_filter: Filter vector results by type
        threshold: Minimum similarity threshold for vector search

    Returns:
        Combined list of SearchResult objects, ranked by relevance
    """
    results = []

    # Initialize clients
    if not graphiti_only:
        supabase_url, supabase_key = get_supabase_credentials()
        supabase = create_client(supabase_url, supabase_key)
        openai_client = get_openai_client()

        vector_results = search_vector_index(
            supabase,
            openai_client,
            query,
            top_k=top_k,
            threshold=threshold,
            folder_filter=folder_filter,
            type_filter=type_filter,
        )
        results.extend(vector_results)

    # Search Graphiti
    if not vector_only and GRAPHITI_AVAILABLE:
        graphiti_results = asyncio.run(search_graphiti(query, top_k=top_k))
        results.extend(graphiti_results)

    # Sort by similarity (vector results have scores, graphiti results don't)
    def sort_key(r):
        if r.similarity is not None:
            return -r.similarity
        return 0  # Graphiti results have no score, show after vector

    results.sort(key=sort_key)

    return results


def format_results(results: list[SearchResult], verbose: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return f"{YELLOW}No results found{RESET}"

    lines = []
    for i, r in enumerate(results, 1):
        # Source indicator
        if r.source == "vector":
            source_badge = f"{BLUE}[VEC]{RESET}"
            score_str = f"{DIM}({r.similarity:.2f}){RESET}" if r.similarity else ""
        else:
            source_badge = f"{CYAN}[KG]{RESET}"
            score_str = ""

        # Type badge
        type_colors = {
            "command": GREEN,
            "skill": YELLOW,
            "agent": BLUE,
            "hook": CYAN,
            "expert": RED,
            "concept": CYAN,
        }
        type_color = type_colors.get(r.type, RESET)
        type_badge = f"{type_color}[{r.type}]{RESET}"

        # Result line
        lines.append(
            f"{i}. {source_badge} {type_badge} {BOLD}{r.name}{RESET} {score_str}"
        )

        if verbose:
            lines.append(f"   {DIM}ID: {r.id}{RESET}")
            if r.file_path:
                lines.append(f"   {DIM}Path: {r.file_path}{RESET}")

        # Summary (truncated)
        summary = r.summary[:200] + "..." if len(r.summary) > 200 else r.summary
        lines.append(f"   {summary}")

        # Relationships (for Graphiti results)
        if r.relationships and verbose:
            lines.append(f"   {DIM}Relationships:{RESET}")
            for rel in r.relationships[:3]:
                lines.append(
                    f"     {rel['source']} -> {rel['relation']} -> {rel['target']}"
                )

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search AI-Agent-KB using vector index and knowledge graph"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Search query"
    )
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=10,
        help="Maximum results per source (default: 10)"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.5,
        help="Minimum similarity threshold (default: 0.5)"
    )
    parser.add_argument(
        "--vector-only",
        action="store_true",
        help="Only search vector index (fast, specific components)"
    )
    parser.add_argument(
        "--graphiti-only",
        action="store_true",
        help="Only search Graphiti knowledge graph (concepts, relationships)"
    )
    parser.add_argument(
        "--folder", "-f",
        type=str,
        help="Filter by folder (commands, agents, skills, hooks)"
    )
    parser.add_argument(
        "--type",
        type=str,
        help="Filter by type (command, agent, skill, hook, expert)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    args = parser.parse_args()

    # Interactive mode if no query provided
    if not args.query:
        print(f"{BOLD}AI-Agent-KB Search{RESET}")
        print(f"Vector index: {GREEN}enabled{RESET}")
        print(f"Graphiti: {GREEN if GRAPHITI_AVAILABLE else RED}{'enabled' if GRAPHITI_AVAILABLE else 'not available'}{RESET}")
        print()
        args.query = input("Enter search query: ").strip()
        if not args.query:
            print("No query provided")
            return

    # Perform search
    results = search_kb(
        query=args.query,
        top_k=args.top_k,
        vector_only=args.vector_only,
        graphiti_only=args.graphiti_only,
        folder_filter=args.folder,
        type_filter=args.type,
        threshold=args.threshold,
    )

    # Output results
    if args.json:
        output = [
            {
                "source": r.source,
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "summary": r.summary,
                "file_path": r.file_path,
                "similarity": r.similarity,
                "relationships": r.relationships,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        print()
        print(f"{BOLD}Results for: {RESET}{args.query}")
        print()
        print(format_results(results, verbose=args.verbose))


if __name__ == "__main__":
    main()
