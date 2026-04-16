#!/usr/bin/env python3
"""
Sync library.yaml → library-catalog.json for the Archon Library viewer.

Reads library.yaml, resolves local SKILL.md / agent.md files,
extracts frontmatter + content, assigns business domain categories,
and writes a JSON catalog to Archon's public directory.

Usage:
  python sync_viewer.py [--dry-run] [--output PATH]

Default output: C:/Users/gblac/OneDrive/Desktop/archon/packages/web/public/library-catalog.json
"""

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# === Paths ===
LIBRARY_YAML = Path("C:/Users/gblac/OneDrive/Desktop/tac/the-library/library.yaml")
CONSULTING_CO = Path("C:/Users/gblac/OneDrive/Desktop/consulting-co")
ARCHON_PUBLIC = Path("C:/Users/gblac/OneDrive/Desktop/archon/packages/web/public")
HOME = Path.home()

# === Category assignment by keywords ===
CATEGORY_RULES = [
    # Order matters — first match wins. Put specific before general.
    ("Expert Systems", [
        "expert-tac", "expert-supabase", "expert-hooks", "expert-aws",
        "expert-obsidian", "expert-openclaw", "expert-pi", "expert-bowser",
        "expert-linkedin", "tac-expert", "hooks-expert", "aws-org-expert",
        "supabase-expert", "obsidian-expert", "obsidian-kb-expert",
        "openclaw-expert", "tac-scaffolding", "tac-kb-query",
    ]),
    ("Trading", [
        "trading", "backtest", "chart", "portfolio", "discord-scraping",
        "ta lesson", "expert-scheduler", "daily-lesson",
    ]),
    ("Consulting Pipeline", [
        "consulting", "intake", "session-processor", "client-linkedin",
        "client-personal", "client-research", "social-media-recon",
        "second-brain-prd", "daily-client-logs",
    ]),
    ("Communication", [
        "gmail", "gws", "email", "google workspace",
    ]),
    ("Sales & Outbound", [
        "linkedin-job", "lead gen", "sales navigator", "inmail",
    ]),
    ("Knowledge Management", [
        "obsidian", "graphiti", "knowledge", "vault", "schema-generator",
        "graphify", "wiki", "kb-expert",
    ]),
    ("Development Tools", [
        "build-agent", "plan-agent", "review-agent", "hook", "github",
        "worktree", "adw", "linear-build", "plugin-builder", "cdk", "forge",
        "skills-installer", "workflow-ideator",
    ]),
    ("Infrastructure", [
        "aws", "openclaw", "mac-mini", "supabase", "lightsail", "deploy",
        "setup-openclaw", "onboarding",
    ]),
    ("Browser & Research", [
        "browser", "bowser", "youtube", "scraping", "scrape",
        "agent-browser",
    ]),
    ("Operations", [
        "subscription", "cost-tracker", "team-runner", "skill-discovery",
        "domain-discovery", "mtg-art",
    ]),
    ("Meta & Platform", [
        "anthropic-memory", "memory", "revstar", "multi-agent-orchestrator",
        "drive-claw",
    ]),
]


def assign_category(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw.lower() in text:
                return category
    return "Other"


# === MTG color assignment ===
def assign_color(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    if re.search(r"github|git|ci/cd|code|build|review|plan|hook|forge|cdk|plugin", text):
        return "Blue"
    if re.search(r"aws|cloud|infra|lightsail|deploy|supabase", text):
        return "Green"
    if re.search(r"obsidian|doc|knowledge|vault|schema|wiki|kb", text):
        return "Red"
    if re.search(r"data|database|memory|graphiti|graph|pgvector|cost|track", text):
        return "Black"
    if re.search(r"test|valid|admin|onboard|qa|audit", text):
        return "White"
    return "Colorless"


# === Resolve source path to local file ===
def resolve_source(source: str, entry_type: str) -> Path | None:
    """Try to resolve a source URL/path to a readable local file."""
    # GitHub URL → local consulting-co path
    if "github.com/gblack686/consulting-co" in source:
        # Extract path after /blob/main/ or /tree/main/
        m = re.search(r"/(blob|tree)/main/(.+)", source)
        if m:
            rel = m.group(2)
            local = CONSULTING_CO / rel
            if local.exists():
                return local
            # For tree URLs (expert dirs), look for expertise.yaml
            if m.group(1) == "tree":
                ey = local / "expertise.yaml"
                if ey.exists():
                    return ey
    # Home-relative paths
    if source.startswith("~/"):
        expanded = HOME / source[2:]
        if expanded.exists():
            return expanded
    # Absolute paths
    p = Path(source)
    if p.exists():
        return p
    return None


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_str = content[3:end].strip()
    body = content[end + 3:].strip()
    try:
        fm = yaml.safe_load(fm_str) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def read_entry_content(source: str, entry_type: str) -> tuple[dict, str]:
    """Read and parse an entry's source file. Returns (frontmatter, body)."""
    path = resolve_source(source, entry_type)
    if path is None:
        return {}, ""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return extract_frontmatter(content)
    except Exception:
        return {}, ""


def process_catalog(catalog: dict) -> list[dict]:
    entries = []
    for entry_type, items in [
        ("skill", catalog.get("skills", [])),
        ("agent", catalog.get("agents", [])),
        ("prompt", catalog.get("prompts", [])),
    ]:
        for item in items:
            name = item["name"]
            desc = item.get("description", "")
            source = item.get("source", "")
            approved = item.get("approved", False)
            usage = item.get("usage", "rare")

            fm, body = read_entry_content(source, entry_type)

            # Truncate body to first ~2000 chars for the viewer
            if len(body) > 2000:
                body = body[:2000] + "\n\n*... (truncated)*"

            entries.append({
                "name": name,
                "description": desc,
                "source": source,
                "approved": approved,
                "usage": usage,
                "type": entry_type,
                "category": assign_category(name, desc),
                "color": assign_color(name, desc),
                "frontmatter": fm,
                "body": body,
            })
    return entries


def remove_entry(name: str, dry_run: bool = False):
    """Remove an entry from library.yaml, its skill directory, and Obsidian notes."""
    import shutil

    def force_rm(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if not LIBRARY_YAML.exists():
        print(f"ERROR: {LIBRARY_YAML} not found", file=sys.stderr)
        sys.exit(1)

    with open(LIBRARY_YAML, encoding="utf-8") as f:
        raw = f.read()

    # Find and remove the YAML block for this entry
    # Match: "    - name: {name}\n      ...\n" until next "    - name:" or end of section
    pattern = rf'(    - name: {re.escape(name)}\n(?:      [^\n]+\n)*)'
    match = re.search(pattern, raw)
    if not match:
        print(f"Entry '{name}' not found in library.yaml")
        sys.exit(1)

    print(f"Found in library.yaml:\n{match.group(0)}")

    # Skill directory
    skill_dir = CONSULTING_CO / f".claude/skills/{name}"
    agent_file = CONSULTING_CO / f".claude/agents/{name}.md"

    # Obsidian notes
    vault = Path("C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB")
    obsidian_paths = [
        vault / f"skills/{name}",
        vault / f"agents/{name}.md",
        vault / f"commands/{name}.md",
        vault / f"03-Skills/{name}.md",
    ]

    if dry_run:
        print(f"\n--dry-run: would remove:")
        print(f"  library.yaml entry: {name}")
        if skill_dir.exists(): print(f"  skill dir: {skill_dir}")
        if agent_file.exists(): print(f"  agent file: {agent_file}")
        for p in obsidian_paths:
            if p.exists(): print(f"  obsidian: {p}")
        return

    # Remove from library.yaml
    updated = raw[:match.start()] + raw[match.end():]
    with open(LIBRARY_YAML, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Removed '{name}' from library.yaml")

    # Remove skill/agent directory
    if skill_dir.exists():
        shutil.rmtree(str(skill_dir), onexc=force_rm)
        print(f"Deleted {skill_dir}")
    if agent_file.exists():
        os.remove(str(agent_file))
        print(f"Deleted {agent_file}")

    # Remove Obsidian notes
    for p in obsidian_paths:
        if p.is_dir():
            shutil.rmtree(str(p), onexc=force_rm)
            print(f"Deleted {p}")
        elif p.is_file():
            os.remove(str(p))
            print(f"Deleted {p}")


def main():
    parser = argparse.ArgumentParser(description="Sync library.yaml → library-catalog.json")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing")
    parser.add_argument("--output", type=Path, default=ARCHON_PUBLIC / "library-catalog.json")
    parser.add_argument("--remove", type=str, metavar="NAME", help="Remove an entry by name from library.yaml + disk + Obsidian")
    args = parser.parse_args()

    if args.remove:
        remove_entry(args.remove, dry_run=args.dry_run)
        if not args.dry_run:
            # Re-sync after removal
            print("\nRe-syncing catalog...")
        else:
            return

    if not LIBRARY_YAML.exists():
        print(f"ERROR: {LIBRARY_YAML} not found", file=sys.stderr)
        sys.exit(1)

    with open(LIBRARY_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    library = data.get("library", {})
    entries = process_catalog(library)

    # Stats
    categories = {}
    resolved = 0
    for e in entries:
        categories[e["category"]] = categories.get(e["category"], 0) + 1
        if e["body"]:
            resolved += 1

    print(f"Processed {len(entries)} entries ({resolved} with content)")
    print(f"Categories:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    if args.dry_run:
        print("\n--dry-run: no files written")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"entries": entries, "synced_at": __import__("datetime").datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
