"""
Compile raw intelligence sources into structured knowledge articles using claude -p.

Usage:
  python compile_knowledge.py --config clients/fisch-group.json
  python compile_knowledge.py --config clients/fisch-group.json --dry-run
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PT = ZoneInfo("America/Los_Angeles")


# ── Config Loading ────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Source Scanning ───────────────────────────────────────────────────────────

def scan_sources(intelligence_dir: Path, daily_dir: Path) -> list[dict]:
    """Walk intelligence/ and daily/ collecting .md and .txt files."""
    sources = []
    for search_dir in [intelligence_dir, daily_dir]:
        if not search_dir.exists():
            continue
        for root, _dirs, files in os.walk(search_dir):
            for fname in files:
                if not fname.endswith((".md", ".txt")):
                    continue
                fpath = Path(root) / fname
                stat = fpath.stat()
                sources.append({
                    "path": str(fpath),
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "rel": str(fpath.relative_to(search_dir.parent)),
                })
    return sources


def get_last_compilation_ts(log_path: Path) -> float:
    """Parse log.md for the most recent compilation timestamp. Return 0 if none found."""
    if not log_path.exists():
        return 0.0
    text = log_path.read_text(encoding="utf-8")
    # Match lines like: ## [2026-04-12] compile | ...
    dates = re.findall(r"## \[(\d{4}-\d{2}-\d{2}(?:T[\d:]+)?)\] compile", text)
    if not dates:
        return 0.0
    last = dates[-1]
    try:
        if "T" in last:
            dt = datetime.fromisoformat(last).replace(tzinfo=PT)
        else:
            dt = datetime.strptime(last, "%Y-%m-%d").replace(tzinfo=PT)
        return dt.timestamp()
    except Exception:
        return 0.0


def filter_new_sources(sources: list[dict], since_ts: float) -> list[dict]:
    """Return sources modified after since_ts. If since_ts is 0, return all."""
    if since_ts == 0:
        return sources
    return [s for s in sources if s["mtime"] > since_ts]


# ── Prompt Building ──────────────────────────────────────────────────────────

def build_prompt(sources: list[dict], index_contents: str, client_name: str) -> str:
    """Build the compilation prompt with all source contents."""
    parts = []
    parts.append(f"# Knowledge Compilation for {client_name}\n")
    parts.append("You are a knowledge compiler. Read the following source files and produce structured knowledge articles.\n")
    parts.append("## Existing Knowledge Index\n")
    parts.append(index_contents if index_contents.strip() else "_Empty — first compilation._")
    parts.append("\n\n## Source Files\n")

    for src in sources:
        fpath = Path(src["path"])
        parts.append(f"### Source: `{src['rel']}`\n")
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            # Cap individual files at 30k chars to stay within limits
            if len(content) > 30000:
                content = content[:30000] + "\n\n[... truncated at 30k chars ...]"
            parts.append(content)
        except Exception as e:
            parts.append(f"[Error reading file: {e}]")
        parts.append("\n\n---\n")

    parts.append("""
## Output Instructions

Produce knowledge articles from the sources above. Follow these rules:

1. **Concepts** — single-topic deep articles. One per distinct topic/theme found in the sources.
2. **Connections** — cross-cutting insights that link 2+ concepts together.

Each article must have this format:

```markdown
---
title: "Article Title"
type: concept  # or: connection
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - intelligence/transcripts/2026-03-05-session-1-intake.md
  - intelligence/correspondence/2026-03-10-some-thread.md
---

Article body with [[wikilinks]] to other articles where relevant.
```

Article filenames: kebab-case.md (e.g. `quickbooks-mcp-integration.md`)

After all articles, output a JSON manifest block fenced with ```json ... ``` containing:
```json
{
  "articles": [
    {"filename": "kebab-case.md", "title": "Article Title", "type": "concept", "summary": "One-line summary"},
    ...
  ],
  "index_update": "Full updated markdown for the index.md file (replace all content after the YAML frontmatter)"
}
```

Focus on actionable, specific knowledge — not generic summaries. Extract decisions, patterns, technical details, relationships, and open questions.
""")

    return "\n".join(parts)


# ── Claude CLI Execution ─────────────────────────────────────────────────────

def run_claude(prompt_path: str) -> str:
    """Shell out to claude -p, returning stdout. Unsets session env vars first."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise RuntimeError("claude CLI not found on PATH. Install it or add to PATH.")

    env = os.environ.copy()
    # Must unset these so claude falls back to stored credentials in ~/.claude
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
        stderr = result.stderr.strip()
        raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {stderr}")

    return result.stdout


# ── Output Parsing & Writing ─────────────────────────────────────────────────

def parse_claude_output(raw: str) -> tuple[list[dict], dict]:
    """Parse claude JSON output, extract articles and manifest.

    Returns (article_blocks, manifest).
    article_blocks: list of {"filename": ..., "content": ...}
    manifest: the JSON manifest dict
    """
    # claude --output-format json wraps the response in a JSON object
    try:
        envelope = json.loads(raw)
        # The actual text is in the "result" field
        text = envelope.get("result", raw)
    except json.JSONDecodeError:
        text = raw

    # Extract the JSON manifest
    manifest = {}
    json_blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    for block in json_blocks:
        try:
            parsed = json.loads(block)
            if "articles" in parsed:
                manifest = parsed
                break
        except json.JSONDecodeError:
            continue

    if not manifest:
        raise RuntimeError("Could not find JSON manifest in Claude output. Raw output saved for inspection.")

    # Extract article content blocks — everything between articles
    # Split on article file markers: look for YAML frontmatter blocks
    article_blocks = []
    # Pattern: find all markdown sections that start with ---\ntitle:
    article_pattern = re.compile(
        r"(?:^|\n)(?:#+\s*`?([a-z0-9-]+\.md)`?\s*\n+)?"  # optional heading with filename
        r"(---\n"  # frontmatter start
        r"title:\s*[\"']?(.+?)[\"']?\s*\n"  # title
        r".*?"  # rest of frontmatter
        r"---\n"  # frontmatter end
        r".*?)"  # body
        r"(?=\n---\ntitle:|\n```json|\Z)",  # lookahead for next article or manifest
        re.DOTALL
    )

    matches = article_pattern.finditer(text)
    seen_filenames = set()

    for match in matches:
        heading_filename = match.group(1)
        full_content = match.group(2).strip()
        title_from_fm = match.group(3).strip()

        if not full_content or "type:" not in full_content:
            continue

        # Determine filename from heading or manifest
        filename = heading_filename
        if not filename:
            # Try to find in manifest by title
            for art in manifest.get("articles", []):
                if art["title"].strip().strip('"\'') == title_from_fm:
                    filename = art["filename"]
                    break
        if not filename:
            # Generate from title
            slug = re.sub(r"[^a-z0-9\s-]", "", title_from_fm.lower())
            filename = re.sub(r"\s+", "-", slug.strip())[:60] + ".md"

        if filename in seen_filenames:
            continue
        seen_filenames.add(filename)

        article_blocks.append({
            "filename": filename,
            "content": full_content,
        })

    # If parsing missed articles but manifest has them, that's okay — we write what we found
    # Also ensure every manifest article has a content block; fill from any we might have missed
    manifest_filenames = {a["filename"] for a in manifest.get("articles", [])}
    found_filenames = {a["filename"] for a in article_blocks}

    if not article_blocks and manifest.get("articles"):
        # Fallback: try splitting on --- boundaries more aggressively
        fm_splits = re.split(r"\n(?=---\ntitle:)", text)
        for chunk in fm_splits:
            chunk = chunk.strip()
            if not chunk.startswith("---\ntitle:"):
                continue
            title_match = re.search(r"title:\s*[\"']?(.+?)[\"']?\s*\n", chunk)
            if not title_match:
                continue
            t = title_match.group(1).strip()
            fn = None
            for art in manifest.get("articles", []):
                if art["title"].strip().strip('"\'') == t:
                    fn = art["filename"]
                    break
            if not fn:
                slug = re.sub(r"[^a-z0-9\s-]", "", t.lower())
                fn = re.sub(r"\s+", "-", slug.strip())[:60] + ".md"
            article_blocks.append({"filename": fn, "content": chunk})

    return article_blocks, manifest


def write_articles(articles: list[dict], knowledge_dir: Path) -> dict[str, int]:
    """Write article files to concepts/ or connections/. Returns counts by type."""
    counts = {"concept": 0, "connection": 0}
    for art in articles:
        content = art["content"]
        # Determine type from frontmatter
        type_match = re.search(r"type:\s*(concept|connection)", content)
        art_type = type_match.group(1) if type_match else "concept"

        subdir = knowledge_dir / (art_type + "s")
        subdir.mkdir(parents=True, exist_ok=True)

        filepath = subdir / art["filename"]
        filepath.write_text(content, encoding="utf-8")
        counts[art_type] = counts.get(art_type, 0) + 1
        print(f"    Wrote: {art_type}s/{art['filename']}")
    return counts


def update_index(manifest: dict, knowledge_dir: Path, client_name: str) -> None:
    """Rewrite index.md with updated catalog from manifest."""
    index_path = knowledge_dir / "index.md"
    index_update = manifest.get("index_update", "")

    if index_update:
        # Preserve original frontmatter, replace body
        frontmatter = f"""---
title: {client_name} Knowledge Index
type: index
created: 2026-04-12
updated: {datetime.now(PT).strftime('%Y-%m-%d')}
---
"""
        index_path.write_text(frontmatter + "\n" + index_update, encoding="utf-8")
    else:
        # Build a basic index from manifest articles
        lines = [
            "---",
            f"title: {client_name} Knowledge Index",
            "type: index",
            "created: 2026-04-12",
            f"updated: {datetime.now(PT).strftime('%Y-%m-%d')}",
            "---", "",
            f"# {client_name} -- Knowledge Index", "",
            "Master catalog of compiled knowledge.", "",
            "## Concepts", "",
        ]
        for art in manifest.get("articles", []):
            if art.get("type") == "concept":
                lines.append(f"- [[{art['filename'].replace('.md', '')}]] -- {art.get('summary', art['title'])}")
        lines.extend(["", "## Connections", ""])
        for art in manifest.get("articles", []):
            if art.get("type") == "connection":
                lines.append(f"- [[{art['filename'].replace('.md', '')}]] -- {art.get('summary', art['title'])}")
        lines.extend(["", "## Q&A", "", "_No filed query answers yet._", ""])
        index_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"  Updated: index.md")


def append_log(log_path: Path, sources: list[dict], counts: dict[str, int], manifest: dict) -> None:
    """Append compilation event to log.md."""
    now = datetime.now(PT)
    ts = now.strftime("%Y-%m-%dT%H:%M")
    date_str = now.strftime("%Y-%m-%d")

    article_list = manifest.get("articles", [])
    article_summary = ", ".join(a["filename"] for a in article_list[:10])
    if len(article_list) > 10:
        article_summary += f", ... (+{len(article_list) - 10} more)"

    entry = f"""
## [{ts}] compile | {len(article_list)} articles from {len(sources)} sources
- Concepts: {counts.get('concept', 0)}, Connections: {counts.get('connection', 0)}
- Sources compiled: {len(sources)} files
- Articles: {article_summary}
"""

    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    log_path.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
    print(f"  Appended to: log.md")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Compile intelligence into knowledge articles")
    parser.add_argument("--config", "-c", required=True, help="Path to client config JSON")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be compiled without running")
    args = parser.parse_args()

    config = load_config(args.config)
    client_name = config["client_name"]
    intelligence_dir = Path(config["output_base"])
    # Derive knowledge_base by replacing intelligence with knowledge
    knowledge_dir = Path(str(config["output_base"]).replace("intelligence", "knowledge"))
    daily_dir = intelligence_dir.parent / "daily"

    print("=" * 60)
    print(f"{client_name.upper()} -- KNOWLEDGE COMPILATION")
    print("=" * 60)

    # 1. Scan sources
    print("\n[1/5] Scanning sources...")
    all_sources = scan_sources(intelligence_dir, daily_dir)
    print(f"  Found {len(all_sources)} total source files")

    # 2. Filter to new/changed
    log_path = knowledge_dir / "log.md"
    last_ts = get_last_compilation_ts(log_path)
    if last_ts > 0:
        last_dt = datetime.fromtimestamp(last_ts, tz=PT).strftime("%Y-%m-%d %H:%M PT")
        print(f"  Last compilation: {last_dt}")
    else:
        print("  No previous compilation found -- will compile all sources")

    new_sources = filter_new_sources(all_sources, last_ts)
    print(f"  Sources to compile: {len(new_sources)}")

    if not new_sources:
        print("\n  No new sources since last compilation. Nothing to do.")
        return

    # 3. Dry run
    if args.dry_run:
        print("\n[DRY RUN] Would compile the following sources:")
        for src in sorted(new_sources, key=lambda s: s["rel"]):
            size_kb = src["size"] / 1024
            mtime_str = datetime.fromtimestamp(src["mtime"], tz=PT).strftime("%Y-%m-%d %H:%M PT")
            print(f"  {src['rel']}  ({size_kb:.1f} KB, modified {mtime_str})")
        total_kb = sum(s["size"] for s in new_sources) / 1024
        print(f"\n  Total: {len(new_sources)} files, {total_kb:.1f} KB")
        print(f"  Knowledge output: {knowledge_dir}")
        return

    # 4. Check claude CLI
    if not shutil.which("claude"):
        print("\nERROR: claude CLI not found on PATH.")
        print("Install it or ensure it is on your PATH.")
        sys.exit(1)

    # 5. Build prompt and call claude
    print("\n[2/5] Building compilation prompt...")
    index_path = knowledge_dir / "index.md"
    index_contents = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    prompt = build_prompt(new_sources, index_contents, client_name)

    # Write prompt to temp file
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(prompt)
    tmp.close()
    prompt_path = tmp.name
    prompt_size_kb = len(prompt) / 1024
    print(f"  Prompt size: {prompt_size_kb:.1f} KB ({len(new_sources)} sources)")
    print(f"  Temp file: {prompt_path}")

    try:
        print("\n[3/5] Running claude -p (this may take a few minutes)...")
        raw_output = run_claude(prompt_path)
        print(f"  Claude returned {len(raw_output):,} chars")

        # Save raw output for debugging
        raw_output_path = knowledge_dir / "_last_compilation_raw.json"
        raw_output_path.write_text(raw_output, encoding="utf-8")

        print("\n[4/5] Parsing articles...")
        articles, manifest = parse_claude_output(raw_output)
        print(f"  Parsed {len(articles)} articles from manifest ({len(manifest.get('articles', []))} listed)")

        if not articles:
            print("\n  WARNING: No articles were parsed from Claude output.")
            print(f"  Raw output saved to: {raw_output_path}")
            print("  Inspect the file and re-run if needed.")
            return

        # Write articles
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        counts = write_articles(articles, knowledge_dir)

        # Update index
        print("\n[5/5] Updating index and log...")
        update_index(manifest, knowledge_dir, client_name)
        append_log(log_path, new_sources, counts, manifest)

    finally:
        # Clean up temp file
        try:
            os.unlink(prompt_path)
        except OSError:
            pass

    print("\n" + "=" * 60)
    print("COMPILATION COMPLETE")
    print(f"  Knowledge dir: {knowledge_dir}")
    print(f"  Concepts: {counts.get('concept', 0)}")
    print(f"  Connections: {counts.get('connection', 0)}")
    print(f"  Total articles: {len(articles)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
