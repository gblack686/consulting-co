"""TAC Component Inventory, Gap Analysis, and Global Sync."""
import os
import shutil
import sys

try:
    import yaml
except ImportError:
    yaml = None


def _parse_yaml_simple(path):
    """Parse the global-manifest.yaml without PyYAML dependency.

    Handles our simple format: top-level keys with list items (- value).
    """
    if yaml:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    result = {}
    current_key = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not line.startswith(" ") and not line.startswith("\t") and stripped.endswith(":"):
                current_key = stripped[:-1]
                result[current_key] = []
            elif stripped.startswith("- ") and current_key is not None:
                result[current_key].append(stripped[2:].strip())
    return result


def _global_home():
    """Return the global ~/.claude/ directory."""
    return os.path.join(os.path.expanduser("~"), ".claude")


# Map manifest keys to subdirectory paths within a .claude/ root
_COMPONENT_PATHS = {
    "agents": "agents",
    "experts": os.path.join("commands", "experts"),
    "skills": "skills",
    "commands": "commands",
}

# Components that are files (name.md) vs directories
_FILE_COMPONENTS = {"agents", "commands"}
_DIR_COMPONENTS = {"experts", "skills"}


def _resolve_source_path(base, kind, name):
    """Resolve the full path for a component in a .claude/ tree."""
    sub = _COMPONENT_PATHS[kind]
    full = os.path.join(base, sub, name)
    # agents and commands are .md files
    if kind in _FILE_COMPONENTS:
        md = full + ".md"
        if os.path.isfile(md):
            return md
        if os.path.isfile(full):
            return full
        return md  # return expected path even if missing
    return full


def _copy_component(src, dst):
    """Copy a file or directory from src to dst, merging into existing dirs."""
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    elif os.path.isfile(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)


def sync_to_global(claude_dir, manifest_path):
    """Push manifest-listed components from project .claude/ to ~/.claude/."""
    manifest = _parse_yaml_simple(manifest_path)
    global_dir = _global_home()
    copied = 0
    skipped = 0

    print("=" * 50)
    print("  Syncing to global ~/.claude/")
    print("=" * 50)

    for kind in ("agents", "experts", "skills", "commands"):
        items = manifest.get(kind, [])
        if not items:
            continue
        print(f"\n  {kind.title()}:")
        for name in items:
            src = _resolve_source_path(claude_dir, kind, name)
            dst = _resolve_source_path(global_dir, kind, name)
            if not os.path.exists(src):
                print(f"    SKIP {name} (not found in project)")
                skipped += 1
                continue
            os.makedirs(os.path.dirname(dst) if os.path.isfile(src) else os.path.dirname(dst),
                        exist_ok=True)
            _copy_component(src, dst)
            print(f"    OK   {name}")
            copied += 1

    print(f"\n  Done: {copied} synced, {skipped} skipped")


def sync_from_global(claude_dir, manifest_path):
    """Pull manifest-listed components from ~/.claude/ into project .claude/."""
    manifest = _parse_yaml_simple(manifest_path)
    global_dir = _global_home()
    copied = 0
    skipped = 0

    print("=" * 50)
    print("  Syncing from global ~/.claude/")
    print("=" * 50)

    for kind in ("agents", "experts", "skills", "commands"):
        items = manifest.get(kind, [])
        if not items:
            continue
        print(f"\n  {kind.title()}:")
        for name in items:
            src = _resolve_source_path(global_dir, kind, name)
            dst = _resolve_source_path(claude_dir, kind, name)
            if not os.path.exists(src):
                print(f"    SKIP {name} (not found in global)")
                skipped += 1
                continue
            os.makedirs(os.path.dirname(dst) if os.path.isfile(src) else os.path.dirname(dst),
                        exist_ok=True)
            _copy_component(src, dst)
            print(f"    OK   {name}")
            copied += 1

    print(f"\n  Done: {copied} synced, {skipped} skipped")


def sync_diff(claude_dir, manifest_path):
    """Show what would sync between project and global (dry-run)."""
    manifest = _parse_yaml_simple(manifest_path)
    global_dir = _global_home()

    print("=" * 50)
    print("  Sync Diff: project <-> global")
    print("=" * 50)

    for kind in ("agents", "experts", "skills", "commands"):
        items = manifest.get(kind, [])
        if not items:
            continue
        print(f"\n  {kind.title()}:")
        for name in items:
            proj = _resolve_source_path(claude_dir, kind, name)
            glob = _resolve_source_path(global_dir, kind, name)
            in_proj = os.path.exists(proj)
            in_glob = os.path.exists(glob)
            if in_proj and in_glob:
                status = "BOTH"
            elif in_proj:
                status = "PROJECT ONLY  -> sync-to-global"
            elif in_glob:
                status = "GLOBAL ONLY   -> sync-from-global"
            else:
                status = "MISSING"
            print(f"    {name:30s} {status}")


def inventory(agents_dir, experts_dir, skills_dir, commands_dir):
    agents = [f[:-3] for f in os.listdir(agents_dir) if f.endswith(".md")]
    experts = [
        d
        for d in os.listdir(experts_dir)
        if os.path.isdir(os.path.join(experts_dir, d))
    ]
    skills = [
        d
        for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d))
    ]
    commands = [f[:-3] for f in os.listdir(commands_dir) if f.endswith(".md")]
    print("=" * 44)
    print("  TAC Component Inventory")
    print("=" * 44)
    print("\n  Agents:")
    for a in sorted(agents):
        print(f"    {a}")
    print("\n  Expert Domains:")
    for e in sorted(experts):
        print(f"    {e}")
    print("\n  Skills:")
    for s in sorted(skills):
        print(f"    {s}")
    print("\n  Commands:")
    for c in sorted(commands):
        print(f"    {c}")
    print("\n" + "=" * 44)
    print(
        f"  Totals: {len(agents)} agents | {len(experts)} experts"
        f" | {len(skills)} skills | {len(commands)} commands"
    )


def gaps(agents_dir, experts_dir, skills_dir):
    agents = {f[:-3] for f in os.listdir(agents_dir) if f.endswith(".md")}
    experts = {
        d
        for d in os.listdir(experts_dir)
        if os.path.isdir(os.path.join(experts_dir, d))
    }
    skills = {
        d
        for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d))
    }
    print("  Component Gaps")
    print("=" * 44)
    print("\n  Agents without expert domains:")
    for a in sorted(agents - experts):
        print(f"    - {a}")
    print("\n  Expert domains without agents:")
    for e in sorted(experts - agents):
        print(f"    - {e}")
    print("\n  Skills without justfiles:")
    for s in sorted(skills):
        if not os.path.isfile(os.path.join(skills_dir, s, "justfile")):
            print(f"    - {s}")


def list_one(directory, kind, is_dir=False):
    print(f"  {kind}:\n")
    if is_dir:
        items = sorted(
            d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))
        )
    else:
        items = sorted(f[:-3] for f in os.listdir(directory) if f.endswith(".md"))
    for item in items:
        print(f"    {item}")


def _auto_claude_dir():
    """Derive claude_dir from this script's location (works with any path format)."""
    my_dir = os.path.dirname(os.path.abspath(__file__))  # .../skills/tac-scaffolding/
    return os.path.dirname(os.path.dirname(my_dir))       # .../.claude/


def _auto_dirs():
    """Return standard TAC directory paths derived from this script's location."""
    cd = _auto_claude_dir()
    return (
        os.path.join(cd, "agents"),
        os.path.join(cd, "commands", "experts"),
        os.path.join(cd, "skills"),
        os.path.join(cd, "commands"),
    )


if __name__ == "__main__":
    cmd = sys.argv[1]
    auto = "--auto" in sys.argv

    if cmd == "inventory":
        if auto:
            a, e, s, c = _auto_dirs()
            inventory(a, e, s, c)
        else:
            inventory(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "gaps":
        if auto:
            a, e, s, _ = _auto_dirs()
            gaps(a, e, s)
        else:
            gaps(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "list":
        if auto:
            kind = sys.argv[2]  # agents, experts, skills, commands
            a, e, s, c = _auto_dirs()
            dirs_map = {
                "agents": (a, "Agents", False),
                "experts": (e, "Expert Domains", True),
                "skills": (s, "Skills", True),
                "commands": (c, "Commands", False),
            }
            d, label, is_dir = dirs_map[kind]
            list_one(d, label, is_dir)
        else:
            is_dir = sys.argv[4] == "dir" if len(sys.argv) > 4 else False
            list_one(sys.argv[2], sys.argv[3], is_dir)
    elif cmd == "sync-to-global":
        if auto:
            cd = _auto_claude_dir()
            manifest = os.path.join(cd, "skills", "tac-scaffolding", "global-manifest.yaml")
            sync_to_global(cd, manifest)
        else:
            sync_to_global(sys.argv[2], sys.argv[3])
    elif cmd == "sync-from-global":
        if auto:
            cd = _auto_claude_dir()
            manifest = os.path.join(cd, "skills", "tac-scaffolding", "global-manifest.yaml")
            sync_from_global(cd, manifest)
        else:
            sync_from_global(sys.argv[2], sys.argv[3])
    elif cmd == "sync-diff":
        if auto:
            cd = _auto_claude_dir()
            manifest = os.path.join(cd, "skills", "tac-scaffolding", "global-manifest.yaml")
            sync_diff(cd, manifest)
        else:
            sync_diff(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
