#!/usr/bin/env python3
"""
Test GitHub CLI authentication for the GitHub Issue Manager skill.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from github_ops import check_auth, list_issues


def main():
    """Test gh CLI authentication and basic operations."""
    print("=" * 50)
    print("GitHub CLI Authentication Test")
    print("=" * 50)

    # Test 1: Auth status
    print("\n1. Checking authentication status...")
    auth_ok, auth_msg = check_auth()

    if auth_ok:
        print("   [PASS] Authenticated successfully")
        # Parse account info from message
        for line in auth_msg.split('\n'):
            if 'Logged in' in line or 'Active account' in line:
                print(f"   {line.strip()}")
    else:
        print("   [FAIL] Not authenticated")
        print(f"   Error: {auth_msg}")
        print("\n   To authenticate, run: gh auth login")
        return 1

    # Test 2: List issues from default repo
    print("\n2. Testing issue list capability...")
    test_repo = "gblack686/consulting-co"

    success, result = list_issues(test_repo, state="open", limit=5)

    if success:
        print(f"   [PASS] Can list issues from {test_repo}")
        print(f"   Found {len(result)} open issues")
        if result:
            print("   Recent issues:")
            for issue in result[:3]:
                print(f"     #{issue['number']}: {issue['title'][:50]}...")
    else:
        print(f"   [FAIL] Cannot list issues")
        print(f"   Error: {result}")
        return 1

    # Test 3: Check required scopes
    print("\n3. Checking token scopes...")
    if 'repo' in auth_msg.lower():
        print("   [PASS] Has 'repo' scope (can create/manage issues)")
    else:
        print("   [WARN] May not have 'repo' scope")

    print("\n" + "=" * 50)
    print("All tests passed! GitHub integration is ready.")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
