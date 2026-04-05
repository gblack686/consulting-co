#!/usr/bin/env python3
"""
GitHub Watchlist Integration for Obsidian
Monitors GitHub organizations and users for push activity and generates daily reports.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


class GitHubWatchlist:
    def __init__(self, config_path: str, vault_path: str):
        self.config_path = Path(config_path)
        self.vault_path = Path(vault_path)
        self.watchlist_dir = self.vault_path / "github-watchlist"
        self.state_file = self.watchlist_dir / ".state.json"

        # Ensure directories exist
        self.watchlist_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Load state
        self.state = self._load_state()

    def _load_config(self) -> Dict[str, Any]:
        """Load watchlist configuration."""
        if not self.config_path.exists():
            default_config = {
                "organizations": [],
                "users": [],
                "filters": {
                    "exclude_forks": True,
                    "exclude_archived": True,
                    "languages": []  # Empty = all languages
                },
                "notification_settings": {
                    "group_by_repo": True,
                    "include_commit_messages": True,
                    "max_commits_per_repo": 10
                }
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default config at: {self.config_path}")
            return default_config

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _load_state(self) -> Dict[str, Any]:
        """Load state file with last scrape timestamp."""
        if not self.state_file.exists():
            return {"last_scrape": None, "repositories": {}}

        with open(self.state_file, 'r') as f:
            return json.load(f)

    def _save_state(self):
        """Save state file."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _run_gh_command(self, args: List[str]) -> str:
        """Run GitHub CLI command and return output."""
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running gh command: {e.stderr}")
            return ""

    def _get_repos_for_org(self, org_name: str) -> List[Dict[str, Any]]:
        """Get all repositories for an organization."""
        json_output = self._run_gh_command([
            'repo', 'list', org_name,
            '--json', 'name,url,pushedAt,isFork,isArchived,primaryLanguage',
            '--limit', '1000'
        ])

        if not json_output:
            return []

        repos = json.loads(json_output)

        # Apply filters
        if self.config['filters']['exclude_forks']:
            repos = [r for r in repos if not r.get('isFork', False)]

        if self.config['filters']['exclude_archived']:
            repos = [r for r in repos if not r.get('isArchived', False)]

        if self.config['filters']['languages']:
            repos = [r for r in repos if r.get('primaryLanguage', {}).get('name') in self.config['filters']['languages']]

        return repos

    def _get_repos_for_user(self, username: str) -> List[Dict[str, Any]]:
        """Get all repositories for a user."""
        json_output = self._run_gh_command([
            'repo', 'list', username,
            '--json', 'name,url,pushedAt,isFork,isArchived,primaryLanguage',
            '--limit', '1000'
        ])

        if not json_output:
            return []

        repos = json.loads(json_output)

        # Apply filters
        if self.config['filters']['exclude_forks']:
            repos = [r for r in repos if not r.get('isFork', False)]

        if self.config['filters']['exclude_archived']:
            repos = [r for r in repos if not r.get('isArchived', False)]

        if self.config['filters']['languages']:
            repos = [r for r in repos if r.get('primaryLanguage', {}).get('name') in self.config['filters']['languages']]

        return repos

    def _get_commits_since(self, repo_url: str, since_date: str, max_commits: int = 10) -> List[Dict[str, Any]]:
        """Get commits for a repository since a given date."""
        # Extract owner/repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner_repo = f"{parts[-2]}/{parts[-1]}"

        json_output = self._run_gh_command([
            'api', f'/repos/{owner_repo}/commits',
            '--jq', f'.[] | select(.commit.author.date >= "{since_date}") | {{sha: .sha, message: .commit.message, author: .commit.author.name, date: .commit.author.date, url: .html_url}}'
        ])

        if not json_output:
            return []

        # Parse JSON lines
        commits = []
        for line in json_output.split('\n'):
            if line.strip():
                try:
                    commits.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return commits[:max_commits]

    def scrape(self, days_back: Optional[int] = None) -> Dict[str, Any]:
        """
        Scrape GitHub for updates.

        Args:
            days_back: Number of days to look back. If None, uses last scrape time or 1 day.
        """
        # Determine time range
        if days_back is not None:
            since_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        elif self.state['last_scrape']:
            since_date = self.state['last_scrape']
        else:
            since_date = (datetime.now() - timedelta(days=1)).isoformat()

        print(f"Scraping GitHub activity since {since_date}")

        results = {
            'scrape_time': datetime.now().isoformat(),
            'since': since_date,
            'organizations': {},
            'users': {},
            'total_repos': 0,
            'total_commits': 0
        }

        # Scrape organizations
        for org in self.config['organizations']:
            print(f"Fetching repos for organization: {org}")
            repos = self._get_repos_for_org(org)
            org_data = {'repos': []}

            for repo in repos:
                repo_name = repo['name']
                repo_url = repo['url']

                # Get commits since date
                commits = self._get_commits_since(repo_url, since_date,
                    self.config['notification_settings']['max_commits_per_repo'])

                if commits:  # Only include repos with new commits
                    org_data['repos'].append({
                        'name': repo_name,
                        'url': repo_url,
                        'language': repo.get('primaryLanguage', {}).get('name', 'Unknown'),
                        'pushed_at': repo['pushedAt'],
                        'commits': commits
                    })
                    results['total_commits'] += len(commits)

            results['total_repos'] += len(org_data['repos'])
            results['organizations'][org] = org_data

        # Scrape users
        for user in self.config['users']:
            print(f"Fetching repos for user: {user}")
            repos = self._get_repos_for_user(user)
            user_data = {'repos': []}

            for repo in repos:
                repo_name = repo['name']
                repo_url = repo['url']

                # Get commits since date
                commits = self._get_commits_since(repo_url, since_date,
                    self.config['notification_settings']['max_commits_per_repo'])

                if commits:  # Only include repos with new commits
                    user_data['repos'].append({
                        'name': repo_name,
                        'url': repo_url,
                        'language': repo.get('primaryLanguage', {}).get('name', 'Unknown'),
                        'pushed_at': repo['pushedAt'],
                        'commits': commits
                    })
                    results['total_commits'] += len(commits)

            results['total_repos'] += len(user_data['repos'])
            results['users'][user] = user_data

        # Update state
        self.state['last_scrape'] = results['scrape_time']
        self._save_state()

        return results

    def generate_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """Generate Obsidian-formatted markdown report."""
        if output_file is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_file = self.watchlist_dir / f"{date_str}-github-activity.md"
        else:
            output_file = Path(output_file)

        # Parse dates
        scrape_time = datetime.fromisoformat(results['scrape_time'])
        since_time = datetime.fromisoformat(results['since'])

        # Build markdown
        lines = []
        lines.append("---")
        lines.append("type: github-watchlist-report")
        lines.append(f"date: {scrape_time.strftime('%Y-%m-%d')}")
        lines.append(f"scrape_time: {scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"since: {since_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"total_repos: {results['total_repos']}")
        lines.append(f"total_commits: {results['total_commits']}")
        lines.append("tags:")
        lines.append("  - github")
        lines.append("  - watchlist")
        lines.append("  - automation")
        lines.append("---")
        lines.append("")
        lines.append(f"# GitHub Activity Report - {scrape_time.strftime('%Y-%m-%d')}")
        lines.append("")
        lines.append(f"**Period**: {since_time.strftime('%Y-%m-%d %H:%M')} to {scrape_time.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Total Repositories with Activity**: {results['total_repos']}")
        lines.append(f"**Total Commits**: {results['total_commits']}")
        lines.append("")

        # Organizations section
        if results['organizations']:
            lines.append("## Organizations")
            lines.append("")

            for org_name, org_data in results['organizations'].items():
                if org_data['repos']:
                    lines.append(f"### {org_name}")
                    lines.append("")
                    lines.append(f"**Repositories with activity**: {len(org_data['repos'])}")
                    lines.append("")

                    for repo in org_data['repos']:
                        lines.append(f"#### [{repo['name']}]({repo['url']})")
                        lines.append("")
                        lines.append(f"- **Language**: {repo['language']}")
                        lines.append(f"- **Last Push**: {repo['pushed_at']}")
                        lines.append(f"- **Commits**: {len(repo['commits'])}")
                        lines.append("")

                        if self.config['notification_settings']['include_commit_messages']:
                            lines.append("**Recent Commits**:")
                            lines.append("")
                            for commit in repo['commits']:
                                commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                                message = commit['message'].split('\n')[0]  # First line only
                                lines.append(f"- [{commit['sha'][:7]}]({commit['url']}) - {message}")
                                lines.append(f"  - *{commit['author']}* on {commit_date.strftime('%Y-%m-%d %H:%M')}")
                            lines.append("")

        # Users section
        if results['users']:
            lines.append("## Users")
            lines.append("")

            for user_name, user_data in results['users'].items():
                if user_data['repos']:
                    lines.append(f"### {user_name}")
                    lines.append("")
                    lines.append(f"**Repositories with activity**: {len(user_data['repos'])}")
                    lines.append("")

                    for repo in user_data['repos']:
                        lines.append(f"#### [{repo['name']}]({repo['url']})")
                        lines.append("")
                        lines.append(f"- **Language**: {repo['language']}")
                        lines.append(f"- **Last Push**: {repo['pushed_at']}")
                        lines.append(f"- **Commits**: {len(repo['commits'])}")
                        lines.append("")

                        if self.config['notification_settings']['include_commit_messages']:
                            lines.append("**Recent Commits**:")
                            lines.append("")
                            for commit in repo['commits']:
                                commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                                message = commit['message'].split('\n')[0]  # First line only
                                lines.append(f"- [{commit['sha'][:7]}]({commit['url']}) - {message}")
                                lines.append(f"  - *{commit['author']}* on {commit_date.strftime('%Y-%m-%d %H:%M')}")
                            lines.append("")

        # No activity section
        if results['total_repos'] == 0:
            lines.append("## No Activity")
            lines.append("")
            lines.append("No repositories had push activity during this period.")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by GitHub Watchlist Integration*")

        # Write to file
        markdown = '\n'.join(lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"Report generated: {output_file}")
        return str(output_file)


def main():
    parser = argparse.ArgumentParser(description='GitHub Watchlist for Obsidian')
    parser.add_argument('--config', default='.claude/obsidian/github-watchlist-config.json',
                       help='Path to configuration file')
    parser.add_argument('--vault', default='C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation',
                       help='Path to Obsidian vault')
    parser.add_argument('--days', type=int, help='Number of days to look back')
    parser.add_argument('--output', help='Output file path (optional)')

    args = parser.parse_args()

    # Check if gh CLI is installed
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: GitHub CLI (gh) is not installed or not in PATH")
        print("Install from: https://cli.github.com/")
        sys.exit(1)

    # Create watchlist instance
    watchlist = GitHubWatchlist(args.config, args.vault)

    # Run scrape
    print("Starting GitHub scrape...")
    results = watchlist.scrape(days_back=args.days)

    # Generate report
    report_path = watchlist.generate_report(results, args.output)

    print(f"\nSummary:")
    print(f"  Repositories with activity: {results['total_repos']}")
    print(f"  Total commits: {results['total_commits']}")
    print(f"  Report saved to: {report_path}")


if __name__ == '__main__':
    main()
