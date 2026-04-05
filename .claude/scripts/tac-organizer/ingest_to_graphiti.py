#!/usr/bin/env python3
"""
AI-Agent-KB Graphiti Ingestion Script (Tier 1)

Ingests high-value conceptual content into Graphiti knowledge graph:
- Experts (expertise.yaml, expertise.md) - domain mental models
- ADWs (plan_build_improve.md) - workflow sequences
- Index/Taxonomy files - KB structure

Estimated: ~100 files, ~1.5 hours (with LLM entity extraction)

Usage:
    # Start Graphiti server first
    python .claude/skills/graphiti/scripts/graphiti_server.py start

    # Run ingestion
    cd .claude/scripts
    python ingest_to_graphiti.py

    # Options:
    python ingest_to_graphiti.py --dry-run           # Preview without ingesting
    python ingest_to_graphiti.py --category experts  # Only ingest experts
    python ingest_to_graphiti.py --force             # Re-ingest all files
"""

import os
import sys
import json
import re
import asyncio
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Third-party imports
try:
    import yaml
    import httpx
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install pyyaml httpx")
    sys.exit(1)

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Configuration
KB_ROOT = Path(__file__).parent.parent  # .claude directory
GRAPHITI_MCP_URL = "http://localhost:8000/mcp/"
GRAPHITI_HEALTH_URL = "http://localhost:8000/health"
GROUP_ID = "ai-agent-kb"

# Tier 1 categories - high-value conceptual content
TIER1_CATEGORIES = {
    "experts": {
        "description": "Domain expertise and mental models",
        "patterns": [
            "commands/experts/**/expertise.yaml",
            "commands/experts/**/expertise.md",
        ],
        "skip_patterns": ["*template*", "*test*"],
    },
    "adws": {
        "description": "AI Developer Workflow sequences",
        "patterns": [
            "commands/experts/**/plan_build_improve.md",
        ],
        "skip_patterns": ["*template*"],
    },
    "index_files": {
        "description": "KB structure and taxonomy",
        "patterns": [
            "commands/experts/**/_index.md",
            "skills/**/SKILL.md",
        ],
        "skip_patterns": ["*template*"],
    },
}


def check_graphiti_health() -> bool:
    """Check if Graphiti MCP server is running."""
    try:
        response = httpx.get(GRAPHITI_HEALTH_URL, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError:
                pass

    return frontmatter, body


def extract_summary(file_path: Path, content: str, frontmatter: dict) -> str:
    """Extract a summary description of the file."""
    # For YAML files, try to get overview.description
    if file_path.suffix == ".yaml":
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                if "overview" in data and "description" in data["overview"]:
                    return data["overview"]["description"]
                if "description" in data:
                    return data["description"]
        except yaml.YAMLError:
            pass

    # For MD files, check frontmatter first
    if frontmatter.get("description"):
        return frontmatter["description"]

    # Look for purpose section
    purpose_match = re.search(
        r"##?\s*(?:Purpose|Overview|Description)\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.IGNORECASE | re.DOTALL
    )
    if purpose_match:
        return purpose_match.group(1).strip()[:500]

    # Fallback: first paragraph
    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            lines.append(line)
        if len(" ".join(lines)) > 300:
            break
    return " ".join(lines)[:500]


def get_category_from_path(file_path: Path) -> str:
    """Determine category from file path."""
    rel_path = str(file_path.relative_to(KB_ROOT))

    if "expertise.yaml" in rel_path or "expertise.md" in rel_path:
        return "expert"
    if "plan_build_improve.md" in rel_path:
        return "adw"
    if "_index.md" in rel_path:
        return "index"
    if "SKILL.md" in rel_path:
        return "skill"

    return "other"


def get_expert_domain(file_path: Path) -> str:
    """Extract expert domain from path like commands/experts/backend/expertise.yaml."""
    parts = file_path.parts
    try:
        experts_idx = parts.index("experts")
        if experts_idx + 1 < len(parts):
            return parts[experts_idx + 1]
    except ValueError:
        pass
    return "unknown"


def collect_tier1_files() -> list[Path]:
    """Collect all Tier 1 files for ingestion."""
    files = []
    collected_paths = set()

    for category, config in TIER1_CATEGORIES.items():
        for pattern in config["patterns"]:
            for file_path in KB_ROOT.glob(pattern):
                if not file_path.is_file():
                    continue

                # Check skip patterns
                rel_path = str(file_path.relative_to(KB_ROOT)).lower()
                skip = False
                for skip_pattern in config.get("skip_patterns", []):
                    if skip_pattern.replace("*", "") in rel_path:
                        skip = True
                        break

                if skip:
                    continue

                # Avoid duplicates
                if str(file_path) in collected_paths:
                    continue

                collected_paths.add(str(file_path))
                files.append(file_path)

    return sorted(files)


def build_episode_body(file_path: Path, content: str, frontmatter: dict) -> dict:
    """Build episode body for Graphiti ingestion."""
    category = get_category_from_path(file_path)
    rel_path = str(file_path.relative_to(KB_ROOT)).replace("\\", "/")
    summary = extract_summary(file_path, content, frontmatter)

    # Build structured content
    episode_body = {
        "file_path": rel_path,
        "category": category,
        "summary": summary,
        "tags": frontmatter.get("tags", []),
        "content_type": file_path.suffix[1:],  # yaml or md
    }

    # Add domain for experts
    if category in ["expert", "adw"]:
        episode_body["domain"] = get_expert_domain(file_path)

    # Include full content for entity extraction
    # Limit size for very large files
    episode_body["content"] = content[:15000]

    return episode_body


async def ingest_file(
    client: httpx.AsyncClient,
    file_path: Path,
    dry_run: bool = False
) -> dict:
    """Ingest a single file into Graphiti."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {"success": False, "error": f"Could not read file: {e}"}

    frontmatter, body = parse_frontmatter(content)
    episode_body = build_episode_body(file_path, content, frontmatter)

    # Create episode name
    category = episode_body["category"]
    domain = episode_body.get("domain", "")
    name_parts = [category.upper()]
    if domain:
        name_parts.append(domain)
    name_parts.append(file_path.stem)
    episode_name = " - ".join(name_parts)

    if dry_run:
        return {
            "success": True,
            "name": episode_name,
            "category": category,
            "summary_preview": episode_body["summary"][:100],
        }

    # Build MCP request
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "add_memory",
            "arguments": {
                "name": episode_name,
                "episode_body": json.dumps(episode_body),
                "source": "json",
                "source_description": f"AI-Agent-KB {category} file",
                "group_id": GROUP_ID
            }
        }
    }

    try:
        response = await client.post(
            GRAPHITI_MCP_URL,
            json=payload,
            timeout=120.0  # Entity extraction can take time
        )
        result = response.json()

        if "error" in result:
            return {"success": False, "error": result["error"]}

        return {"success": True, "name": episode_name, "result": result.get("result")}

    except httpx.TimeoutException:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def ingest_all(
    files: list[Path],
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """Ingest all files sequentially (parallel would overload the LLM)."""
    results = {"success": 0, "failed": 0, "errors": []}

    async with httpx.AsyncClient() as client:
        total = len(files)
        for i, file_path in enumerate(files, 1):
            rel_path = str(file_path.relative_to(KB_ROOT))

            if verbose:
                print(f"[{i}/{total}] Processing: {rel_path}")

            result = await ingest_file(client, file_path, dry_run)

            if result.get("success"):
                results["success"] += 1
                if not verbose:
                    print(f"{GREEN}✓{RESET} [{i}/{total}] {result.get('name', rel_path)}")
                else:
                    print(f"  {GREEN}✓{RESET} {result.get('name')}")
                    if "summary_preview" in result:
                        print(f"    Summary: {result['summary_preview']}...")
            else:
                results["failed"] += 1
                results["errors"].append({
                    "file": rel_path,
                    "error": result.get("error")
                })
                print(f"{RED}✗{RESET} [{i}/{total}] {rel_path}: {result.get('error')}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Ingest AI-Agent-KB Tier 1 files into Graphiti knowledge graph"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files without ingesting"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=list(TIER1_CATEGORIES.keys()),
        help="Only ingest a specific category"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest all files (skip hash check)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    args = parser.parse_args()

    print(f"{BOLD}AI-Agent-KB Graphiti Ingestion (Tier 1){RESET}")
    print(f"KB Root: {KB_ROOT}")
    print()

    # Check Graphiti health
    if not args.dry_run:
        print("Checking Graphiti server...")
        if not check_graphiti_health():
            print(f"{RED}✗ Graphiti server not available{RESET}")
            print()
            print("Start it with:")
            print("  python .claude/skills/graphiti/scripts/graphiti_server.py start")
            sys.exit(1)
        print(f"{GREEN}✓ Graphiti server is healthy{RESET}")
    else:
        print(f"{YELLOW}DRY RUN MODE - no ingestion{RESET}")
    print()

    # Collect files
    print("Collecting Tier 1 files...")
    files = collect_tier1_files()

    # Filter by category if specified
    if args.category:
        category_patterns = TIER1_CATEGORIES[args.category]["patterns"]
        files = [
            f for f in files
            if any(
                f.match(p.replace("**", "*"))
                for p in category_patterns
            )
        ]

    print(f"Found {len(files)} files to process")
    print()

    # Show category breakdown
    category_counts = {}
    for f in files:
        cat = get_category_from_path(f)
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("Categories:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    print()

    if not files:
        print(f"{YELLOW}No files to process{RESET}")
        return

    # Estimate time
    if not args.dry_run:
        est_minutes = len(files) * 1  # ~1 minute per file
        print(f"Estimated time: ~{est_minutes} minutes ({len(files)} files × ~1 min/file)")
        print()

    # Run ingestion
    print(f"{BOLD}Starting ingestion...{RESET}")
    print()
    start_time = datetime.now()

    results = asyncio.run(ingest_all(files, args.dry_run, args.verbose))

    elapsed = datetime.now() - start_time
    print()
    print(f"{BOLD}Results:{RESET}")
    print(f"  Success: {GREEN}{results['success']}{RESET}")
    print(f"  Failed: {RED}{results['failed']}{RESET}")
    print(f"  Time: {elapsed}")

    if results["errors"]:
        print()
        print(f"{YELLOW}Errors:{RESET}")
        for err in results["errors"][:10]:
            print(f"  {err['file']}: {err['error']}")
        if len(results["errors"]) > 10:
            print(f"  ... and {len(results['errors']) - 10} more")


if __name__ == "__main__":
    main()
