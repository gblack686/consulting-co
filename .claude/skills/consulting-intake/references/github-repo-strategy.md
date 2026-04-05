# GitHub Repo Strategy: Per-Client Repos

## Overview

Each client intake gets its own private GitHub repo under the `gbauto` org.

## Repo Naming Convention

```
gbauto/{client-project}
```

Examples:
```
gbauto/greg-trading
gbauto/erica-creations
gbauto/michael-fisch
```

The `YYYYMMDD` date lives in the internal `client-sessions/` folder name only —
repo names stay clean and readable.

---

## Repo Structure (per client)

```
{client-project}/
  main              ← delivered workspace (the actual client files)
  update/YYYYMMDD   ← future iterations (new features, improvements)
  fix/YYYYMMDD      ← deployed hotfixes
```

### `main` Branch Contents

```
openclaw-greg-trading/
├── workspace/           ← filled-in OpenClaw config
│   ├── SOUL.md
│   ├── USER.md
│   ├── IDENTITY.md
│   ├── MEMORY.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   ├── openclaw.json
│   ├── cron-setup.sh
│   └── skills/
│       └── {domain}/{workflow}/SKILL.md
├── experts/             ← domain expert systems (8 files each)
│   └── {domain}/
├── PACKAGE_SUMMARY.md
└── VALIDATION_REPORT.md
```

**NOT committed** (stays in `client-sessions/` locally only):
- `session_output/` — raw transcript data, client answers, internal notes
- `intake-answers.txt` — raw session transcript
- Any `.env`, `secrets.json`, `tokens.json`

---

## .gitignore

```
# Raw session data (internal only — never commit)
session_output/
intake-answers.txt
*.txt

# Secrets
.env
*.env
secrets.json
tokens.json

# OS
.DS_Store
Thumbs.db
__pycache__/
*.pyc
```

---

## Workflow: New Client Intake

```bash
REPO="gbauto/{client-project}"
SESSION_DIR="client-sessions/YYYYMMDD-{project}"

# 1. Create private repo
gh repo create "$REPO" \
  --private \
  --description "OpenClaw workspace — {client} ({date})"

# 2. Clone it
git clone "$(gh repo view "$REPO" --json url -q .url)" ~/{client-project}
cd ~/{client-project}

# 3. Copy deliverables (NOT session_output)
cp -r "$SESSION_DIR/workspace/"* workspace/
cp -r "$SESSION_DIR/experts/"* experts/
cp "$SESSION_DIR/PACKAGE_SUMMARY.md" .
cp "$SESSION_DIR/VALIDATION_REPORT.md" .

# 4. Commit and push to main
git add workspace/ experts/ PACKAGE_SUMMARY.md VALIDATION_REPORT.md
git commit -m "intake: YYYYMMDD {client} — {N} domains, score {score}/100"
git push -u origin main
```

---

## Workflow: Client Iteration

```bash
# Create an update branch
git checkout main
git checkout -b "update/20260315"

# Make changes, then push and open PR
git push -u origin "update/20260315"
gh pr create --base main --head "update/20260315" --title "[{client}] March update"
```

---

## Client Access

Each client gets invited as a collaborator (read-only) to their own repo:

```bash
gh api repos/gbauto/{client-project}/collaborators/{client-github} \
  --method PUT --field permission=pull
```

---

## Base Template Repo

`gbauto` org — all client repos live here as private repos.
Each client gets their own repo (e.g., `gbauto/greg-trading`).
Never mix client data across repos.

---

## Privacy Notes

- All client repos are **private** — never public
- `session_output/` never committed (contains raw client answers)
- API keys never committed — always env vars with `openclaw secret add`
- Repo descriptions are safe: domain count, score, date — no sensitive PII
