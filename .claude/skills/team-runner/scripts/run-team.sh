#!/bin/bash
# run-team.sh — Execute a team-spec.yaml on Mac Mini through the Meridian pipeline
# Called by the team-runner skill after spec approval
#
# Usage: run-team.sh <spec-file> [--dry-run]
set -euo pipefail

SPEC="$1"
DRY_RUN="${2:-}"
MAC="greg@100.88.4.114"
EMPIRE="http://127.0.0.1:8800"
AUTH="Authorization: Bearer eagle-empire-2026"

# Parse spec with Python (works on Windows)
parse() { python -c "import yaml,sys; d=yaml.safe_load(open('$SPEC')); exec(sys.argv[1])" "$1"; }

PROJECT_NAME=$(parse "print(d['project']['name'])")
PROJECT_PATH=$(parse "print(d['project']['path'])")
TEAM_TYPE=$(parse "print(d['team_type'])")
STRATEGY=$(parse "print(d['execution']['strategy'])")

echo "=== Team Runner ==="
echo "Project: $PROJECT_NAME ($PROJECT_PATH)"
echo "Type:    $TEAM_TYPE"
echo "Strategy: $STRATEGY"
echo

if [ "$DRY_RUN" = "--dry-run" ]; then
  echo "[DRY RUN] Would execute on Mac Mini. Exiting."
  exit 0
fi

# ── Phase 2: Create Claw Empire agents ──
echo "[Phase 2] Creating Claw Empire agents..."

DEPT_ID=$(parse "print(d['department']['id'])")
DEPT_NAME=$(parse "print(d['department']['name'])")
DEPT_ICON=$(parse "print(d['department']['icon'])")
DEPT_COLOR=$(parse "print(d['department']['color'])")

# Create department
ssh "$MAC" "curl -s -X POST -H '$AUTH' -H 'Content-Type: application/json' \
  '$EMPIRE/api/departments' \
  -d '{\"id\":\"$DEPT_ID\",\"name\":\"$DEPT_NAME\",\"name_ko\":\"$DEPT_NAME\",\"icon\":\"$DEPT_ICON\",\"color\":\"$DEPT_COLOR\",\"sort_order\":0}'" > /dev/null 2>&1 || true

# Create agents and collect IDs (idempotent — skips existing agents)
# Use Windows-compatible path for Python (MSYS /c/ paths don't work in Windows Python)
AGENT_IDS_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -W)/.agent-ids-tmp.json"
python -c "
import yaml, json, subprocess, sys

spec = yaml.safe_load(open('$SPEC'))
dept_id = spec['department']['id']

# Fetch existing agents to avoid duplicates
existing = {}
result = subprocess.run(
    ['ssh', '$MAC', \"curl -s -H '$AUTH' '$EMPIRE/api/agents'\"],
    capture_output=True, text=True
)
try:
    agents_resp = json.loads(result.stdout)
    for a in agents_resp.get('agents', agents_resp if isinstance(agents_resp, list) else []):
        if a.get('department_id') == dept_id:
            existing[a['name']] = a['id']
except:
    pass

ids = {}
for agent in spec['agents']:
    name = agent['name']
    role = agent.get('role', 'senior')
    avatar = agent.get('avatar', '🤖')
    personality = agent.get('personality', '')

    # Skip if agent already exists in this department
    if name in existing:
        ids[name] = existing[name]
        print(f'  Exists:  {name} -> {existing[name][:8]}')
        continue

    data = json.dumps({
        'name': name, 'name_ko': name,
        'department_id': dept_id, 'role': role,
        'cli_provider': 'claude', 'avatar_emoji': avatar,
        'personality': personality
    })

    result = subprocess.run(
        ['ssh', '$MAC', f\"curl -s -X POST -H '$AUTH' -H 'Content-Type: application/json' '$EMPIRE/api/agents' -d '{data}'\"],
        capture_output=True, text=True
    )
    try:
        resp = json.loads(result.stdout)
        aid = resp.get('agent', {}).get('id', '')
        ids[name] = aid
        print(f'  Created: {name} -> {aid[:8]}')
    except:
        print(f'  Warning: {name} creation failed')

with open('$AGENT_IDS_FILE', 'w') as f:
    json.dump(ids, f)
    f.flush()
"

echo

# ── Phase 3: Run Team ──
echo "[Phase 3] Running team on Mac Mini..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/run-phase3.py" "$SPEC" "$AGENT_IDS_FILE"

echo
echo "[Phase 4] Committing and reporting..."

# Commit on Mac Mini
ssh "$MAC" "export PATH='/opt/homebrew/bin:/usr/bin:/bin:\$PATH'; cd $PROJECT_PATH && git add -A && git commit -m 'team-runner: $TEAM_TYPE run for $PROJECT_NAME' 2>&1 || echo 'nothing to commit'"

# Wiki log
DATE=$(date +%Y-%m-%d)
WIKI_ENTRY="## $DATE - $PROJECT_NAME / $TEAM_TYPE\n- Spec: $SPEC\n- Strategy: $STRATEGY\n- Agents: $(parse "print(len(d['agents']))")\n"
ssh "$MAC" "echo -e '$WIKI_ENTRY' >> ~/repos/wiki/team-runs.md 2>/dev/null || true"

echo
echo "=== Team Runner Complete ==="
rm -f "$AGENT_IDS_FILE"
