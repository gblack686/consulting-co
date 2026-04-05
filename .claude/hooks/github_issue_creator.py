#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic",
# ]
# ///
"""
GitHub Issue Creator Hook

Post-hook that triggers on Stop events, analyzes the session for fixes,
and creates GitHub issues to track them for later review.

Triggers: Stop event
Purpose: Log/archive fixes, track vulnerabilities, get email notifications
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


# Configuration
SKILL_DIR = Path(__file__).parent.parent / "skills" / "github-issue-manager"
CONFIG_PATH = SKILL_DIR / "config" / "settings.json"
LOG_DIR = Path.home() / ".claude" / "logs"
LOG_FILE = LOG_DIR / "github_issue_debug.log"


def log_debug(message: str):
    """Log debug message to file."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def load_config() -> dict:
    """Load configuration from settings.json."""
    default_config = {
        "enabled": True,
        "default_repo": "gblack686/consulting-co",
        "default_labels": ["claude-code-fix"],
        "min_confidence": 0.7,
        "fix_types_to_track": ["bug_fix", "security_fix", "edge_case_fix"],
        "dry_run": False,
        "fix_keywords": ["fixed", "bug", "resolved", "patched", "corrected", "security", "vulnerability"]
    }

    try:
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            return {**default_config, **config}
    except Exception as e:
        log_debug(f"Error loading config: {e}")

    return default_config


def quick_fix_scan(text: str, keywords: list) -> bool:
    """
    Quick heuristic scan for fix indicators.
    Returns True if any keyword is found.
    """
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def analyze_with_haiku(user_message: str, assistant_message: str, config: dict) -> dict:
    """
    Use Claude Haiku to analyze if a real fix occurred.

    Returns:
        Dict with: is_fix, confidence, fix_type, summary, description, files_changed
    """
    try:
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            log_debug("No ANTHROPIC_API_KEY found")
            return {"is_fix": False, "confidence": 0}

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Analyze this Claude Code session to determine if a real code fix was made.

USER REQUEST:
{user_message[:2000]}

ASSISTANT RESPONSE:
{assistant_message[:3000]}

Analyze whether a real bug fix, security fix, or important code correction was made.
Ignore: documentation changes, test additions, new features, refactoring.
Focus on: actual bugs fixed, security vulnerabilities patched, error handling added for edge cases.

Return JSON only (no markdown):
{{
  "is_fix": true/false,
  "confidence": 0.0-1.0,
  "fix_type": "bug_fix" | "security_fix" | "edge_case_fix" | "other" | "none",
  "summary": "One-line summary of the fix (50 chars max)",
  "description": "2-3 sentence description of what was fixed and why",
  "files_changed": ["file1.py", "file2.ts"],
  "should_create_issue": true/false
}}"""

        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = response.content[0].text.strip()

        # Try to extract JSON from response
        if response_text.startswith("{"):
            result = json.loads(response_text)
        else:
            # Try to find JSON in response
            import re
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                log_debug(f"Could not parse Haiku response: {response_text[:200]}")
                return {"is_fix": False, "confidence": 0}

        log_debug(f"Haiku analysis: is_fix={result.get('is_fix')}, confidence={result.get('confidence')}")
        return result

    except Exception as e:
        log_debug(f"Haiku analysis error: {type(e).__name__}: {str(e)}")
        return {"is_fix": False, "confidence": 0}


def check_for_duplicates(repo: str, title: str, labels: list) -> list:
    """Check for existing similar issues."""
    try:
        # Use gh CLI to search for similar issues
        search_query = f"repo:{repo} is:issue is:open {title[:30]}"
        result = subprocess.run(
            ["gh", "search", "issues", "--limit", "5", "--json", "number,title,url", search_query],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0 and result.stdout:
            issues = json.loads(result.stdout)
            return issues
    except Exception as e:
        log_debug(f"Duplicate check error: {e}")

    return []


def create_github_issue(
    repo: str,
    title: str,
    body: str,
    labels: list,
    dry_run: bool = False
) -> tuple[bool, str]:
    """Create GitHub issue via gh CLI."""
    if dry_run:
        log_debug(f"DRY RUN - Would create issue: {title}")
        return True, "DRY_RUN"

    try:
        args = [
            "gh", "issue", "create",
            "--repo", repo,
            "--title", title,
            "--body", body
        ]

        for label in labels:
            args.extend(["--label", label])

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            issue_url = result.stdout.strip()
            log_debug(f"Created issue: {issue_url}")
            return True, issue_url
        else:
            log_debug(f"Failed to create issue: {result.stderr}")
            return False, result.stderr

    except Exception as e:
        log_debug(f"Create issue error: {type(e).__name__}: {str(e)}")
        return False, str(e)


def format_issue_body(analysis: dict, session_id: str = None) -> str:
    """Generate formatted issue body."""
    fix_type = analysis.get("fix_type", "unknown").replace("_", " ").title()
    confidence = int(analysis.get("confidence", 0) * 100)
    description = analysis.get("description", "No description available")
    files = analysis.get("files_changed", [])

    body = f"""## Fix Applied During Claude Code Session

**Type**: {fix_type}
**Confidence**: {confidence}%

### Description
{description}

"""

    if files:
        body += "### Files Changed\n"
        for f in files[:10]:  # Limit to 10 files
            body += f"- `{f}`\n"
        body += "\n"

    if session_id:
        body += f"**Session ID**: `{session_id}`\n\n"

    body += f"**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    body += "---\n*Auto-generated by Claude Code GitHub Issue Hook*"

    return body


def main():
    """Main hook entry point."""
    try:
        log_debug("=" * 50)
        log_debug("GitHub Issue Creator Hook triggered")

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")

        log_debug(f"Session ID: {session_id}")

        # Load config
        config = load_config()

        if not config.get("enabled", True):
            log_debug("Hook disabled via config")
            sys.exit(0)

        # Extract messages from input
        user_message = input_data.get("user_message", "")
        assistant_message = input_data.get("assistant_message", "")

        if not user_message and not assistant_message:
            log_debug("No messages found in input, skipping")
            sys.exit(0)

        # Quick heuristic scan
        combined_text = f"{user_message} {assistant_message}"
        fix_keywords = config.get("fix_keywords", ["fixed", "bug", "resolved"])

        if not quick_fix_scan(combined_text, fix_keywords):
            log_debug("No fix indicators found in quick scan")
            sys.exit(0)

        log_debug("Fix indicators detected, calling Haiku for analysis")

        # Analyze with Haiku
        analysis = analyze_with_haiku(user_message, assistant_message, config)

        # Check if we should create an issue
        is_fix = analysis.get("is_fix", False)
        confidence = analysis.get("confidence", 0)
        fix_type = analysis.get("fix_type", "none")
        should_create = analysis.get("should_create_issue", False)

        min_confidence = config.get("min_confidence", 0.7)
        tracked_types = config.get("fix_types_to_track", ["bug_fix", "security_fix"])

        log_debug(f"Analysis: is_fix={is_fix}, conf={confidence}, type={fix_type}, should_create={should_create}")

        if not is_fix:
            log_debug("Not identified as a fix")
            sys.exit(0)

        if confidence < min_confidence:
            log_debug(f"Confidence {confidence} below threshold {min_confidence}")
            sys.exit(0)

        if fix_type not in tracked_types and fix_type != "other":
            log_debug(f"Fix type '{fix_type}' not in tracked types")
            sys.exit(0)

        # Build issue details
        repo = config.get("default_repo", "gblack686/consulting-co")
        labels = config.get("default_labels", ["claude-code-fix"])
        summary = analysis.get("summary", "Fix applied during Claude Code session")

        # Add fix type as label
        if fix_type and fix_type != "none":
            labels = labels + [fix_type.replace("_", "-")]

        title_prefix = config.get("issue_template", {}).get("title_prefix", "[Claude Code Fix]")
        title = f"{title_prefix} {summary}"

        # Check for duplicates
        duplicates = check_for_duplicates(repo, summary, labels)
        if duplicates:
            log_debug(f"Found {len(duplicates)} potential duplicates, skipping")
            for dup in duplicates[:3]:
                log_debug(f"  #{dup.get('number')}: {dup.get('title')}")
            sys.exit(0)

        # Format body
        body = format_issue_body(analysis, session_id)

        # Create the issue
        dry_run = config.get("dry_run", False)
        success, result = create_github_issue(repo, title, body, labels, dry_run)

        if success:
            if dry_run:
                log_debug(f"DRY RUN complete - would have created: {title}")
            else:
                log_debug(f"SUCCESS: Created issue {result}")
        else:
            log_debug(f"FAILED: {result}")

        sys.exit(0)

    except json.JSONDecodeError:
        log_debug("Invalid JSON input")
        sys.exit(0)
    except Exception as e:
        log_debug(f"Hook error: {type(e).__name__}: {str(e)}")
        import traceback
        log_debug(traceback.format_exc())
        sys.exit(0)  # Don't fail the hook chain


if __name__ == "__main__":
    main()
