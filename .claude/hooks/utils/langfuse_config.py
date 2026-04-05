#!/usr/bin/env python3
"""
Langfuse configuration manager.
Handles project mapping and configuration for multi-repo observability.
Supports dynamic org/project detection and auto-creation based on working directory.
"""

import os
import yaml
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple

class LangfuseConfig:
    """Manage Langfuse configuration and project mapping."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Langfuse config.

        Args:
            config_path: Path to langfuse.yaml config file.
                        If not provided, searches in .claude/config/
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load Langfuse configuration from YAML file."""

        # Try provided path first
        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}

        # Search for config in .claude/config/
        search_paths = [
            Path.cwd() / ".claude" / "config" / "langfuse.yaml",
            Path.cwd() / ".." / ".claude" / "config" / "langfuse.yaml",
            Path.home() / ".claude" / "config" / "langfuse.yaml",
        ]

        for path in search_paths:
            if path.exists():
                with open(path, 'r') as f:
                    return yaml.safe_load(f) or {}

        # Return empty config if file not found
        return {}

    def get_base_url(self) -> str:
        """Get Langfuse base URL."""
        return os.getenv(
            "LANGFUSE_BASE_URL",
            self.config.get("langfuse", {}).get("base_url", "http://localhost:3000")
        )

    def get_organization(self) -> str:
        """Get Langfuse organization name."""
        return os.getenv(
            "LANGFUSE_ORGANIZATION",
            self.config.get("langfuse", {}).get("organization", "default")
        )

    def get_project_id_for_dir(self, directory_name: str) -> Optional[str]:
        """Get Langfuse project ID for a given directory name.

        Args:
            directory_name: Repository directory name (e.g., 'consulting-co')

        Returns:
            Project ID if found, None otherwise
        """
        projects = self.config.get("langfuse", {}).get("projects", {})
        return projects.get(directory_name)

    def get_current_project_id(self) -> Optional[str]:
        """Get Langfuse project ID for current directory.

        Uses:
        1. LANGFUSE_PROJECT_ID environment variable (highest priority)
        2. PROJECT_NAME environment variable -> project mapping
        3. Current directory name -> project mapping (auto-detect)

        Returns:
            Project ID if found, None otherwise
        """
        # Check environment variable first
        project_id = os.getenv("LANGFUSE_PROJECT_ID")
        if project_id:
            return project_id

        # Check PROJECT_NAME env var
        project_name = os.getenv("PROJECT_NAME")
        if project_name:
            project_id = self.get_project_id_for_dir(project_name)
            if project_id:
                return project_id

        # Auto-detect from current directory
        if self.config.get("langfuse", {}).get("auto_detect_project"):
            current_dir = Path.cwd().name
            project_id = self.get_project_id_for_dir(current_dir)
            if project_id:
                return project_id

        return None

    def get_current_project_name(self) -> str:
        """Get project name for current directory.

        Returns:
            PROJECT_NAME env var, or current directory name
        """
        return os.getenv("PROJECT_NAME", Path.cwd().name)

    def get_capture_config(self) -> Dict:
        """Get what to capture in traces."""
        return self.config.get("langfuse", {}).get("capture", {})

    def get_tracing_config(self) -> Dict:
        """Get tracing configuration."""
        return self.config.get("langfuse", {}).get("tracing", {})

    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled."""
        return os.getenv("ENABLE_LANGFUSE", "false").lower() == "true"

    def detect_organization(self) -> Tuple[str, str]:
        """Detect organization and project based on working directory.

        Returns:
            Tuple of (organization, project_id) or (organization, None) if project doesn't exist yet
        """
        cwd = Path.cwd()
        cwd_str = str(cwd)

        # Check if we're in a RevStar quickstart
        if "aws" in cwd_str and "RevStar" in cwd_str and "quickstarts" in cwd_str:
            org = "RevStar"
            # Extract quickstart name (e.g., quickstart-dataforinclusion)
            try:
                quickstarts_idx = cwd.parts.index("quickstarts")
                if quickstarts_idx + 1 < len(cwd.parts):
                    project_name = cwd.parts[quickstarts_idx + 1]
                    return org, project_name
            except (ValueError, IndexError):
                pass

        # Default: consulting-co organization
        return "consulting-co", None

    def get_credentials_for_org(self, organization: str) -> Dict[str, str]:
        """Get API credentials for a specific organization.

        Args:
            organization: Organization name ('RevStar' or 'consulting-co')

        Returns:
            Dict with 'public_key', 'secret_key', 'base_url'
        """
        # Check environment for organization-specific credentials
        org_upper = organization.upper().replace("-", "_")

        public_key = os.getenv(f"LANGFUSE_PUBLIC_KEY_{org_upper}") or os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv(f"LANGFUSE_SECRET_KEY_{org_upper}") or os.getenv("LANGFUSE_SECRET_KEY")
        base_url = os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")

        return {
            "public_key": public_key,
            "secret_key": secret_key,
            "base_url": base_url,
            "organization": organization
        }

    def get_or_create_project(self, organization: str, project_name: str) -> Optional[str]:
        """Get or create a Langfuse project.

        Args:
            organization: Organization name
            project_name: Project name (will be used as project ID)

        Returns:
            Project ID if successful, None otherwise
        """
        creds = self.get_credentials_for_org(organization)
        base_url = creds["base_url"]
        public_key = creds["public_key"]
        secret_key = creds["secret_key"]

        if not public_key or not secret_key:
            return None

        try:
            # First, try to list projects and find existing one
            response = requests.get(
                f"{base_url}/api/public/projects",
                auth=(public_key, secret_key),
                timeout=5
            )

            if response.status_code == 200:
                projects = response.json().get("data", [])
                for proj in projects:
                    if proj.get("name") == project_name:
                        return proj.get("id")

            # If project doesn't exist, create it
            create_response = requests.post(
                f"{base_url}/api/public/projects",
                auth=(public_key, secret_key),
                json={"name": project_name},
                timeout=5
            )

            if create_response.status_code in (200, 201):
                return create_response.json().get("id")

        except Exception as e:
            # Fail silently - just log the error
            print(f"[WARNING] Failed to get/create project: {e}", file=__import__('sys').stderr)

        return None


def get_langfuse_config(config_path: Optional[str] = None) -> LangfuseConfig:
    """Get Langfuse configuration singleton.

    Args:
        config_path: Optional path to langfuse.yaml

    Returns:
        LangfuseConfig instance
    """
    return LangfuseConfig(config_path)


if __name__ == "__main__":
    # Test the configuration
    config = get_langfuse_config()

    print("=== Langfuse Configuration ===")
    print(f"Base URL: {config.get_base_url()}")
    print(f"Organization: {config.get_organization()}")
    print(f"Current Project: {config.get_current_project_name()}")
    print(f"Project ID: {config.get_current_project_id()}")
    print(f"Enabled: {config.is_enabled()}")
    print(f"Capture Config: {config.get_capture_config()}")
