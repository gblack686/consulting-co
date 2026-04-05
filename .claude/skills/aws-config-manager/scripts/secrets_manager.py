#!/usr/bin/env python3
"""
AWS Secrets Manager and SSM Parameter Store Manager.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

import click
import boto3
from botocore.exceptions import ClientError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def load_settings():
    """Load skill settings."""
    settings_path = Path(__file__).parent.parent / "config" / "aws-settings.json"
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}


def get_session(profile: str = None, region: str = None):
    """Create boto3 session with optional profile and region."""
    settings = load_settings()
    region = region or settings.get("defaultRegion", "us-east-1")
    return boto3.Session(profile_name=profile, region_name=region)


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value for display."""
    if len(value) <= show_chars:
        return "***"
    return value[:show_chars] + "***" + value[-show_chars:]


# ============= Secrets Manager Functions =============

def list_secrets(profile: str = None, region: str = None, prefix: str = None):
    """List all secrets in Secrets Manager."""
    session = get_session(profile, region)
    client = session.client("secretsmanager")

    secrets = []
    paginator = client.get_paginator("list_secrets")

    filters = []
    if prefix:
        filters.append({"Key": "name", "Values": [prefix]})

    try:
        for page in paginator.paginate(Filters=filters if filters else []):
            for secret in page.get("SecretList", []):
                secrets.append({
                    "name": secret["Name"],
                    "arn": secret["ARN"],
                    "description": secret.get("Description", ""),
                    "last_changed": secret.get("LastChangedDate", "").isoformat() if secret.get("LastChangedDate") else None,
                    "last_accessed": secret.get("LastAccessedDate", "").isoformat() if secret.get("LastAccessedDate") else None,
                    "rotation_enabled": secret.get("RotationEnabled", False),
                    "tags": {t["Key"]: t["Value"] for t in secret.get("Tags", [])},
                })
        return {"success": True, "secrets": secrets, "count": len(secrets)}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_secret(name: str, profile: str = None, region: str = None, version: str = None, mask: bool = True):
    """Get a secret value from Secrets Manager."""
    session = get_session(profile, region)
    client = session.client("secretsmanager")

    try:
        params = {"SecretId": name}
        if version:
            params["VersionId"] = version

        response = client.get_secret_value(**params)

        # Determine if it's a string or binary secret
        if "SecretString" in response:
            value = response["SecretString"]
            # Try to parse as JSON
            try:
                parsed = json.loads(value)
                if mask:
                    # Mask values in JSON
                    masked = {k: mask_secret(str(v)) for k, v in parsed.items()}
                    return {
                        "success": True,
                        "name": response["Name"],
                        "type": "json",
                        "value": masked,
                        "raw_value": parsed,  # Include raw for programmatic use
                        "version": response.get("VersionId"),
                        "created": response.get("CreatedDate", "").isoformat() if response.get("CreatedDate") else None,
                    }
                else:
                    return {
                        "success": True,
                        "name": response["Name"],
                        "type": "json",
                        "value": parsed,
                        "version": response.get("VersionId"),
                    }
            except json.JSONDecodeError:
                display_value = mask_secret(value) if mask else value
                return {
                    "success": True,
                    "name": response["Name"],
                    "type": "string",
                    "value": display_value,
                    "version": response.get("VersionId"),
                }
        else:
            return {
                "success": True,
                "name": response["Name"],
                "type": "binary",
                "value": "[Binary data - use --no-mask to export]",
                "version": response.get("VersionId"),
            }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def describe_secret(name: str, profile: str = None, region: str = None):
    """Get metadata about a secret (without retrieving the value)."""
    session = get_session(profile, region)
    client = session.client("secretsmanager")

    try:
        response = client.describe_secret(SecretId=name)

        return {
            "success": True,
            "name": response["Name"],
            "arn": response["ARN"],
            "description": response.get("Description", ""),
            "kms_key_id": response.get("KmsKeyId"),
            "rotation_enabled": response.get("RotationEnabled", False),
            "rotation_lambda": response.get("RotationLambdaARN"),
            "last_rotated": response.get("LastRotatedDate", "").isoformat() if response.get("LastRotatedDate") else None,
            "last_changed": response.get("LastChangedDate", "").isoformat() if response.get("LastChangedDate") else None,
            "last_accessed": response.get("LastAccessedDate", "").isoformat() if response.get("LastAccessedDate") else None,
            "versions": list(response.get("VersionIdsToStages", {}).keys()),
            "tags": {t["Key"]: t["Value"] for t in response.get("Tags", [])},
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


# ============= SSM Parameter Store Functions =============

def list_parameters(profile: str = None, region: str = None, path: str = None, recursive: bool = True):
    """List SSM parameters, optionally by path."""
    session = get_session(profile, region)
    client = session.client("ssm")

    parameters = []

    try:
        if path:
            # Get parameters by path
            paginator = client.get_paginator("get_parameters_by_path")
            for page in paginator.paginate(Path=path, Recursive=recursive, WithDecryption=False):
                for param in page.get("Parameters", []):
                    parameters.append({
                        "name": param["Name"],
                        "type": param["Type"],
                        "version": param["Version"],
                        "last_modified": param.get("LastModifiedDate", "").isoformat() if param.get("LastModifiedDate") else None,
                    })
        else:
            # Describe all parameters
            paginator = client.get_paginator("describe_parameters")
            for page in paginator.paginate():
                for param in page.get("Parameters", []):
                    parameters.append({
                        "name": param["Name"],
                        "type": param["Type"],
                        "version": param.get("Version"),
                        "tier": param.get("Tier", "Standard"),
                        "last_modified": param.get("LastModifiedDate", "").isoformat() if param.get("LastModifiedDate") else None,
                        "description": param.get("Description", ""),
                    })

        return {"success": True, "parameters": parameters, "count": len(parameters)}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_parameter(name: str, profile: str = None, region: str = None, decrypt: bool = True, mask: bool = True):
    """Get an SSM parameter value."""
    session = get_session(profile, region)
    client = session.client("ssm")

    try:
        response = client.get_parameter(Name=name, WithDecryption=decrypt)
        param = response["Parameter"]

        value = param["Value"]
        display_value = mask_secret(value) if mask and param["Type"] == "SecureString" else value

        return {
            "success": True,
            "name": param["Name"],
            "type": param["Type"],
            "value": display_value,
            "version": param["Version"],
            "last_modified": param.get("LastModifiedDate", "").isoformat() if param.get("LastModifiedDate") else None,
            "arn": param.get("ARN"),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_parameters_batch(names: list, profile: str = None, region: str = None, decrypt: bool = True, mask: bool = True):
    """Get multiple SSM parameters at once."""
    session = get_session(profile, region)
    client = session.client("ssm")

    try:
        response = client.get_parameters(Names=names, WithDecryption=decrypt)

        parameters = []
        for param in response.get("Parameters", []):
            value = param["Value"]
            display_value = mask_secret(value) if mask and param["Type"] == "SecureString" else value
            parameters.append({
                "name": param["Name"],
                "type": param["Type"],
                "value": display_value,
                "version": param["Version"],
            })

        return {
            "success": True,
            "parameters": parameters,
            "invalid": response.get("InvalidParameters", []),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@click.command()
@click.option("--action", "-a", required=True,
              type=click.Choice(["list-secrets", "get-secret", "describe-secret",
                                "list-parameters", "get-parameter", "get-parameters"]))
@click.option("--name", "-n", default=None, help="Secret or parameter name")
@click.option("--names", default=None, help="Comma-separated parameter names for batch get")
@click.option("--path", default=None, help="Parameter path prefix")
@click.option("--prefix", default=None, help="Secret name prefix filter")
@click.option("--profile", "-p", default=None, help="AWS profile")
@click.option("--region", "-r", default=None, help="AWS region")
@click.option("--version", "-v", default=None, help="Secret version")
@click.option("--decrypt/--no-decrypt", default=True, help="Decrypt SecureString parameters")
@click.option("--mask/--no-mask", default=True, help="Mask secret values in output")
@click.option("--recursive/--no-recursive", default=True, help="Recursive parameter search")
@click.option("--output", "-o", default="table", type=click.Choice(["table", "json"]))
def main(action, name, names, path, prefix, profile, region, version, decrypt, mask, recursive, output):
    """AWS Secrets and Parameters Manager CLI."""

    if action == "list-secrets":
        result = list_secrets(profile, region, prefix)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Secrets Manager ({result['count']} secrets)")
                table.add_column("Name", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Rotation", style="green")
                table.add_column("Last Changed", style="yellow")

                for s in result["secrets"]:
                    table.add_row(
                        s["name"],
                        s["description"][:30] + "..." if len(s.get("description", "")) > 30 else s.get("description", ""),
                        "Yes" if s["rotation_enabled"] else "No",
                        s["last_changed"][:10] if s.get("last_changed") else "-"
                    )
                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "get-secret":
        if not name:
            console.print("[red]Error: --name required[/red]")
            sys.exit(1)

        result = get_secret(name, profile, region, version, mask)

        if output == "json":
            # Remove raw_value for JSON output if masking
            if mask and "raw_value" in result:
                del result["raw_value"]
            console.print_json(data=result)
        else:
            if result["success"]:
                if result["type"] == "json":
                    value_display = json.dumps(result["value"], indent=2)
                else:
                    value_display = result["value"]

                console.print(Panel(
                    f"Name: {result['name']}\n"
                    f"Type: {result['type']}\n"
                    f"Version: {result.get('version', 'N/A')}\n\n"
                    f"Value:\n{value_display}",
                    title="Secret Value"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "describe-secret":
        if not name:
            console.print("[red]Error: --name required[/red]")
            sys.exit(1)

        result = describe_secret(name, profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"Name: {result['name']}\n"
                    f"ARN: {result['arn']}\n"
                    f"Description: {result.get('description', 'N/A')}\n"
                    f"KMS Key: {result.get('kms_key_id', 'Default')}\n"
                    f"Rotation: {'Enabled' if result['rotation_enabled'] else 'Disabled'}\n"
                    f"Last Changed: {result.get('last_changed', 'N/A')}\n"
                    f"Last Accessed: {result.get('last_accessed', 'N/A')}\n"
                    f"Versions: {', '.join(result.get('versions', []))}",
                    title="Secret Metadata"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "list-parameters":
        result = list_parameters(profile, region, path, recursive)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"SSM Parameters ({result['count']} parameters)")
                table.add_column("Name", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Version", style="yellow")
                table.add_column("Last Modified", style="white")

                for p in result["parameters"]:
                    table.add_row(
                        p["name"],
                        p["type"],
                        str(p.get("version", "-")),
                        p["last_modified"][:10] if p.get("last_modified") else "-"
                    )
                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "get-parameter":
        if not name:
            console.print("[red]Error: --name required[/red]")
            sys.exit(1)

        result = get_parameter(name, profile, region, decrypt, mask)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"Name: {result['name']}\n"
                    f"Type: {result['type']}\n"
                    f"Version: {result['version']}\n"
                    f"Value: {result['value']}",
                    title="Parameter Value"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "get-parameters":
        if not names:
            console.print("[red]Error: --names required (comma-separated)[/red]")
            sys.exit(1)

        name_list = [n.strip() for n in names.split(",")]
        result = get_parameters_batch(name_list, profile, region, decrypt, mask)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title="Parameters")
                table.add_column("Name", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Value", style="white")

                for p in result["parameters"]:
                    table.add_row(p["name"], p["type"], p["value"])

                console.print(table)

                if result.get("invalid"):
                    console.print(f"[yellow]Invalid parameters: {', '.join(result['invalid'])}[/yellow]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")


if __name__ == "__main__":
    main()
