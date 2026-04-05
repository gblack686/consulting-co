"""Test the fixed matches_path_pattern function."""
from pathlib import Path


def matches_path_pattern(file_path: str, pattern: str) -> bool:
    fp = file_path.replace("\\", "/")
    pat = pattern.replace("\\", "/")
    if pat.startswith("~/"):
        home = str(Path.home()).replace("\\", "/")
        pat = home + pat[1:]
    if pat.startswith("*."):
        return fp.endswith(pat[1:])
    if pat.endswith("/"):
        seg = pat.rstrip("/")
        return ("/" + seg + "/") in ("/" + fp)
    basename = Path(fp).name
    return basename == pat or fp.endswith(pat)


# Should NOT match (build in filename, not a directory segment)
assert not matches_path_pattern(
    "C:/Users/gblac/.claude/skills/tac-scaffolding/templates/expert_plan_build_improve.md",
    "build/",
), "FALSE POSITIVE on build in filename"

# Should match (actual build/ directory)
assert matches_path_pattern("C:/project/build/output.js", "build/"), "Missed actual build/ dir"

# Should match (actual dist/ directory)
assert matches_path_pattern("C:/project/dist/bundle.js", "dist/"), "Missed actual dist/ dir"

# Should NOT match distribution.md
assert not matches_path_pattern("C:/project/distribution.md", "dist/"), "FALSE POSITIVE on dist in filename"

# Should still match node_modules
assert matches_path_pattern("C:/project/node_modules/foo/bar.js", "node_modules/"), "Missed node_modules/"

# Should still match .git
assert matches_path_pattern("C:/project/.git/config", ".git/"), "Missed .git/"

# Non-directory patterns
assert matches_path_pattern("C:/project/.env", ".env"), "Missed .env exact"
assert not matches_path_pattern("C:/project/.env.example", ".env"), "FALSE POSITIVE on .env.example"
assert matches_path_pattern("C:/project/package-lock.json", "package-lock.json"), "Missed package-lock.json"

print("All 9 tests passed!")
