#!/bin/bash
# repo-setup.sh — Step 5a: GitHub Repo Setup for 20260221-greg-trading
#
# Run from: client-sessions/20260221-greg-trading/
# Requires: gh CLI authenticated, git configured
#
# What this does:
#   1. Creates private repo gblack686/openclaw-greg-trading
#   2. Clones it locally
#   3. Copies workspace + experts (NOT session_output)
#   4. Commits and pushes to main
#   5. Invites client as collaborator (optional)

set -e

REPO="gblack686/openclaw-greg-trading"
SESSION_DIR="$(pwd)"
CLONE_DIR="$HOME/openclaw-greg-trading"
COMMIT_MSG="intake: 20260221 greg-trading — 4 domains, score 94/100"

# ── Step 1: Check / create repo ──────────────────────────────────────────────
echo "Checking for $REPO on GitHub..."
if ! gh repo view "$REPO" &>/dev/null; then
  echo "Creating $REPO..."
  gh repo create "$REPO" \
    --private \
    --description "OpenClaw workspace — Greg trading (2026-02-21)"
  echo "✅ Repo created: https://github.com/$REPO"
else
  echo "✅ Repo $REPO already exists"
fi

# ── Step 2: Clone ─────────────────────────────────────────────────────────────
REPO_URL=$(gh repo view "$REPO" --json url -q .url)

if [ ! -d "$CLONE_DIR/.git" ]; then
  echo "Cloning $REPO to $CLONE_DIR..."
  git clone "$REPO_URL" "$CLONE_DIR"
fi

cd "$CLONE_DIR"

# Initialize main if repo is empty
if ! git show-ref --verify --quiet "refs/remotes/origin/main" 2>/dev/null && \
   ! git show-ref --verify --quiet "refs/heads/main" 2>/dev/null; then
  echo "Initializing main branch..."
  git checkout -b main 2>/dev/null || git checkout main
else
  git fetch origin
  git checkout main
  git pull origin main 2>/dev/null || true
fi

echo "✅ On main branch"

# ── Step 3: Copy deliverables (NOT session_output) ───────────────────────────
echo "Copying workspace files..."
mkdir -p "$CLONE_DIR/workspace"
cp -r "$SESSION_DIR/workspace/"* "$CLONE_DIR/workspace/"

echo "Copying expert systems..."
mkdir -p "$CLONE_DIR/experts"
cp -r "$SESSION_DIR/experts/"* "$CLONE_DIR/experts/"

echo "Copying package docs..."
cp "$SESSION_DIR/PACKAGE_SUMMARY.md" "$CLONE_DIR/"
cp "$SESSION_DIR/VALIDATION_REPORT.md" "$CLONE_DIR/"

# ── Step 4: Stage and commit ──────────────────────────────────────────────────
cd "$CLONE_DIR"
git add workspace/ experts/ PACKAGE_SUMMARY.md VALIDATION_REPORT.md

# Verify nothing sensitive is staged
if git diff --cached --name-only | grep -E "(session_output|intake-answers|\.env|secrets|tokens)"; then
  echo "❌ ERROR: Sensitive files detected in staging area. Aborting."
  git reset HEAD
  exit 1
fi

if git diff --cached --quiet; then
  echo "Nothing new to commit — already up to date"
else
  git commit -m "$COMMIT_MSG"
  echo "✅ Committed: $COMMIT_MSG"
fi

# ── Step 5: Push ─────────────────────────────────────────────────────────────
git push -u origin main
echo "✅ Pushed to https://github.com/$REPO"

echo ""
echo "══════════════════════════════════════════════"
echo "✅ Step 5a Complete: GitHub Repo Setup"
echo "   Repo:  https://github.com/$REPO"
echo "   Clone: $CLONE_DIR"
echo ""
echo "Optional: invite client as collaborator"
echo "  gh api repos/$REPO/collaborators/{github-username} --method PUT --field permission=pull"
echo ""
echo "Next: Run Step 5b (local deploy)"
echo "  cp -r $CLONE_DIR/workspace/* ~/.openclaw/workspace/"
echo "  bash $SESSION_DIR/workspace/cron-setup.sh"
echo "══════════════════════════════════════════════"
