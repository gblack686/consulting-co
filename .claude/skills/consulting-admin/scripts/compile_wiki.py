"""
Compile cross-client knowledge into the company wiki using claude -p.

Reads knowledge/index.md from each client's second brain and compiles
cross-client entities, concepts, and connections into the wiki.

Usage:
  python compile_wiki.py
  python compile_wiki.py --dry-run
  python compile_wiki.py --clients fisch-group gbautomation
"""
import sys
import os
import re
import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")

GBAUTO_DIR = Path("C:/Users/gblac/OneDrive/Desktop/gbauto")
WIKI_DIR = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co/wiki")
CLIENTS_DIR = Path(__file__).parent / "clients"


# ── Client Discovery ────────────────────────────────────────────────────────

def discover_clients(filter_slugs: list[str] | None = None) -> list[dict]:
    """Find all client configs and their second brain paths."""
    clients = []
    for config_path in sorted(CLIENTS_DIR.glob("*.json")):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        slug = config.get("client_slug", config_path.stem)
        if filter_slugs and slug not in filter_slugs:
            continue

        sb_dir = Path(config["output_base"]).parent  # second-brain/
        knowledge_dir = sb_dir / "knowledge"
        intelligence_dir = sb_dir / "intelligence"

        clients.append({
            "name": config["client_name"],
            "slug": slug,
            "config_path": str(config_path),
            "second_brain": str(sb_dir),
            "knowledge_dir": str(knowledge_dir),
            "intelligence_dir": str(intelligence_dir),
            "status": config.get("status", "Unknown"),
            "engagement_start": config.get("engagement_start"),
            "contacts": config.get("contacts", ""),
        })
    return clients


# ── Source Collection ────────────────────────────────────────────────────────

def collect_wiki_sources(clients: list[dict]) -> dict:
    """Collect knowledge indexes + key files from each client second brain."""
    sources = {}
    for client in clients:
        slug = client["slug"]
        kd = Path(client["knowledge_dir"])
        sources[slug] = {
            "name": client["name"],
            "status": client["status"],
            "contacts": client["contacts"],
            "engagement_start": client["engagement_start"],
            "index": None,
            "articles": [],
        }

        # Read knowledge index
        index_path = kd / "index.md"
        if index_path.exists():
            sources[slug]["index"] = index_path.read_text(encoding="utf-8")

        # Read all concept/connection articles (titles + summaries only to save tokens)
        for subdir in ["concepts", "connections"]:
            art_dir = kd / subdir
            if not art_dir.is_dir():
                continue
            for art_path in sorted(art_dir.glob("*.md")):
                content = art_path.read_text(encoding="utf-8", errors="replace")
                # Keep only frontmatter + first 500 chars of body
                if len(content) > 800:
                    content = content[:800] + "\n\n[... truncated ...]"
                sources[slug]["articles"].append({
                    "path": f"{subdir}/{art_path.name}",
                    "content": content,
                })

        # Read engagement timeline if exists
        timeline_path = Path(client["intelligence_dir"]) / "_ENGAGEMENT_TIMELINE.md"
        if timeline_path.exists():
            timeline = timeline_path.read_text(encoding="utf-8", errors="replace")
            if len(timeline) > 2000:
                timeline = timeline[:2000] + "\n\n[... truncated ...]"
            sources[slug]["timeline"] = timeline

    return sources


# ── Prompt Building ──────────────────────────────────────────────────────────

def build_wiki_prompt(sources: dict, existing_index: str) -> str:
    """Build the wiki compilation prompt."""
    parts = []
    parts.append("# GBAutomation Wiki Compilation\n")
    parts.append("You are a wiki compiler for GBAutomation, an AI automation consulting company.")
    parts.append("Read the per-client knowledge below and produce cross-client wiki pages.\n")

    parts.append("## Existing Wiki Index\n")
    parts.append(existing_index if existing_index.strip() else "_Empty wiki._")
    parts.append("\n\n---\n")

    for slug, data in sources.items():
        parts.append(f"## Client: {data['name']} (`{slug}`)\n")
        parts.append(f"- **Status**: {data['status']}")
        parts.append(f"- **Contacts**: {data['contacts']}")
        parts.append(f"- **Engagement start**: {data['engagement_start'] or 'Unknown'}\n")

        if data.get("index"):
            parts.append(f"### Knowledge Index\n{data['index']}\n")

        if data.get("articles"):
            parts.append("### Compiled Articles\n")
            for art in data["articles"]:
                parts.append(f"#### `{art['path']}`\n{art['content']}\n")

        if data.get("timeline"):
            parts.append(f"### Engagement Timeline\n{data['timeline']}\n")

        parts.append("---\n")

    parts.append("""
## Output Instructions

Produce wiki pages for the GBAutomation company wiki. Follow these rules:

1. **Entity pages** (`entities/`) — one per client, person, tool, or service mentioned across clients.
   Update existing pages rather than creating duplicates.
2. **Concept pages** (`concepts/`) — cross-client patterns, consulting frameworks, technical approaches
   that appear in 2+ client engagements.
3. **Source summaries** (`sources/`) — summaries of key raw sources (optional, only if highly relevant).

Each page must have this format:

```markdown
---
title: "Page Title"
type: entity  # or: concept, source, ops
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [client-slug/knowledge/concepts/article.md]
---

Page body with [[wikilinks]] to other wiki pages.
```

Filenames: kebab-case.md (e.g. `michael-fisch.md`, `second-brain-architecture.md`)

After all pages, output a JSON manifest fenced with ```json ... ```:
```json
{
  "pages": [
    {"filename": "michael-fisch.md", "dir": "entities", "title": "Michael Fisch", "action": "update", "summary": "One-line"},
    ...
  ],
  "index_update": "Full updated markdown for wiki/index.md (after YAML frontmatter)"
}
```

Focus on cross-client insights. Entity pages should synthesize across all client interactions.
""")

    return "\n".join(parts)


# ── Claude CLI ───────────────────────────────────────────────────────────────

def run_claude(prompt_path: str) -> str:
    """Shell out to claude -p."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError("claude CLI not found on PATH.")

    env = os.environ.copy()
    for key in ["CLAUDECODE", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN"]:
        env.pop(key, None)

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()

    result = subprocess.run(
        [claude_bin, "-p", prompt_content, "--output-format", "json"],
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr.strip()}")

    return result.stdout


# ── Output Parsing & Writing ─────────────────────────────────────────────────

def parse_wiki_output(raw: str) -> tuple[list[dict], dict]:
    """Parse claude output into page blocks + manifest."""
    try:
        envelope = json.loads(raw)
        text = envelope.get("result", raw)
    except json.JSONDecodeError:
        text = raw

    # Extract JSON manifest
    manifest = {}
    json_blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    for block in json_blocks:
        try:
            parsed = json.loads(block)
            if "pages" in parsed:
                manifest = parsed
                break
        except json.JSONDecodeError:
            continue

    if not manifest:
        raise RuntimeError("Could not find JSON manifest in Claude output.")

    # Extract page content blocks
    page_blocks = []
    fm_splits = re.split(r"\n(?=---\ntitle:)", text)
    for chunk in fm_splits:
        chunk = chunk.strip()
        if not chunk.startswith("---\ntitle:"):
            continue
        title_match = re.search(r"title:\s*[\"']?(.+?)[\"']?\s*\n", chunk)
        if not title_match:
            continue
        t = title_match.group(1).strip().strip("\"'")
        fn = None
        target_dir = "entities"
        for page in manifest.get("pages", []):
            if page["title"].strip().strip("\"'") == t:
                fn = page["filename"]
                target_dir = page.get("dir", "entities")
                break
        if not fn:
            slug = re.sub(r"[^a-z0-9\s-]", "", t.lower())
            fn = re.sub(r"\s+", "-", slug.strip())[:60] + ".md"
        page_blocks.append({"filename": fn, "dir": target_dir, "content": chunk})

    return page_blocks, manifest


def write_wiki_pages(pages: list[dict]) -> dict[str, int]:
    """Write pages to wiki directories. Returns counts by dir."""
    counts = {}
    for page in pages:
        target_dir = WIKI_DIR / page["dir"]
        target_dir.mkdir(parents=True, exist_ok=True)
        filepath = target_dir / page["filename"]
        filepath.write_text(page["content"], encoding="utf-8")
        counts[page["dir"]] = counts.get(page["dir"], 0) + 1
        print(f"    Wrote: {page['dir']}/{page['filename']}")
    return counts


def update_wiki_index(manifest: dict) -> None:
    """Update wiki/index.md with compiled catalog."""
    index_path = WIKI_DIR / "index.md"
    index_update = manifest.get("index_update", "")

    if index_update:
        frontmatter = f"""---
title: Index
type: index
updated: {datetime.now(PT).strftime('%Y-%m-%d')}
---
"""
        index_path.write_text(frontmatter + "\n" + index_update, encoding="utf-8")
        print("  Updated: index.md")


def append_wiki_log(pages: list[dict], clients: list[dict]) -> None:
    """Append compilation event to wiki/log.md."""
    log_path = WIKI_DIR / "log.md"
    now = datetime.now(PT)
    ts = now.strftime("%Y-%m-%dT%H:%M")
    client_names = ", ".join(c["name"] for c in clients)
    page_list = ", ".join(f"{p['dir']}/{p['filename']}" for p in pages[:10])
    if len(pages) > 10:
        page_list += f", ... (+{len(pages) - 10} more)"

    entry = f"""
## [{ts}] wiki-compile | {len(pages)} pages from {len(clients)} clients
- Clients: {client_names}
- Pages: {page_list}
"""

    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "---\ntitle: Wiki Log\ntype: log\n---\n\n# Wiki Compilation Log\n"
    log_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    print("  Appended to: log.md")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compile cross-client knowledge into wiki")
    parser.add_argument("--dry-run", action="store_true", help="Preview without running")
    parser.add_argument("--clients", nargs="*", help="Filter to specific client slugs")
    args = parser.parse_args()

    print("=" * 60)
    print("GBAUTOMATION WIKI COMPILATION")
    print("=" * 60)

    # 1. Discover clients
    print("\n[1/5] Discovering clients...")
    clients = discover_clients(args.clients)
    print(f"  Found {len(clients)} clients: {', '.join(c['name'] for c in clients)}")

    if not clients:
        print("  No client configs found. Nothing to compile.")
        return

    # 2. Collect sources
    print("\n[2/5] Collecting knowledge sources...")
    sources = collect_wiki_sources(clients)
    total_articles = sum(len(d["articles"]) for d in sources.values())
    print(f"  Total knowledge articles across clients: {total_articles}")

    # 3. Dry run
    if args.dry_run:
        print("\n[DRY RUN] Would compile wiki from:")
        for slug, data in sources.items():
            has_index = "yes" if data["index"] else "no"
            art_count = len(data["articles"])
            print(f"  {data['name']} ({slug}): index={has_index}, articles={art_count}")
        print(f"\n  Wiki output: {WIKI_DIR}")
        return

    # 4. Check claude CLI
    if not shutil.which("claude"):
        print("\nERROR: claude CLI not found on PATH.")
        sys.exit(1)

    # 5. Build prompt and call claude
    print("\n[3/5] Building wiki prompt...")
    existing_index = ""
    index_path = WIKI_DIR / "index.md"
    if index_path.exists():
        existing_index = index_path.read_text(encoding="utf-8")

    prompt = build_wiki_prompt(sources, existing_index)

    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(prompt)
    tmp.close()
    prompt_path = tmp.name
    print(f"  Prompt size: {len(prompt) / 1024:.1f} KB")

    try:
        print("\n[4/5] Running claude -p (this may take a few minutes)...")
        raw_output = run_claude(prompt_path)
        print(f"  Claude returned {len(raw_output):,} chars")

        # Save raw output
        raw_path = WIKI_DIR / "_last_compilation_raw.json"
        raw_path.write_text(raw_output, encoding="utf-8")

        print("\n[5/5] Parsing and writing pages...")
        pages, manifest = parse_wiki_output(raw_output)
        print(f"  Parsed {len(pages)} pages")

        if not pages:
            print(f"\n  WARNING: No pages parsed. Raw output saved to: {raw_path}")
            return

        counts = write_wiki_pages(pages)
        update_wiki_index(manifest)
        append_wiki_log(pages, clients)

    finally:
        try:
            os.unlink(prompt_path)
        except OSError:
            pass

    print("\n" + "=" * 60)
    print("WIKI COMPILATION COMPLETE")
    print(f"  Wiki dir: {WIKI_DIR}")
    for dir_name, count in sorted(counts.items()):
        print(f"  {dir_name}: {count}")
    print(f"  Total pages: {len(pages)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
