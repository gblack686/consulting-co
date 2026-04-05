#!/usr/bin/env python3
"""
AWS Credentials Manager - Manage AWS profiles, credentials, and authentication.
"""

import os
import sys
import json
import configparser
from pathlib import Path
from datetime import datetime, timezone

import click
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def get_aws_config_paths():
    """Get paths to AWS config and credentials files."""
    home = Path.home()
    return {
        "config": home / ".aws" / "config",
        "credentials": home / ".aws" / "credentials",
    }


def load_settings():
    """Load skill settings."""
    settings_path = Path(__file__).parent.parent / "config" / "aws-settings.json"
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}


def list_profiles():
    """List all available AWS profiles."""
    paths = get_aws_config_paths()
    profiles = set()

    # Parse credentials file
    if paths["credentials"].exists():
        creds = configparser.ConfigParser()
        creds.read(paths["credentials"])
        profiles.update(creds.sections())

    # Parse config file
    if paths["config"].exists():
        config = configparser.ConfigParser()
        config.read(paths["config"])
        for section in config.sections():
            # Config file uses "profile <name>" format for non-default profiles
            if section.startswith("profile "):
                profiles.add(section.replace("profile ", ""))
            elif section == "default":
                profiles.add("default")

    return sorted(profiles)


def get_profile_details(profile_name: str):
    """Get details for a specific profile."""
    paths = get_aws_config_paths()
    details = {"profile": profile_name, "type": "unknown", "region": None}

    # Check credentials file
    if paths["credentials"].exists():
        creds = configparser.ConfigParser()
        creds.read(paths["credentials"])
        if profile_name in creds.sections() or (profile_name == "default" and "default" in creds.sections()):
            section = profile_name if profile_name in creds.sections() else "default"
            if creds.has_option(section, "aws_access_key_id"):
                details["type"] = "static"
                details["access_key_prefix"] = creds.get(section, "aws_access_key_id")[:8] + "..."

    # Check config file for additional settings
    if paths["config"].exists():
        config = configparser.ConfigParser()
        config.read(paths["config"])
        section = f"profile {profile_name}" if profile_name != "default" else "default"

        if section in config.sections() or profile_name == "default":
            actual_section = section if section in config.sections() else "default"

            if config.has_option(actual_section, "region"):
                details["region"] = config.get(actual_section, "region")

            if config.has_option(actual_section, "sso_start_url"):
                details["type"] = "sso"
                details["sso_start_url"] = config.get(actual_section, "sso_start_url")
                details["sso_account_id"] = config.get(actual_section, "sso_account_id", fallback=None)
                details["sso_role_name"] = config.get(actual_section, "sso_role_name", fallback=None)

            if config.has_option(actual_section, "role_arn"):
                details["type"] = "assume_role"
                details["role_arn"] = config.get(actual_section, "role_arn")
                details["source_profile"] = config.get(actual_section, "source_profile", fallback=None)

    return details


def validate_credentials(profile: str = None, region: str = None):
    """Validate AWS credentials by calling STS GetCallerIdentity."""
    settings = load_settings()
    region = region or settings.get("defaultRegion", "us-east-1")

    try:
        session = boto3.Session(profile_name=profile, region_name=region)
        sts = session.client("sts")
        identity = sts.get_caller_identity()

        return {
            "valid": True,
            "account": identity["Account"],
            "arn": identity["Arn"],
            "user_id": identity["UserId"],
            "profile": profile or "default",
            "region": region,
        }
    except NoCredentialsError:
        return {"valid": False, "error": "No credentials found"}
    except ProfileNotFound:
        return {"valid": False, "error": f"Profile '{profile}' not found"}
    except ClientError as e:
        return {"valid": False, "error": str(e)}


def assume_role(role_arn: str, session_name: str = None, profile: str = None,
                duration_seconds: int = 3600, external_id: str = None):
    """Assume an IAM role and get temporary credentials."""
    session_name = session_name or f"aws-config-manager-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    try:
        session = boto3.Session(profile_name=profile)
        sts = session.client("sts")

        params = {
            "RoleArn": role_arn,
            "RoleSessionName": session_name,
            "DurationSeconds": duration_seconds,
        }

        if external_id:
            params["ExternalId"] = external_id

        response = sts.assume_role(**params)
        creds = response["Credentials"]

        return {
            "success": True,
            "access_key_id": creds["AccessKeyId"],
            "secret_access_key": "***MASKED***",  # Never expose
            "session_token": creds["SessionToken"][:20] + "...",  # Truncated
            "expiration": creds["Expiration"].isoformat(),
            "assumed_role_user": response["AssumedRoleUser"]["Arn"],
            "export_commands": f"""
# Export these environment variables:
export AWS_ACCESS_KEY_ID="{creds['AccessKeyId']}"
export AWS_SECRET_ACCESS_KEY="<secret>"
export AWS_SESSION_TOKEN="<token>"
""",
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_session_token(profile: str = None, duration_seconds: int = 3600, mfa_serial: str = None, mfa_token: str = None):
    """Get temporary session token, optionally with MFA."""
    try:
        session = boto3.Session(profile_name=profile)
        sts = session.client("sts")

        params = {"DurationSeconds": duration_seconds}

        if mfa_serial and mfa_token:
            params["SerialNumber"] = mfa_serial
            params["TokenCode"] = mfa_token

        response = sts.get_session_token(**params)
        creds = response["Credentials"]

        return {
            "success": True,
            "access_key_id": creds["AccessKeyId"],
            "expiration": creds["Expiration"].isoformat(),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@click.command()
@click.option("--action", "-a", required=True,
              type=click.Choice(["list-profiles", "validate", "profile-details",
                                "assume-role", "session-token", "export"]))
@click.option("--profile", "-p", default=None, help="AWS profile to use")
@click.option("--region", "-r", default=None, help="AWS region")
@click.option("--role-arn", default=None, help="Role ARN for assume-role")
@click.option("--session-name", default=None, help="Session name for assume-role")
@click.option("--duration", default=3600, type=int, help="Session duration in seconds")
@click.option("--external-id", default=None, help="External ID for assume-role")
@click.option("--mfa-serial", default=None, help="MFA device serial for session-token")
@click.option("--mfa-token", default=None, help="MFA token code")
@click.option("--output", "-o", default="table", type=click.Choice(["table", "json"]))
def main(action, profile, region, role_arn, session_name, duration, external_id, mfa_serial, mfa_token, output):
    """AWS Credentials Manager CLI."""

    if action == "list-profiles":
        profiles = list_profiles()

        if output == "json":
            console.print_json(data=profiles)
        else:
            table = Table(title="AWS Profiles")
            table.add_column("Profile", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Region", style="yellow")

            for p in profiles:
                details = get_profile_details(p)
                table.add_row(p, details.get("type", "unknown"), details.get("region", "-"))

            console.print(table)

    elif action == "validate":
        result = validate_credentials(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["valid"]:
                console.print(Panel(
                    f"[green]✓ Credentials Valid[/green]\n\n"
                    f"Account: {result['account']}\n"
                    f"ARN: {result['arn']}\n"
                    f"User ID: {result['user_id']}\n"
                    f"Profile: {result['profile']}\n"
                    f"Region: {result['region']}",
                    title="AWS Identity"
                ))
            else:
                console.print(f"[red]✗ Invalid: {result['error']}[/red]")

    elif action == "profile-details":
        if not profile:
            console.print("[red]Error: --profile required for profile-details[/red]")
            sys.exit(1)

        details = get_profile_details(profile)

        if output == "json":
            console.print_json(data=details)
        else:
            console.print(Panel(
                "\n".join([f"{k}: {v}" for k, v in details.items()]),
                title=f"Profile: {profile}"
            ))

    elif action == "assume-role":
        if not role_arn:
            console.print("[red]Error: --role-arn required for assume-role[/red]")
            sys.exit(1)

        result = assume_role(role_arn, session_name, profile, duration, external_id)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"[green]✓ Role Assumed Successfully[/green]\n\n"
                    f"Access Key: {result['access_key_id']}\n"
                    f"Expiration: {result['expiration']}\n"
                    f"Assumed Role: {result['assumed_role_user']}\n\n"
                    f"{result['export_commands']}",
                    title="Temporary Credentials"
                ))
            else:
                console.print(f"[red]✗ Failed: {result['error']}[/red]")

    elif action == "session-token":
        result = get_session_token(profile, duration, mfa_serial, mfa_token)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"[green]✓ Session Token Retrieved[/green]\n\n"
                    f"Access Key: {result['access_key_id']}\n"
                    f"Expiration: {result['expiration']}",
                    title="Session Credentials"
                ))
            else:
                console.print(f"[red]✗ Failed: {result['error']}[/red]")

    elif action == "export":
        result = validate_credentials(profile, region)
        if result["valid"]:
            session = boto3.Session(profile_name=profile, region_name=region)
            creds = session.get_credentials()
            frozen = creds.get_frozen_credentials()

            console.print("# Export these to your shell:")
            console.print(f'export AWS_ACCESS_KEY_ID="{frozen.access_key}"')
            console.print('export AWS_SECRET_ACCESS_KEY="***"  # Get from credentials file')
            if frozen.token:
                console.print('export AWS_SESSION_TOKEN="***"  # Get from credentials file')
            console.print(f'export AWS_DEFAULT_REGION="{region or "us-east-1"}"')
        else:
            console.print(f"[red]Cannot export: {result['error']}[/red]")


if __name__ == "__main__":
    main()
