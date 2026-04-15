#!/usr/bin/env python
"""
graphify-sync: Scan all client repos on Mac Mini, detect changes since last
graphify run, and re-run `graphify . --update` on repos with new/modified files.

Usage:
    python graphify_sync.py                # scan all, update changed repos
    python graphify_sync.py --repo X       # single repo
    python graphify_sync.py --force        # re-graphify all regardless of changes
    python graphify_sync.py --dry-run      # show what would change, don't run
    python graphify_sync.py --list         # show repo registry and last-run status
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config" / "repos.json"
STATE_DIR = SKILL_DIR / "state"
STATE_DIR.mkdir(exist_ok=True)

# Add consulting-admin to path for Drive imports
CONSULTING_ADMIN = Path(__file__).parent.parent.parent / "consulting-admin"
sys.path.insert(0, str(CONSULTING_ADMIN))


def load_config():
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def ssh(host, cmd, timeout=30):
    """Run a command on Mac Mini via SSH, return stdout."""
    full = f"export PATH='/opt/homebrew/bin:/usr/bin:/bin:$PATH'; {cmd}"
    r = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=10", host, full],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.stdout.strip(), r.returncode


def get_file_manifest(host, repo_path):
    """Get {path: mtime} for all tracked files in a repo via SSH."""
    cmd = (
        f"cd {repo_path} && "
        f"find . -not -path './.git/*' -not -path './node_modules/*' "
        f"-not -path './graphify-out/*' -not -path './.obsidian/*' "
        f"-type f -exec stat -f '%m %N' {{}} \\;"
    )
    out, rc = ssh(host, cmd, timeout=30)
    if rc != 0:
        return None
    manifest = {}
    for line in out.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            manifest[parts[1]] = int(parts[0])
    return manifest


def load_state(repo_id):
    """Load last-known file manifest for a repo."""
    state_file = STATE_DIR / f"{repo_id}.json"
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {"manifest": {}, "last_run": None, "last_run_files": 0}


def save_state(repo_id, manifest, file_count):
    state_file = STATE_DIR / f"{repo_id}.json"
    state_file.write_text(json.dumps({
        "manifest": manifest,
        "last_run": datetime.now(timezone.utc).isoformat(),
        "last_run_files": file_count,
    }, indent=2), encoding="utf-8")


def list_drive_folder_recursive(drive, folder_id):
    """List all files in a Drive folder, recursing into subfolders."""
    files = []
    page_token = None
    while True:
        resp = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageSize=100,
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            if f["mimeType"] == "application/vnd.google-apps.folder":
                files.extend(list_drive_folder_recursive(drive, f["id"]))
            else:
                files.append(f)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def drive_sync(repo_id, folder_id, ssh_host, repo_path, dry_run=False):
    """Sync Google Drive folder to {repo_path}/drive-mirror/ on Mac Mini.
    Returns count of new/changed files."""
    try:
        from scripts import google_client, drive_manager
    except ImportError:
        print("    WARNING: consulting-admin not importable, skipping Drive sync")
        return 0

    drive = google_client.drive_service()
    drive_files = list_drive_folder_recursive(drive, folder_id)

    # Load last Drive state
    drive_state_file = STATE_DIR / f"{repo_id}-drive.json"
    old_state = {}
    if drive_state_file.exists():
        old_state = json.loads(drive_state_file.read_text(encoding="utf-8")).get("files", {})

    # Diff
    changed = []
    for f in drive_files:
        fid = f["id"]
        old = old_state.get(fid)
        if not old or old.get("modifiedTime") != f.get("modifiedTime"):
            changed.append(f)

    if not changed:
        print(f"    Drive: {len(drive_files)} files, 0 changed")
        return 0

    print(f"    Drive: {len(drive_files)} files, {len(changed)} new/changed")
    for f in changed[:5]:
        print(f"      + {f['name']} ({f['mimeType'].split('.')[-1]})")
    if len(changed) > 5:
        print(f"      ... and {len(changed) - 5} more")

    if dry_run:
        return len(changed)

    # Ensure drive-mirror/ exists on Mac Mini
    ssh(ssh_host, f"mkdir -p {repo_path}/drive-mirror")

    # Export and upload each changed file
    for f in changed:
        safe_name = re.sub(r'[^\w\s-]', '', f["name"]).strip().replace(' ', '-').lower()
        if not safe_name:
            safe_name = f["id"][:8]
        dest = f"{repo_path}/drive-mirror/{safe_name}.md"

        try:
            text = drive_manager.export_doc_text(f["id"], f["mimeType"])
            if text and not text.startswith("["):
                # Upload via SSH
                # Escape for heredoc
                escaped = text.replace("\\", "\\\\").replace("'", "'\\''")
                cmd = f"cat > {dest} << 'DRIVEEOF'\n{text[:50000]}\nDRIVEOF"
                ssh(ssh_host, cmd, timeout=30)
                print(f"      Synced: {f['name']} -> {safe_name}.md")
        except Exception as e:
            print(f"      Error exporting {f['name']}: {e}")

    # Save new Drive state
    new_state = {f["id"]: {"name": f["name"], "modifiedTime": f.get("modifiedTime"), "mimeType": f["mimeType"]} for f in drive_files}
    drive_state_file.write_text(json.dumps({
        "files": new_state,
        "last_sync": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    return len(changed)


def diff_manifests(old_manifest, new_manifest):
    """Return added, modified, deleted file lists."""
    old_set = set(old_manifest.keys())
    new_set = set(new_manifest.keys())
    added = sorted(new_set - old_set)
    deleted = sorted(old_set - new_set)
    modified = sorted(
        f for f in old_set & new_set
        if old_manifest[f] != new_manifest[f]
    )
    return added, modified, deleted


def run_graphify(host, repo_path, flags, claude_env, timeout=600):
    """Run graphify --update on a repo via Claude Code on Mac Mini."""
    env_str = " ".join(f"{k}={v}" for k, v in claude_env.items())
    cmd = (
        f"cd {repo_path} && {env_str} "
        f"claude -p '/graphify . --update {flags}' --max-turns 30"
    )
    print(f"    Running graphify (this may take a few minutes)...")
    out, rc = ssh(host, cmd, timeout=timeout)
    return out, rc


def check_graphify_output(host, repo_path):
    """Check if graphify-out exists and get stats."""
    cmd = f"ls -la {repo_path}/graphify-out/graph.json {repo_path}/graphify-out/GRAPH_REPORT.md 2>&1"
    out, _ = ssh(host, cmd)
    has_graph = "graph.json" in out and "No such file" not in out
    return has_graph


def main():
    parser = argparse.ArgumentParser(description="graphify-sync: keep client knowledge graphs fresh")
    parser.add_argument("--repo", help="Run for a single repo only")
    parser.add_argument("--force", action="store_true", help="Re-graphify all repos regardless of changes")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without running graphify")
    parser.add_argument("--list", action="store_true", help="Show repo registry and status")
    args = parser.parse_args()

    config = load_config()
    host = config["mac_mini"]["host"]
    claude_env = config["mac_mini"]["claude_env"]

    if args.list:
        print(f"{'Repo':<20} {'Display':<25} {'Auto':<6} {'Last Run':<22} {'Has Graph'}")
        print("-" * 95)
        for repo_id, repo in config["repos"].items():
            state = load_state(repo_id)
            has_graph = check_graphify_output(host, repo["path"])
            last = state.get("last_run") or "never"
            if last != "never":
                last = last[:19].replace("T", " ")
            auto = "yes" if repo.get("auto_update", True) else "no"
            print(f"{repo_id:<20} {repo['display_name']:<25} {auto:<6} {last:<22} {'yes' if has_graph else 'no'}")
        return

    # Filter repos
    repos = config["repos"]
    if args.repo:
        if args.repo not in repos:
            print(f"Error: repo '{args.repo}' not in config. Available: {', '.join(repos.keys())}")
            sys.exit(1)
        repos = {args.repo: repos[args.repo]}

    print(f"graphify-sync — scanning {len(repos)} repo(s) on {host}")
    print()

    summary = []
    for repo_id, repo in repos.items():
        if not repo.get("auto_update", True) and not args.force:
            print(f"  [{repo_id}] skipped (auto_update=false)")
            summary.append((repo_id, "skipped", 0, 0, 0))
            continue

        print(f"  [{repo_id}] scanning {repo['path']}...")

        # Get current file manifest from Mac Mini
        current = get_file_manifest(host, repo["path"])
        if current is None:
            print(f"    ERROR: could not read repo (SSH failed or path missing)")
            summary.append((repo_id, "error", 0, 0, 0))
            continue

        # Diff against last state
        state = load_state(repo_id)
        old_manifest = state.get("manifest", {})
        added, modified, deleted = diff_manifests(old_manifest, current)
        total_changes = len(added) + len(modified) + len(deleted)

        print(f"    {len(current)} files | +{len(added)} added, ~{len(modified)} modified, -{len(deleted)} deleted")

        # Drive sync (if configured)
        drive_folder_id = repo.get("drive_folder_id")
        if drive_folder_id:
            drive_changes = drive_sync(repo_id, drive_folder_id, host, repo["path"], dry_run=args.dry_run)
            total_changes += drive_changes

        if total_changes == 0 and not args.force:
            print(f"    No changes — skipping graphify")
            # Still save state (updates timestamp)
            save_state(repo_id, current, len(current))
            summary.append((repo_id, "unchanged", len(added), len(modified), len(deleted)))
            continue

        if args.dry_run:
            if added:
                print(f"    Added: {', '.join(added[:5])}{'...' if len(added) > 5 else ''}")
            if modified:
                print(f"    Modified: {', '.join(modified[:5])}{'...' if len(modified) > 5 else ''}")
            if deleted:
                print(f"    Deleted: {', '.join(deleted[:5])}{'...' if len(deleted) > 5 else ''}")
            print(f"    [DRY RUN] Would run: graphify . --update {repo.get('graphify_flags', '')}")
            summary.append((repo_id, "dry-run", len(added), len(modified), len(deleted)))
            continue

        # Run graphify --update
        flags = repo.get("graphify_flags", "")
        out, rc = run_graphify(host, repo["path"], flags, claude_env)
        status = "updated" if rc == 0 else "failed"
        print(f"    graphify {status} (exit={rc})")

        # Save new state
        save_state(repo_id, current, len(current))
        summary.append((repo_id, status, len(added), len(modified), len(deleted)))

    # Summary table
    print()
    print(f"{'Repo':<20} {'Status':<12} {'Added':<8} {'Modified':<10} {'Deleted':<8}")
    print("-" * 60)
    for repo_id, status, a, m, d in summary:
        print(f"{repo_id:<20} {status:<12} {a:<8} {m:<10} {d:<8}")


if __name__ == "__main__":
    main()
