#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Secret Scanner — PostToolUse Hook (Write)

Scans newly written files for hardcoded secrets:
  - API keys (sk-ant-*, AKIA*, ghp_*, sk-proj-*)
  - Tokens, passwords, connection strings
  - Private keys

Action: WARN (log + stderr message, don't block)
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.hook_utils import read_hook_input, log_hook_activity


# Secret patterns — (regex, description, severity)
SECRET_PATTERNS = [
    # Anthropic
    (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API key", "high"),
    # OpenAI
    (r"sk-proj-[a-zA-Z0-9_-]{20,}", "OpenAI project API key", "high"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API key (legacy)", "high"),
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", "critical"),
    (r"(?:aws_secret_access_key|AWS_SECRET)\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}", "AWS Secret Key", "critical"),
    # GitHub
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token", "high"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token", "high"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub Server Token", "high"),
    (r"github_pat_[a-zA-Z0-9_]{82}", "GitHub Fine-grained PAT", "high"),
    # Stripe
    (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe Live Secret Key", "critical"),
    (r"sk_test_[a-zA-Z0-9]{24,}", "Stripe Test Secret Key", "medium"),
    # Supabase
    (r"eyJ[a-zA-Z0-9_-]{100,}\.[a-zA-Z0-9_-]{100,}\.[a-zA-Z0-9_-]{40,}", "JWT Token (possibly Supabase)", "medium"),
    # Generic
    (r"(?:password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "Hardcoded password", "high"),
    (r"(?:secret|token|api_key|apikey)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "Hardcoded secret/token", "high"),
    (r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----", "Private key", "critical"),
    # Database
    (r"(?:postgres|mysql|mongodb)://[a-zA-Z0-9_:@]+", "Database connection string", "high"),
]

# Files to skip scanning
SKIP_EXTENSIONS = {".lock", ".png", ".jpg", ".gif", ".ico", ".woff", ".woff2", ".ttf"}
SKIP_PATHS = {"node_modules/", "dist/", "build/", "__pycache__/", ".git/"}


def should_skip(file_path: str) -> bool:
    """Check if file should be skipped."""
    fp = file_path.replace("\\", "/")

    ext = Path(fp).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return True

    for skip in SKIP_PATHS:
        if skip in fp:
            return True

    return False


def scan_content(content: str) -> list:
    """Scan content for secret patterns."""
    findings = []
    for pattern, description, severity in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            findings.append({
                "pattern": description,
                "severity": severity,
                "count": len(matches),
                "sample": matches[0][:20] + "..." if len(matches[0]) > 20 else matches[0],
            })
    return findings


def main():
    try:
        input_data = read_hook_input()

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name != "Write":
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        if not file_path or not content:
            sys.exit(0)

        if should_skip(file_path):
            sys.exit(0)

        findings = scan_content(content)

        if findings:
            # Log findings
            log_hook_activity(
                "secret_scanner",
                {
                    "file_path": file_path,
                    "findings_count": len(findings),
                    "findings": findings,
                },
                log_subdir="hooks/creative",
            )

            # Warn via stderr
            print(
                f"SECRET SCANNER WARNING: {len(findings)} potential secret(s) in {Path(file_path).name}",
                file=sys.stderr,
            )
            for f in findings:
                icon = "!!!" if f["severity"] == "critical" else "!!" if f["severity"] == "high" else "!"
                print(
                    f"  [{icon}] {f['pattern']} ({f['severity']}) — found {f['count']}x",
                    file=sys.stderr,
                )

        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
