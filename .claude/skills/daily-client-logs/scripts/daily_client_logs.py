#!/usr/bin/env python
"""
daily-client-logs — scan client workspaces, diff vs last snapshot, write daily
activity logs into each client's second brain.

Usage:
    python daily_client_logs.py                 # all clients
    python daily_client_logs.py --client fisch-group
    python daily_client_logs.py --dry-run
    python daily_client_logs.py --list
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config" / "clients.json"
STATE_DIR = SKILL_DIR / "state"


# ---------- file walking ----------

def iter_files(root: Path, ignore: list[str]) -> Iterable[Path]:
    """Walk root, yielding files that don't match any ignore glob."""
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(_matches(rel, pat) for pat in ignore):
            continue
        yield path


def _matches(rel_path: str, pattern: str) -> bool:
    """Match pattern at any depth in rel_path.

    - Plain name (".git") matches any path segment.
    - Path pattern ("daily/*.md") matches any suffix of rel_path.
    - Glob ("*.pyc") matches the basename.
    """
    # 1. Full path fnmatch
    if fnmatch.fnmatch(rel_path, pattern):
        return True
    # 2. Basename fnmatch (handles "*.pyc", "~$*")
    if fnmatch.fnmatch(Path(rel_path).name, pattern):
        return True
    parts = rel_path.split("/")
    # 3. Plain directory/file name matches any segment
    if "/" not in pattern and not any(c in pattern for c in "*?["):
        if pattern in parts:
            return True
    # 4. Path pattern matches any suffix
    if "/" in pattern:
        for i in range(len(parts)):
            suffix = "/".join(parts[i:])
            if fnmatch.fnmatch(suffix, pattern):
                return True
    return False


def file_fingerprint(path: Path) -> dict:
    stat = path.stat()
    h = hashlib.sha1()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except OSError as e:
        return {"size": stat.st_size, "mtime": stat.st_mtime, "sha1": None, "error": str(e)}
    return {"size": stat.st_size, "mtime": stat.st_mtime, "sha1": h.hexdigest()}


# ---------- snapshot + diff ----------

@dataclass
class Snapshot:
    """client snapshot: key is abs path string, value is fingerprint dict"""
    files: dict[str, dict] = field(default_factory=dict)
    generated_at: str = ""


def build_snapshot(workspaces: list[str], ignore: list[str]) -> Snapshot:
    snap = Snapshot(generated_at=datetime.now().isoformat(timespec="seconds"))
    for ws in workspaces:
        root = Path(ws).resolve()
        if not root.exists():
            print(f"  ! workspace not found: {root}", file=sys.stderr)
            continue
        for path in iter_files(root, ignore):
            key = str(path.resolve()).replace("\\", "/")
            snap.files[key] = file_fingerprint(path)
    return snap


def load_state(client: str) -> Snapshot:
    p = STATE_DIR / f"{client}.json"
    if not p.exists():
        return Snapshot()
    data = json.loads(p.read_text(encoding="utf-8"))
    return Snapshot(files=data.get("files", {}), generated_at=data.get("generated_at", ""))


def save_state(client: str, snap: Snapshot) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    p = STATE_DIR / f"{client}.json"
    p.write_text(
        json.dumps({"generated_at": snap.generated_at, "files": snap.files}, indent=2),
        encoding="utf-8",
    )


@dataclass
class Diff:
    added: list[str] = field(default_factory=list)
    modified: list[tuple[str, dict, dict]] = field(default_factory=list)  # (path, old, new)
    deleted: list[str] = field(default_factory=list)
    unchanged: int = 0

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.deleted)


def diff_snapshots(old: Snapshot, new: Snapshot) -> Diff:
    d = Diff()
    old_keys = set(old.files.keys())
    new_keys = set(new.files.keys())
    for key in sorted(new_keys - old_keys):
        d.added.append(key)
    for key in sorted(old_keys - new_keys):
        d.deleted.append(key)
    for key in sorted(old_keys & new_keys):
        o, n = old.files[key], new.files[key]
        if o.get("sha1") != n.get("sha1") or o.get("size") != n.get("size"):
            d.modified.append((key, o, n))
        else:
            d.unchanged += 1
    return d


# ---------- daily note writer ----------

def fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def relpath_for_display(abs_path: str, workspaces: list[str]) -> str:
    """Shorten an absolute path to {workspace_basename}/relative."""
    p = abs_path.replace("\\", "/")
    for ws in workspaces:
        ws_norm = str(Path(ws).resolve()).replace("\\", "/")
        if p.startswith(ws_norm + "/"):
            return f"{Path(ws).name}/{p[len(ws_norm) + 1:]}"
    return p


def render_daily_note(
    client_key: str,
    client_cfg: dict,
    snap: Snapshot,
    diff: Diff,
    date_str: str,
) -> str:
    display = client_cfg.get("display_name", client_key)
    workspaces = client_cfg["workspaces"]
    total = len(snap.files)
    lines = [
        "---",
        "type: daily",
        f"title: {display} — {date_str}",
        f"date: {date_str}",
        f"tags: [daily, {client_key}, auto]",
        "generated_by: daily-client-logs",
        "---",
        "",
        f"# {display} — {date_str}",
        "",
        f"**Workspaces scanned:** {len(workspaces)}",
        f"**Files tracked:** {total}",
        f"**Changes since last scan:** "
        f"{len(diff.added)} added · {len(diff.modified)} modified · {len(diff.deleted)} deleted",
        "",
    ]

    for ws in workspaces:
        lines.append(f"- `{ws}`")
    lines.append("")

    if not diff.has_changes and snap.generated_at:
        lines.append("## No changes")
        lines.append("")
        lines.append(f"{diff.unchanged} files unchanged since last scan.")
        lines.append("")
        return "\n".join(lines)

    if diff.added:
        lines.append(f"## Added ({len(diff.added)})")
        for key in diff.added:
            size = snap.files[key].get("size", 0)
            lines.append(f"- `{relpath_for_display(key, workspaces)}` ({fmt_size(size)})")
        lines.append("")

    if diff.modified:
        lines.append(f"## Modified ({len(diff.modified)})")
        for key, old, new in diff.modified:
            lines.append(
                f"- `{relpath_for_display(key, workspaces)}` — "
                f"was {fmt_size(old.get('size', 0))}, now {fmt_size(new.get('size', 0))}"
            )
        lines.append("")

    if diff.deleted:
        lines.append(f"## Deleted ({len(diff.deleted)})")
        for key in diff.deleted:
            lines.append(f"- `{relpath_for_display(key, workspaces)}`")
        lines.append("")

    lines.append(f"## Unchanged")
    lines.append(f"{diff.unchanged} files unchanged since last scan.")
    lines.append("")
    return "\n".join(lines)


def write_daily_note(second_brain: Path, client_key: str, content: str, date_str: str) -> Path:
    daily_dir = second_brain / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    out = daily_dir / f"{date_str}.md"
    # If a note already exists for today, append a run separator
    if out.exists():
        existing = out.read_text(encoding="utf-8")
        content = existing.rstrip() + "\n\n---\n\n" + content
    out.write_text(content, encoding="utf-8")
    return out


# ---------- main ----------

def load_clients() -> dict:
    if not CONFIG_PATH.exists():
        print(f"config not found: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(2)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def run_client(client_key: str, cfg: dict, dry_run: bool) -> None:
    display = cfg.get("display_name", client_key)
    print(f"\n=== {display} ({client_key}) ===")
    workspaces = cfg["workspaces"]
    ignore = cfg.get("ignore", [])
    second_brain = Path(cfg["second_brain"]).resolve()

    if not second_brain.exists():
        print(f"  ! second_brain not found: {second_brain}", file=sys.stderr)
        return

    print(f"  scanning {len(workspaces)} workspace(s)...")
    new_snap = build_snapshot(workspaces, ignore)
    old_snap = load_state(client_key)
    diff = diff_snapshots(old_snap, new_snap)

    print(
        f"  files: {len(new_snap.files)} "
        f"(+{len(diff.added)} ~{len(diff.modified)} -{len(diff.deleted)})"
    )

    date_str = datetime.now().strftime("%Y-%m-%d")
    content = render_daily_note(client_key, cfg, new_snap, diff, date_str)

    if dry_run:
        print(f"  [dry-run] would write daily note ({len(content)} chars)")
        print(f"  [dry-run] would save state with {len(new_snap.files)} entries")
        return

    out_path = write_daily_note(second_brain, client_key, content, date_str)
    save_state(client_key, new_snap)
    print(f"  wrote: {out_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Diff client workspaces and log to second brain")
    ap.add_argument("--client", help="Run only this client key (from clients.json)")
    ap.add_argument("--dry-run", action="store_true", help="Don't write anything")
    ap.add_argument("--list", action="store_true", help="List configured clients and exit")
    args = ap.parse_args()

    clients = load_clients()

    if args.list:
        print("Configured clients:")
        for key, cfg in clients.items():
            name = cfg.get("display_name", key)
            wc = len(cfg.get("workspaces", []))
            sb = cfg.get("second_brain", "?")
            print(f"  - {key}  ({name})  — {wc} workspace(s) → {sb}")
        return 0

    if args.client:
        if args.client not in clients:
            print(f"unknown client: {args.client}", file=sys.stderr)
            return 2
        run_client(args.client, clients[args.client], args.dry_run)
    else:
        for key, cfg in clients.items():
            run_client(key, cfg, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
