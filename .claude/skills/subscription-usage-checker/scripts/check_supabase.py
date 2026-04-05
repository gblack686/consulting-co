#!/usr/bin/env python3
"""
Supabase Usage Checker
Checks Supabase project usage, storage, and plan status.
"""

import argparse
import json
import os
from typing import Optional

import requests

# Try to import boto3 for AWS Secrets Manager
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_access_token() -> str:
    """Get Supabase access token from various sources."""
    # 1. Environment variable
    if os.environ.get("SUPABASE_ACCESS_TOKEN"):
        return os.environ["SUPABASE_ACCESS_TOKEN"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(SecretId="gbautomation/infrastructure/supabase")
            secret = response["SecretString"]
            try:
                data = json.loads(secret)
                return data.get("access_token", data.get("SUPABASE_ACCESS_TOKEN", secret))
            except json.JSONDecodeError:
                return secret
        except Exception:
            pass

    raise ValueError("No Supabase access token found. Set SUPABASE_ACCESS_TOKEN or store in AWS Secrets Manager.")


def check_supabase_usage(project_ref: Optional[str] = None) -> dict:
    """
    Check Supabase project usage and plan status.

    Args:
        project_ref: Specific project reference (optional)

    Returns:
        dict with usage information
    """
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    base_url = "https://api.supabase.com/v1"

    try:
        # List all projects
        projects_response = requests.get(
            f"{base_url}/projects",
            headers=headers,
            timeout=30
        )

        if projects_response.status_code == 401:
            return {
                "status": "error",
                "error": "Invalid access token"
            }
        elif projects_response.status_code != 200:
            return {
                "status": "error",
                "error": f"API returned status {projects_response.status_code}"
            }

        projects = projects_response.json()

        if not projects:
            return {
                "status": "success",
                "message": "No projects found",
                "used_display": "0 projects",
                "remaining_display": "N/A",
                "status_display": "No projects",
                "percent_used": 0
            }

        # If specific project requested, filter
        if project_ref:
            projects = [p for p in projects if p.get("id") == project_ref]
            if not projects:
                return {
                    "status": "error",
                    "error": f"Project {project_ref} not found"
                }

        total_db_size = 0
        total_storage = 0
        project_details = []

        for project in projects:
            ref = project.get("id")
            name = project.get("name", "Unknown")
            region = project.get("region", "Unknown")
            status = project.get("status", "Unknown")

            project_info = {
                "name": name,
                "ref": ref,
                "region": region,
                "status": status
            }

            # Try to get usage for this project
            try:
                usage_response = requests.get(
                    f"{base_url}/projects/{ref}/usage",
                    headers=headers,
                    timeout=30
                )
                if usage_response.status_code == 200:
                    usage = usage_response.json()
                    project_info["database_size"] = usage.get("db_size", 0)
                    project_info["storage_size"] = usage.get("storage_size", 0)
                    project_info["bandwidth"] = usage.get("bandwidth", 0)

                    total_db_size += usage.get("db_size", 0)
                    total_storage += usage.get("storage_size", 0)
            except Exception:
                pass

            project_details.append(project_info)

        # Free tier limits (as of 2026)
        free_db_limit = 500 * 1024 * 1024  # 500 MB
        free_storage_limit = 1 * 1024 * 1024 * 1024  # 1 GB
        free_bandwidth_limit = 2 * 1024 * 1024 * 1024  # 2 GB

        # Format sizes
        def format_bytes(b):
            if b >= 1024 * 1024 * 1024:
                return f"{b / (1024*1024*1024):.1f} GB"
            elif b >= 1024 * 1024:
                return f"{b / (1024*1024):.1f} MB"
            elif b >= 1024:
                return f"{b / 1024:.1f} KB"
            return f"{b} B"

        # Calculate usage percentage (based on free tier)
        db_percent = (total_db_size / free_db_limit * 100) if free_db_limit > 0 else 0

        result = {
            "status": "success",
            "project_count": len(projects),
            "total_database_size": total_db_size,
            "total_database_size_formatted": format_bytes(total_db_size),
            "total_storage_size": total_storage,
            "total_storage_size_formatted": format_bytes(total_storage),
            "free_tier_db_limit": format_bytes(free_db_limit),
            "free_tier_storage_limit": format_bytes(free_storage_limit),
            "percent_used": round(db_percent, 1),
            "used_display": format_bytes(total_db_size),
            "remaining_display": format_bytes(max(0, free_db_limit - total_db_size)),
            "status_display": f"{len(projects)} project(s)",
            "projects": project_details
        }

        return result

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "Request timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Check Supabase project usage")
    parser.add_argument("--project-ref", help="Specific project reference")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_supabase_usage(project_ref=args.project_ref)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Supabase Usage ===\n")
        for key, value in result.items():
            if key == "projects":
                print(f"  Projects:")
                for p in value:
                    print(f"    - {p['name']} ({p['status']})")
                    if "database_size" in p:
                        print(f"      DB: {p.get('database_size', 0) / (1024*1024):.1f} MB")
            elif not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
