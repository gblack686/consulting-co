#!/usr/bin/env python3
"""Skill Discovery — scan .claude/skills/ and generate capability indexes."""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

# Pipeline phase keywords (from references/pipeline-taxonomy.md)
PHASES = {
    "Prospect": ["linkedin", "prospect", "recon", "social", "research", "intel", "outreach"],
    "Onboard": ["onboard", "welcome", "admin", "email", "drive", "folder", "deck", "setup", "new-client"],
    "Discover": ["discover", "question", "intake", "interview", "workflow", "ideator", "transcript"],
    "Build": ["build", "scaffold", "agent", "skill", "code", "repo", "workspace", "template"],
    "Deploy": ["deploy", "github-actions", "ci", "cd", "lightsail", "openclaw", "production"],
    "Monitor": ["monitor", "heartbeat", "inbox", "log", "sync", "graphify", "daily", "scan", "watch"],
    "Grow": ["grow", "proposal", "upsell", "expand", "renew", "report"],
}

META_KEYWORDS = ["meta", "discovery", "inventory", "scan", "index", "archive", "sync", "knowledge"]
OPS_KEYWORDS = ["cost", "budget", "billing", "infrastructure", "secret", "credential"]


def find_skills_root():
    """Find .claude/skills/ relative to git root or cwd."""
    # Try git root first
    git_root = os.popen("git rev-parse --show-toplevel 2>/dev/null").read().strip()
    if git_root:
        skills = os.path.join(git_root, ".claude", "skills")
        if os.path.isdir(skills):
            return skills
    # Fallback: walk up from cwd
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        skills = parent / ".claude" / "skills"
        if skills.is_dir():
            return str(skills)
    return None


def parse_frontmatter(path):
    """Extract YAML frontmatter from a SKILL.md file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    # Match YAML frontmatter
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {"name": "", "description": ""}

    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            fm[key] = val
    return fm


def classify_phase(name, description):
    """Classify a skill into a pipeline phase based on keywords."""
    text = f"{name} {description}".lower()

    # Check meta/ops first (cross-cutting)
    meta_score = sum(1 for kw in META_KEYWORDS if kw in text)
    ops_score = sum(1 for kw in OPS_KEYWORDS if kw in text)

    best_phase = "Meta"
    best_score = meta_score

    if ops_score > best_score:
        best_phase = "Operations"
        best_score = ops_score

    for phase, keywords in PHASES.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_phase = phase
            best_score = score

    return best_phase


def discover_skills(skills_root):
    """Scan all SKILL.md files and return structured skill data."""
    skills = []
    for skill_md in sorted(glob.glob(os.path.join(skills_root, "*", "SKILL.md"))):
        skill_dir = os.path.basename(os.path.dirname(skill_md))
        fm = parse_frontmatter(skill_md)
        if fm is None:
            continue

        name = fm.get("name", skill_dir)
        desc = fm.get("description", "")
        # Clean up description
        desc = desc.strip('"').strip("'")
        # Truncate long descriptions for table display
        short_desc = desc[:80] + "..." if len(desc) > 80 else desc

        trigger = f"/{name}" if name else f"/{skill_dir}"
        phase = classify_phase(name, desc)

        skills.append({
            "name": name,
            "dir": skill_dir,
            "trigger": trigger,
            "phase": phase,
            "description": desc,
            "short_description": short_desc,
        })

    return skills


def generate_skills_index(skills):
    """Generate skills-index.md content."""
    from datetime import date
    lines = [
        "---",
        "type: capability-index",
        "title: Skills Index",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        "# Skills Index",
        "",
        f"All consulting pipeline skills available in `consulting-co/.claude/skills/`.",
        "",
        "| Skill | Trigger | Phase | Description |",
        "|-------|---------|-------|-------------|",
    ]
    for s in sorted(skills, key=lambda x: (x["phase"], x["name"])):
        lines.append(f"| {s['name']} | `{s['trigger']}` | {s['phase']} | {s['short_description']} |")

    lines.append("")
    lines.append("> Auto-generated. Run `/skill-discovery` to refresh.")
    lines.append("")
    return "\n".join(lines)


def generate_pipeline_map(skills):
    """Generate pipeline-map.md content."""
    from datetime import date
    phase_order = ["Prospect", "Onboard", "Discover", "Build", "Deploy", "Monitor", "Grow"]
    cross_cutting = ["Meta", "Operations"]

    lines = [
        "---",
        "type: capability-index",
        "title: Pipeline Map",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        "# Consulting Pipeline Map",
        "",
        "Skills mapped to the 7-phase consulting lifecycle.",
        "",
    ]

    for phase in phase_order:
        phase_skills = [s for s in skills if s["phase"] == phase]
        lines.append(f"## {phase}")
        lines.append("")
        if phase_skills:
            lines.append("| Skill | Trigger | Description |")
            lines.append("|-------|---------|-------------|")
            for s in phase_skills:
                lines.append(f"| {s['name']} | `{s['trigger']}` | {s['short_description']} |")
        else:
            lines.append("_No skills mapped to this phase yet._")
        lines.append("")

    # Cross-cutting
    lines.append("## Cross-Cutting Skills")
    lines.append("")
    for cat in cross_cutting:
        cat_skills = [s for s in skills if s["phase"] == cat]
        if cat_skills:
            lines.append(f"### {cat}")
            lines.append("")
            lines.append("| Skill | Trigger | Description |")
            lines.append("|-------|---------|-------------|")
            for s in cat_skills:
                lines.append(f"| {s['name']} | `{s['trigger']}` | {s['short_description']} |")
            lines.append("")

    lines.append("> Auto-generated. Run `/skill-discovery` to refresh.")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Discover and index consulting pipeline skills")
    parser.add_argument("--output", "-o", help="Path to capabilities/ folder to write output")
    parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="Output format")
    parser.add_argument("--skills-root", help="Path to .claude/skills/ (auto-detected if omitted)")
    args = parser.parse_args()

    skills_root = args.skills_root or find_skills_root()
    if not skills_root or not os.path.isdir(skills_root):
        print("Error: Could not find .claude/skills/ directory", file=sys.stderr)
        sys.exit(1)

    skills = discover_skills(skills_root)
    print(f"Found {len(skills)} skills in {skills_root}", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(skills, indent=2))
        return

    index_content = generate_skills_index(skills)
    map_content = generate_pipeline_map(skills)

    if args.output:
        os.makedirs(args.output, exist_ok=True)
        index_path = os.path.join(args.output, "skills-index.md")
        map_path = os.path.join(args.output, "pipeline-map.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)
        with open(map_path, "w", encoding="utf-8") as f:
            f.write(map_content)
        print(f"Wrote {index_path}", file=sys.stderr)
        print(f"Wrote {map_path}", file=sys.stderr)
    else:
        print("# === skills-index.md ===")
        print(index_content)
        print("\n# === pipeline-map.md ===")
        print(map_content)


if __name__ == "__main__":
    main()
