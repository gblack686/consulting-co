#!/usr/bin/env python3
"""
AI-Agent-KB Vector Index Builder

Creates a Supabase pgvector index for Tier 2 KB components:
- Commands (~90 files)
- Agents (~12 files)
- Skills (~22 files)
- Hooks config files (~10 files)
- Output styles (~5 files)

Extracts frontmatter metadata and first 500 chars of content,
generates embeddings via OpenAI, and stores in Supabase.

Usage:
    cd .claude/scripts
    python create_vector_index.py

    # With options:
    python create_vector_index.py --dry-run           # Preview without writing
    python create_vector_index.py --folder commands   # Index only commands
    python create_vector_index.py --force             # Re-index all files
"""

import os
import sys
import json
import re
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Third-party imports
try:
    import yaml
    from openai import OpenAI
    from supabase import create_client, Client
    import boto3
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install openai supabase pyyaml boto3")
    sys.exit(1)

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Configuration
KB_ROOT = Path(__file__).parent.parent  # .claude directory
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
BATCH_SIZE = 100  # OpenAI embedding batch size

# Tier 2 folders to index (lightweight components)
TIER2_FOLDERS = {
    "commands": {"type": "command", "exclude_patterns": ["experts/"]},
    "agents": {"type": "agent", "exclude_patterns": []},
    "skills": {"type": "skill", "exclude_patterns": []},
    "hooks": {"type": "hook", "exclude_patterns": ["utils/"]},
    "output-styles": {"type": "output-style", "exclude_patterns": []},
}

# Files to skip
SKIP_FILES = {
    "_index.md",
    "_TAXONOMY.md",
    "_SCHEMA.md",
    "_template.md",
    "AGENT_SUGGESTIONS.md",
}


def get_supabase_credentials() -> tuple[str, str]:
    """Get Supabase credentials from AWS Secrets Manager."""
    try:
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(
            SecretId="gbautomation/infrastructure/supabase"
        )
        secret = json.loads(response["SecretString"])
        return secret["url"], secret["service_key"]
    except Exception as e:
        print(f"{RED}Error getting Supabase credentials: {e}{RESET}")
        print("Falling back to environment variables...")
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
            )
        return url, key


def get_openai_client() -> OpenAI:
    """Initialize OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try AWS Secrets Manager
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


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content

    # Check for YAML frontmatter (--- delimited)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError:
                pass

    return frontmatter, body


def extract_summary(body: str, max_chars: int = 500) -> str:
    """Extract summary from markdown body.

    Looks for Purpose section first, then falls back to first content.
    """
    # Look for Purpose or Description section
    purpose_patterns = [
        r"##?\s*Purpose\s*\n(.*?)(?=\n##|\n---|\Z)",
        r"##?\s*Description\s*\n(.*?)(?=\n##|\n---|\Z)",
        r"##?\s*Overview\s*\n(.*?)(?=\n##|\n---|\Z)",
        r"##?\s*What\s+(?:it|this)\s+does\s*\n(.*?)(?=\n##|\n---|\Z)",
    ]

    for pattern in purpose_patterns:
        match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
        if match:
            summary = match.group(1).strip()
            # Clean up markdown formatting
            summary = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", summary)  # Links
            summary = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", summary)  # Bold/italic
            summary = re.sub(r"`([^`]+)`", r"\1", summary)  # Code
            summary = re.sub(r"\n+", " ", summary)  # Newlines
            return summary[:max_chars].strip()

    # Fallback: use first non-header content
    lines = []
    for line in body.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            lines.append(line)
        if len(" ".join(lines)) > max_chars:
            break

    summary = " ".join(lines)
    summary = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", summary)
    summary = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", summary)
    summary = re.sub(r"`([^`]+)`", r"\1", summary)
    return summary[:max_chars].strip()


def extract_name(frontmatter: dict, file_path: Path) -> str:
    """Extract name from frontmatter or derive from filename."""
    if "name" in frontmatter:
        return frontmatter["name"]
    if "title" in frontmatter:
        return frontmatter["title"]
    if "description" in frontmatter:
        # Use first sentence of description
        desc = frontmatter["description"]
        return desc.split(".")[0][:100]

    # Derive from filename
    name = file_path.stem
    if name == "SKILL":
        name = file_path.parent.name
    elif name == "AGENT_SPEC":
        name = file_path.parent.name

    # Convert kebab-case to Title Case
    return name.replace("-", " ").replace("_", " ").title()


def generate_file_id(file_path: Path) -> str:
    """Generate unique ID for a file."""
    # Use relative path from KB root as ID
    rel_path = file_path.relative_to(KB_ROOT)
    return str(rel_path).replace("\\", "/").replace(".md", "").replace(".yaml", "")


def collect_files(folder: str, config: dict) -> list[Path]:
    """Collect all files to index in a folder."""
    folder_path = KB_ROOT / folder
    if not folder_path.exists():
        return []

    files = []
    exclude_patterns = config.get("exclude_patterns", [])

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip non-content files
        if file_path.suffix not in [".md", ".yaml"]:
            continue

        # Skip known skip files
        if file_path.name in SKIP_FILES:
            continue

        # Skip excluded patterns
        rel_path = str(file_path.relative_to(folder_path))
        if any(pattern in rel_path for pattern in exclude_patterns):
            continue

        # Skip template files
        if "template" in file_path.name.lower():
            continue

        files.append(file_path)

    return files


def process_file(file_path: Path, folder: str, file_type: str) -> Optional[dict]:
    """Process a single file and extract metadata."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"{YELLOW}  Warning: Could not read {file_path}: {e}{RESET}")
        return None

    frontmatter, body = parse_frontmatter(content)

    # Extract metadata
    name = extract_name(frontmatter, file_path)
    summary = frontmatter.get("description", "") or extract_summary(body)
    tags = frontmatter.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    # Build text for embedding
    embedding_text = f"{file_type}: {name}\n{summary}"
    if tags:
        embedding_text += f"\nTags: {', '.join(tags)}"

    return {
        "id": generate_file_id(file_path),
        "file_path": str(file_path.relative_to(KB_ROOT)).replace("\\", "/"),
        "folder": folder,
        "type": file_type,
        "name": name,
        "summary": summary[:1000] if summary else f"{file_type} component",
        "tags": tags,
        "embedding_text": embedding_text[:8000],  # OpenAI limit
    }


def generate_embeddings(openai_client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return [item.embedding for item in response.data]


def upsert_to_supabase(
    supabase: Client,
    records: list[dict],
    dry_run: bool = False,
    batch_size: int = 10
) -> int:
    """Upsert records to Supabase kb_index table.

    Generates SQL file for batch execution via Supabase MCP or SQL Editor.
    The Python SDK has issues with this table, so we use direct SQL.
    """
    if dry_run:
        return len(records)

    sql_file = Path(__file__).parent / "kb_index_inserts.sql"

    # Generate SQL file for all inserts with embeddings
    print(f"  Generating SQL file: {sql_file.name}")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("-- KB Index Inserts with Embeddings\n")
        f.write("-- Generated by create_vector_index.py\n")
        f.write("-- Run via Supabase MCP execute_sql (in batches) or SQL Editor\n\n")

        for i, record in enumerate(records):
            # Escape single quotes in text fields
            id_escaped = record["id"].replace("'", "''")
            file_path = record["file_path"].replace("'", "''")
            folder = record["folder"].replace("'", "''")
            type_val = record["type"].replace("'", "''")
            name = record["name"].replace("'", "''")
            summary = record["summary"][:1000].replace("'", "''")
            tags = record.get("tags", [])
            tags_str = "ARRAY[" + ",".join(f"'{t}'" for t in tags) + "]::text[]" if tags else "ARRAY[]::text[]"

            # Embedding
            embedding = record.get("embedding", [])
            if embedding:
                embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
                embedding_sql = f"'{embedding_str}'::vector(1536)"
            else:
                embedding_sql = "NULL"

            f.write(f"""INSERT INTO kb_index (id, file_path, folder, type, name, summary, tags, embedding)
VALUES ('{id_escaped}', '{file_path}', '{folder}', '{type_val}', '{name}', '{summary}', {tags_str}, {embedding_sql})
ON CONFLICT (id) DO UPDATE SET file_path=EXCLUDED.file_path, folder=EXCLUDED.folder, type=EXCLUDED.type, name=EXCLUDED.name, summary=EXCLUDED.summary, tags=EXCLUDED.tags, embedding=EXCLUDED.embedding, updated_at=NOW();\n""")

    print(f"{GREEN}  Generated {len(records)} INSERT statements{RESET}")
    print(f"  File: {sql_file}")
    print()
    print(f"{YELLOW}  Next step: Run the SQL file via Supabase MCP or SQL Editor{RESET}")
    print(f"  The file is too large for a single execute_sql call.")
    print(f"  Split into batches of ~20 statements each.")

    return len(records)


def main():
    parser = argparse.ArgumentParser(
        description="Build vector index for AI-Agent-KB"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files without writing to database"
    )
    parser.add_argument(
        "--folder",
        type=str,
        help="Index only a specific folder"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-index all files even if unchanged"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output"
    )
    args = parser.parse_args()

    print(f"{BOLD}AI-Agent-KB Vector Index Builder{RESET}")
    print(f"KB Root: {KB_ROOT}")
    print()

    # Initialize clients
    if not args.dry_run:
        print("Initializing clients...")
        supabase_url, supabase_key = get_supabase_credentials()
        supabase = create_client(supabase_url, supabase_key)
        openai_client = get_openai_client()
        print(f"{GREEN}✓ Supabase connected{RESET}")
        print(f"{GREEN}✓ OpenAI client initialized{RESET}")
    else:
        supabase = None
        openai_client = None
        print(f"{YELLOW}DRY RUN MODE - no database writes{RESET}")
    print()

    # Determine folders to process
    folders_to_process = TIER2_FOLDERS
    if args.folder:
        if args.folder not in TIER2_FOLDERS:
            print(f"{RED}Unknown folder: {args.folder}{RESET}")
            print(f"Available: {', '.join(TIER2_FOLDERS.keys())}")
            sys.exit(1)
        folders_to_process = {args.folder: TIER2_FOLDERS[args.folder]}

    # Collect and process files
    all_records = []
    for folder, config in folders_to_process.items():
        print(f"{BLUE}Processing {folder}...{RESET}")
        files = collect_files(folder, config)

        for file_path in files:
            record = process_file(file_path, folder, config["type"])
            if record:
                all_records.append(record)
                if args.verbose:
                    print(f"  {GREEN}✓{RESET} {record['id']}")

        print(f"  Found {len(files)} files")

    print()
    print(f"Total files to index: {len(all_records)}")

    if not all_records:
        print(f"{YELLOW}No files to index{RESET}")
        return

    if args.dry_run:
        print()
        print(f"{BOLD}Files that would be indexed:{RESET}")
        for record in all_records[:20]:
            print(f"  {record['type']}: {record['name']}")
            if args.verbose:
                print(f"    Path: {record['file_path']}")
                print(f"    Summary: {record['summary'][:100]}...")
        if len(all_records) > 20:
            print(f"  ... and {len(all_records) - 20} more")
        return

    # Generate embeddings in batches
    print()
    print("Generating embeddings...")
    embedding_texts = [r["embedding_text"] for r in all_records]
    all_embeddings = []

    for i in range(0, len(embedding_texts), BATCH_SIZE):
        batch = embedding_texts[i:i + BATCH_SIZE]
        batch_embeddings = generate_embeddings(openai_client, batch)
        all_embeddings.extend(batch_embeddings)
        print(f"  Processed {min(i + BATCH_SIZE, len(embedding_texts))}/{len(embedding_texts)}")

    # Add embeddings to records and remove embedding_text
    for record, embedding in zip(all_records, all_embeddings):
        record["embedding"] = embedding
        del record["embedding_text"]

    # Upsert to Supabase
    print()
    print("Writing to Supabase...")
    upserted = upsert_to_supabase(supabase, all_records, args.dry_run)

    print()
    print(f"{GREEN}{BOLD}Success!{RESET}")
    print(f"Indexed {upserted} files to Supabase kb_index table")

    # Show summary by folder
    print()
    print("Summary by folder:")
    folder_counts = {}
    for record in all_records:
        folder_counts[record["folder"]] = folder_counts.get(record["folder"], 0) + 1
    for folder, count in sorted(folder_counts.items()):
        print(f"  {folder}: {count} files")


if __name__ == "__main__":
    main()
