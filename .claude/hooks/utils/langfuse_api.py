#!/usr/bin/env python3
"""
Langfuse API utility for common trace operations.
Provides simple, error-aware access to Langfuse REST API.
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

class LangfuseAPI:
    """Client for Langfuse REST API operations."""

    def __init__(self, base_url: str = None, public_key: str = None, secret_key: str = None):
        """Initialize Langfuse API client.

        Args:
            base_url: Langfuse server URL (defaults to env or http://localhost:3000)
            public_key: API public key (defaults to env LANGFUSE_PUBLIC_KEY)
            secret_key: API secret key (defaults to env LANGFUSE_SECRET_KEY)
        """
        # Load environment
        env_path = Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)

        self.base_url = base_url or os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")
        self.base_url = self.base_url.rstrip('/')
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY", "")

    def _request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None) -> Dict:
        """Make authenticated request to Langfuse API.

        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint path (e.g. /api/public/traces)
            params: Query parameters
            json_data: JSON body for POST requests

        Returns:
            Response JSON as dict

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                auth=(self.public_key, self.secret_key),
                timeout=10
            )

            # Log errors but don't raise - return response
            if response.status_code != 200:
                print(f"⚠️  API returned {response.status_code}: {response.text}", file=__import__('sys').stderr)

            return response.json() if response.text else {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}", file=__import__('sys').stderr)
            return {"error": str(e)}

    def get_traces(self, limit: int = 10, project_id: str = None) -> List[Dict]:
        """Fetch recent traces.

        Args:
            limit: Number of traces to fetch
            project_id: Filter by project ID (optional)

        Returns:
            List of trace dicts
        """
        params = {"limit": limit}
        if project_id:
            params["projectId"] = project_id

        response = self._request("GET", "/api/public/traces", params=params)
        return response.get("data", [])

    def get_trace(self, trace_id: str) -> Dict:
        """Fetch a specific trace by ID.

        Args:
            trace_id: The trace ID

        Returns:
            Trace dict with observations
        """
        return self._request("GET", f"/api/public/traces/{trace_id}")

    def get_observations(self, trace_id: str) -> List[Dict]:
        """Fetch observations for a trace.

        Args:
            trace_id: The trace ID

        Returns:
            List of observation dicts
        """
        response = self._request("GET", f"/api/public/traces/{trace_id}/observations")
        return response.get("data", [])

    def get_projects(self) -> List[Dict]:
        """Fetch all projects in the organization.

        Returns:
            List of project dicts
        """
        response = self._request("GET", "/api/public/projects")
        return response.get("data", [])

    def create_project(self, name: str) -> Optional[str]:
        """Create a new project.

        Args:
            name: Project name

        Returns:
            Project ID if created, None on error
        """
        response = self._request("POST", "/api/public/projects", json_data={"name": name})
        return response.get("id")

    def print_trace_summary(self, trace: Dict) -> None:
        """Pretty print a trace summary.

        Args:
            trace: Trace dict from API
        """
        print("\n" + "="*60)
        print(f"📊 TRACE: {trace.get('name', 'unknown')}")
        print("="*60)
        print(f"ID:        {trace.get('id')}")
        print(f"Session:   {trace.get('sessionId')}")
        print(f"Project:   {trace.get('projectId')}")
        print(f"Tags:      {', '.join(trace.get('tags', []))}")
        print(f"Cost:      ${trace.get('totalCost', 0):.6f}")
        print(f"Latency:   {trace.get('latency', 0)}ms")
        print(f"Model:     {trace.get('model', 'N/A')}")

        if trace.get('metadata'):
            print(f"\nMetadata:")
            for key, value in trace.get('metadata', {}).items():
                if not isinstance(value, (dict, list)):
                    print(f"  {key}: {value}")

        print(f"\nObservations: {len(trace.get('observations', []))}")
        for obs in trace.get('observations', []):
            obs_type = obs.get('type', 'UNKNOWN')
            obs_name = obs.get('name', 'unnamed')
            print(f"  - {obs_type}: {obs_name}")


def main():
    """CLI for fetching and displaying traces."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Langfuse trace utilities")
    parser.add_argument("command", choices=["list", "get", "projects"], help="Command to run")
    parser.add_argument("--trace-id", help="Trace ID (for 'get' command)")
    parser.add_argument("--limit", type=int, default=5, help="Number of traces to fetch")
    parser.add_argument("--project-id", help="Filter by project ID")

    args = parser.parse_args()

    api = LangfuseAPI()

    if args.command == "list":
        traces = api.get_traces(limit=args.limit, project_id=args.project_id)
        for trace in traces:
            api.print_trace_summary(trace)
        if not traces:
            print("No traces found")

    elif args.command == "get":
        if not args.trace_id:
            print("Error: --trace-id required for 'get' command")
            sys.exit(1)
        trace = api.get_trace(args.trace_id)
        print(json.dumps(trace, indent=2))

    elif args.command == "projects":
        projects = api.get_projects()
        print(f"\n{'='*60}")
        print(f"📋 PROJECTS ({len(projects)} total)")
        print(f"{'='*60}")
        for proj in projects:
            print(f"  {proj.get('name')} ({proj.get('id')})")


if __name__ == "__main__":
    main()
