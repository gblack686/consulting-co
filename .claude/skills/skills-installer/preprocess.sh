#!/usr/bin/env bash
# Skills Installer — Dynamic Injection Preprocessor
# Pre-loads session context into the prompt so Claude starts with full knowledge
# Usage: preprocess.sh <session-dir>
# Source concept: Leon van Zyl — "dynamic injection / preprocessing"

set -euo pipefail

SESSION_DIR="${1:?Usage: preprocess.sh <session-dir>}"

# Use python (Windows) or python3 (Unix)
PY=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "python")

echo "=== SKILLS INSTALLER: SESSION CONTEXT ==="
echo ""

# --- Client Profile ---
PROFILE="$SESSION_DIR/session_output/client_profile.json"
if [[ -f "$PROFILE" ]]; then
  echo "--- Client ---"
  "$PY" -c "
import json, sys, os
d = json.load(open(sys.argv[1]))
print(f'Name: {d.get(\"name\", d.get(\"client_name\", d.get(\"client\", \"Unknown\")))}')
print(f'Domain: {d.get(\"domain\", d.get(\"business_type\", \"Unknown\"))}')
print(f'Timezone: {d.get(\"timezone\", \"Unknown\")}')
contacts = d.get('contacts', d.get('associates', d.get('team', [])))
if isinstance(contacts, list) and contacts:
    names = [c.get('name', str(c)) if isinstance(c, dict) else str(c) for c in contacts]
    print(f'Contacts: {\", \".join(names)}')
" "$PROFILE" 2>&1 || echo "(client_profile.json parse error)"
  echo ""
fi

# --- Workflow Catalog Summary ---
CATALOG="$SESSION_DIR/session_output/workflow-catalog.json"
if [[ -f "$CATALOG" ]]; then
  echo "--- Workflow Catalog ---"
  "$PY" -c "
import json, sys
d = json.load(open(sys.argv[1]))
total = d.get('total_workflows', len(d.get('workflows', [])))
workflows = d.get('workflows', [])
phases = d.get('build_phases', [])
print(f'Total workflows: {total}')
if phases:
    for p in phases:
        wf_ids = p.get('workflows', [])
        print(f'  Phase {p[\"phase\"]} ({p[\"name\"]}): {\", \".join(wf_ids)} [sessions {p.get(\"sessions\", \"?\")}]')
high = [w for w in workflows if w.get('priority_score', 0) >= 8]
med = [w for w in workflows if 5 <= w.get('priority_score', 0) < 8]
low = [w for w in workflows if w.get('priority_score', 0) < 5]
print(f'Priority: {len(high)} high (8+), {len(med)} medium (5-7), {len(low)} low (<5)')
ideas = [w for w in workflows if w.get('status') == 'idea']
print(f'Status: {len(ideas)} ideas, {total - len(ideas)} other')
" "$CATALOG" 2>&1 || echo "(workflow-catalog.json parse error)"
  echo ""
fi

# --- Agents & Bindings from openclaw.json ---
OC="$SESSION_DIR/workspace/openclaw.json"
if [[ -f "$OC" ]]; then
  echo "--- Agents & Bindings ---"
  "$PY" -c "
import json, re, sys
raw = open(sys.argv[1]).read()
# Strip JSONC comments
raw = re.sub(r'//.*$', '', raw, flags=re.MULTILINE)
raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
# Fix unquoted keys (JSONC style: key: value -> "key": value)
raw = re.sub(r'(?m)^(\s*)([a-zA-Z_]\w*)(\s*:\s)', r'\1\"\2\"\3', raw)
# Also fix nested unquoted keys
raw = re.sub(r'(?<=[\{,])\s*([a-zA-Z_]\w*)\s*:', r' \"\1\":', raw)
# Remove trailing commas before } or ]
raw = re.sub(r',\s*([}\]])', r'\1', raw)
d = json.loads(raw)
agents = d.get('agents', {}).get('list', [])
bindings = d.get('bindings', [])
skills = d.get('skills', {}).get('entries', {})
print(f'Agents ({len(agents)}):')
for a in agents:
    emoji = a.get('identity', {}).get('emoji', '')
    model = a.get('model', 'default')
    model = model.split('/')[-1] if '/' in model else model
    dflt = ' [default]' if a.get('default') else ''
    print(f'  {a[\"id\"]}: {emoji} {a.get(\"name\", a[\"id\"])} ({model}){dflt}')
print()
print(f'Bindings ({len(bindings)}):')
for b in bindings:
    kw = ', '.join(b.get('on', []))
    print(f'  {b[\"from\"]} -> {b[\"to\"]}: [{kw}]')
print()
print(f'Registered skills ({len(skills)}):')
for name, cfg in skills.items():
    inv = ' [user_invocable]' if cfg.get('user_invocable') else ''
    en = 'enabled' if cfg.get('enabled', True) else 'disabled'
    print(f'  {name}: {en}{inv}')
" "$OC" 2>&1 || echo "(openclaw.json parse error)"
  echo ""
fi

# --- Existing Skill Files ---
SKILLS_DIR="$SESSION_DIR/workspace/skills"
if [[ -d "$SKILLS_DIR" ]]; then
  echo "--- Existing SKILL.md Files ---"
  find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | sort | while read -r f; do
    rel="${f#$SESSION_DIR/}"
    echo "  $rel"
  done
  count=$(find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
  echo "  Total: $count skill files"
else
  echo "--- Existing SKILL.md Files ---"
  echo "  (none -- workspace/skills/ directory does not exist)"
fi

echo ""
echo "=== END SESSION CONTEXT ==="
