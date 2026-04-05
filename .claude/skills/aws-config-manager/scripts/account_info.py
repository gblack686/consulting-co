#!/usr/bin/env python3
"""
AWS Account Information - Get account details, identity, regions, and organization info.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

import click
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
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
    """Create boto3 session."""
    settings = load_settings()
    region = region or settings.get("defaultRegion", "us-east-1")
    return boto3.Session(profile_name=profile, region_name=region)


def get_caller_identity(profile: str = None, region: str = None):
    """Get current IAM identity information."""
    try:
        session = get_session(profile, region)
        sts = session.client("sts")

        identity = sts.get_caller_identity()

        # Parse ARN to extract user/role type
        arn = identity["Arn"]
        arn_parts = arn.split(":")
        resource = arn_parts[-1] if len(arn_parts) > 5 else ""

        identity_type = "unknown"
        identity_name = resource

        if resource.startswith("user/"):
            identity_type = "user"
            identity_name = resource.replace("user/", "")
        elif resource.startswith("assumed-role/"):
            identity_type = "assumed-role"
            parts = resource.replace("assumed-role/", "").split("/")
            identity_name = parts[0] if parts else resource
        elif resource.startswith("root"):
            identity_type = "root"
            identity_name = "root"

        return {
            "success": True,
            "account": identity["Account"],
            "arn": identity["Arn"],
            "user_id": identity["UserId"],
            "identity_type": identity_type,
            "identity_name": identity_name,
            "profile": profile or "default",
            "region": region or "us-east-1",
        }
    except NoCredentialsError:
        return {"success": False, "error": "No credentials found"}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_account_aliases(profile: str = None, region: str = None):
    """Get IAM account aliases."""
    try:
        session = get_session(profile, region)
        iam = session.client("iam")

        response = iam.list_account_aliases()

        return {
            "success": True,
            "aliases": response.get("AccountAliases", []),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def list_regions(profile: str = None, region: str = None, enabled_only: bool = True):
    """List available AWS regions."""
    try:
        session = get_session(profile, region)
        ec2 = session.client("ec2")

        if enabled_only:
            response = ec2.describe_regions()
        else:
            response = ec2.describe_regions(AllRegions=True)

        regions = []
        for r in response.get("Regions", []):
            regions.append({
                "name": r["RegionName"],
                "endpoint": r["Endpoint"],
                "opt_in_status": r.get("OptInStatus", "opt-in-not-required"),
            })

        return {
            "success": True,
            "regions": sorted(regions, key=lambda x: x["name"]),
            "count": len(regions),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_organization_info(profile: str = None, region: str = None):
    """Get AWS Organization information."""
    try:
        session = get_session(profile, region)
        org = session.client("organizations")

        response = org.describe_organization()
        org_info = response["Organization"]

        return {
            "success": True,
            "id": org_info["Id"],
            "arn": org_info["Arn"],
            "master_account_id": org_info["MasterAccountId"],
            "master_account_email": org_info.get("MasterAccountEmail", "N/A"),
            "feature_set": org_info["FeatureSet"],
            "available_policy_types": [p["Type"] for p in org_info.get("AvailablePolicyTypes", [])],
        }
    except ClientError as e:
        if "AWSOrganizationsNotInUseException" in str(e):
            return {"success": False, "error": "Account is not part of an organization"}
        return {"success": False, "error": str(e)}


def list_organization_accounts(profile: str = None, region: str = None):
    """List all accounts in the organization."""
    try:
        session = get_session(profile, region)
        org = session.client("organizations")

        accounts = []
        paginator = org.get_paginator("list_accounts")

        for page in paginator.paginate():
            for account in page.get("Accounts", []):
                accounts.append({
                    "id": account["Id"],
                    "name": account["Name"],
                    "email": account["Email"],
                    "status": account["Status"],
                    "joined": account.get("JoinedTimestamp", "").isoformat() if account.get("JoinedTimestamp") else None,
                })

        return {
            "success": True,
            "accounts": accounts,
            "count": len(accounts),
        }
    except ClientError as e:
        if "AWSOrganizationsNotInUseException" in str(e):
            return {"success": False, "error": "Account is not part of an organization"}
        if "AccessDeniedException" in str(e):
            return {"success": False, "error": "Access denied - need organizations:ListAccounts permission"}
        return {"success": False, "error": str(e)}


def get_service_quotas(profile: str = None, region: str = None, service_code: str = None):
    """Get service quotas for a specific service."""
    try:
        session = get_session(profile, region)
        sq = session.client("service-quotas")

        if not service_code:
            # List available services
            services = []
            paginator = sq.get_paginator("list_services")

            for page in paginator.paginate():
                for svc in page.get("Services", []):
                    services.append({
                        "code": svc["ServiceCode"],
                        "name": svc["ServiceName"],
                    })

            return {"success": True, "services": services, "count": len(services)}
        else:
            # Get quotas for specific service
            quotas = []
            paginator = sq.get_paginator("list_service_quotas")

            for page in paginator.paginate(ServiceCode=service_code):
                for quota in page.get("Quotas", []):
                    quotas.append({
                        "name": quota["QuotaName"],
                        "code": quota["QuotaCode"],
                        "value": quota["Value"],
                        "unit": quota.get("Unit", ""),
                        "adjustable": quota["Adjustable"],
                        "global": quota.get("GlobalQuota", False),
                    })

            return {"success": True, "service": service_code, "quotas": quotas}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_account_summary(profile: str = None, region: str = None):
    """Get comprehensive account summary."""
    identity = get_caller_identity(profile, region)
    if not identity["success"]:
        return identity

    aliases = get_account_aliases(profile, region)
    org_info = get_organization_info(profile, region)
    regions = list_regions(profile, region)

    return {
        "success": True,
        "identity": identity,
        "aliases": aliases.get("aliases", []) if aliases["success"] else [],
        "organization": org_info if org_info["success"] else None,
        "enabled_regions": regions["count"] if regions["success"] else 0,
    }


@click.command()
@click.option("--action", "-a", required=True,
              type=click.Choice(["identity", "aliases", "regions", "organization",
                                "accounts", "quotas", "summary"]))
@click.option("--profile", "-p", default=None, help="AWS profile")
@click.option("--region", "-r", default=None, help="AWS region")
@click.option("--all-regions", is_flag=True, help="Include opt-in regions")
@click.option("--service", default=None, help="Service code for quotas")
@click.option("--output", "-o", default="table", type=click.Choice(["table", "json"]))
def main(action, profile, region, all_regions, service, output):
    """AWS Account Information CLI."""

    if action == "identity":
        result = get_caller_identity(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"[bold]Account ID:[/bold] {result['account']}\n"
                    f"[bold]Identity Type:[/bold] {result['identity_type']}\n"
                    f"[bold]Identity Name:[/bold] {result['identity_name']}\n"
                    f"[bold]User ID:[/bold] {result['user_id']}\n"
                    f"[bold]ARN:[/bold] {result['arn']}\n"
                    f"[bold]Profile:[/bold] {result['profile']}\n"
                    f"[bold]Region:[/bold] {result['region']}",
                    title="AWS Identity"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "aliases":
        result = get_account_aliases(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                if result["aliases"]:
                    console.print("[bold]Account Aliases:[/bold]")
                    for alias in result["aliases"]:
                        console.print(f"  - {alias}")
                else:
                    console.print("[dim]No account aliases configured[/dim]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "regions":
        result = list_regions(profile, region, enabled_only=not all_regions)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"AWS Regions ({result['count']})")
                table.add_column("Region", style="cyan")
                table.add_column("Endpoint", style="white")
                table.add_column("Status", style="green")

                for r in result["regions"]:
                    status = r["opt_in_status"]
                    if status == "opted-in":
                        status_style = "[green]Opted In[/green]"
                    elif status == "not-opted-in":
                        status_style = "[yellow]Not Opted In[/yellow]"
                    else:
                        status_style = "[dim]Default[/dim]"

                    table.add_row(r["name"], r["endpoint"], status_style)

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "organization":
        result = get_organization_info(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"[bold]Organization ID:[/bold] {result['id']}\n"
                    f"[bold]Master Account:[/bold] {result['master_account_id']}\n"
                    f"[bold]Master Email:[/bold] {result['master_account_email']}\n"
                    f"[bold]Feature Set:[/bold] {result['feature_set']}\n"
                    f"[bold]Policy Types:[/bold] {', '.join(result['available_policy_types']) or 'None'}",
                    title="AWS Organization"
                ))
            else:
                console.print(f"[yellow]{result['error']}[/yellow]")

    elif action == "accounts":
        result = list_organization_accounts(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Organization Accounts ({result['count']})")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="white")
                table.add_column("Email", style="dim")
                table.add_column("Status", style="green")

                for a in result["accounts"]:
                    status_style = "[green]ACTIVE[/green]" if a["status"] == "ACTIVE" else f"[yellow]{a['status']}[/yellow]"
                    table.add_row(a["id"], a["name"], a["email"], status_style)

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "quotas":
        result = get_service_quotas(profile, region, service)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                if "services" in result:
                    # List of services
                    table = Table(title=f"Available Services ({result['count']})")
                    table.add_column("Code", style="cyan")
                    table.add_column("Name", style="white")

                    for svc in result["services"][:30]:
                        table.add_row(svc["code"], svc["name"])

                    console.print(table)
                    if result["count"] > 30:
                        console.print(f"[dim]... and {result['count'] - 30} more services. Use --service <code> to see quotas.[/dim]")
                else:
                    # Quotas for specific service
                    table = Table(title=f"Quotas for {result['service']}")
                    table.add_column("Name", style="cyan")
                    table.add_column("Value", style="green", justify="right")
                    table.add_column("Unit", style="dim")
                    table.add_column("Adjustable", style="yellow")

                    for q in result["quotas"]:
                        table.add_row(
                            q["name"][:50],
                            str(q["value"]),
                            q["unit"],
                            "Yes" if q["adjustable"] else "No"
                        )

                    console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "summary":
        result = get_account_summary(profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                identity = result["identity"]

                console.print(Panel(
                    f"[bold cyan]Account:[/bold cyan] {identity['account']}\n"
                    f"[bold cyan]Identity:[/bold cyan] {identity['identity_name']} ({identity['identity_type']})\n"
                    f"[bold cyan]Aliases:[/bold cyan] {', '.join(result['aliases']) or 'None'}\n"
                    f"[bold cyan]Enabled Regions:[/bold cyan] {result['enabled_regions']}\n"
                    f"[bold cyan]Organization:[/bold cyan] {'Yes - ' + result['organization']['id'] if result['organization'] else 'No'}",
                    title="Account Summary"
                ))
            else:
                console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")


if __name__ == "__main__":
    main()
