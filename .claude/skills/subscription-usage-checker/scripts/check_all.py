#!/usr/bin/env python3
"""
Subscription Usage Checker - Main Orchestrator
Checks usage across all configured services and generates reports.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import individual checkers
from check_anthropic import check_anthropic_usage
from check_elevenlabs import check_elevenlabs_usage
from check_aws import check_aws_costs
from check_openai import check_openai_usage
from check_supabase import check_supabase_usage
from check_gemini import check_gemini_usage
from check_apify import check_apify_usage


def get_status_emoji(percent_used: float, warn: float = 50, critical: float = 80) -> str:
    """Return status emoji based on usage percentage."""
    if percent_used >= critical:
        return "🔴"
    elif percent_used >= warn:
        return "⚠️"
    else:
        return "✅"


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"


def format_number(num: float) -> str:
    """Format large numbers with commas."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:,.0f}"


def load_config() -> dict:
    """Load service configuration."""
    config_path = Path(__file__).parent.parent / "config" / "services.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    # Default config
    return {
        "anthropic": {"enabled": True},
        "elevenlabs": {"enabled": True},
        "aws": {"enabled": True},
        "openai": {"enabled": True},
        "supabase": {"enabled": True},
        "gemini": {"enabled": True},
        "apify": {"enabled": True}
    }


def check_all_services(services: Optional[list] = None, verbose: bool = False) -> dict:
    """Check all enabled services and return results."""
    config = load_config()
    results = {}

    service_checkers = {
        "anthropic": check_anthropic_usage,
        "elevenlabs": check_elevenlabs_usage,
        "aws": check_aws_costs,
        "openai": check_openai_usage,
        "supabase": check_supabase_usage,
        "gemini": check_gemini_usage,
        "apify": check_apify_usage
    }

    for service_name, checker_func in service_checkers.items():
        if services and service_name not in services:
            continue
        if not config.get(service_name, {}).get("enabled", True):
            continue

        try:
            if verbose:
                print(f"Checking {service_name}...")
            results[service_name] = checker_func()
        except Exception as e:
            results[service_name] = {
                "status": "error",
                "error": str(e)
            }

    return results


def output_console(results: dict) -> None:
    """Output results to console with rich formatting."""
    if not RICH_AVAILABLE:
        # Fallback to simple output
        print("\n=== Subscription Usage Report ===\n")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        for service, data in results.items():
            if data.get("status") == "error":
                print(f"{service}: ERROR - {data.get('error')}")
            else:
                used = data.get("used_display", "N/A")
                remaining = data.get("remaining_display", "N/A")
                status = data.get("status_display", "Unknown")
                print(f"{service}: Used={used}, Remaining={remaining}, Status={status}")
        return

    console = Console()

    # Header
    console.print(Panel(
        f"[bold cyan]Subscription Usage Report[/bold cyan]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]",
        box=box.DOUBLE
    ))
    console.print()

    # Create table
    table = Table(
        title="Service Usage Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )

    table.add_column("Service", style="cyan", width=12)
    table.add_column("Used", style="yellow", width=15)
    table.add_column("Remaining", style="green", width=15)
    table.add_column("Status", width=20)

    for service, data in results.items():
        if data.get("status") == "error":
            table.add_row(
                service.title(),
                "[red]Error[/red]",
                "-",
                f"[red]{data.get('error', 'Unknown error')[:30]}[/red]"
            )
        else:
            used = data.get("used_display", "N/A")
            remaining = data.get("remaining_display", "N/A")
            status = data.get("status_display", "Unknown")
            percent = data.get("percent_used", 0)
            emoji = get_status_emoji(percent)

            table.add_row(
                service.title(),
                used,
                remaining,
                f"{emoji} {status}"
            )

    console.print(table)
    console.print()


def output_markdown(results: dict, output_file: Optional[str] = None) -> str:
    """Generate markdown report."""
    lines = [
        f"# Subscription Usage Report",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"## Summary",
        f"",
        f"| Service | Used | Remaining | Status |",
        f"|---------|------|-----------|--------|"
    ]

    for service, data in results.items():
        if data.get("status") == "error":
            lines.append(f"| {service.title()} | Error | - | {data.get('error', 'Unknown')[:30]} |")
        else:
            used = data.get("used_display", "N/A")
            remaining = data.get("remaining_display", "N/A")
            status = data.get("status_display", "Unknown")
            percent = data.get("percent_used", 0)
            emoji = get_status_emoji(percent)
            lines.append(f"| {service.title()} | {used} | {remaining} | {emoji} {status} |")

    lines.extend([
        "",
        "## Detailed Breakdown",
        ""
    ])

    for service, data in results.items():
        lines.append(f"### {service.title()}")
        lines.append("")

        if data.get("status") == "error":
            lines.append(f"**Error:** {data.get('error')}")
        else:
            for key, value in data.items():
                if not key.endswith("_display") and key not in ["status", "error"]:
                    lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        lines.append("")

    content = "\n".join(lines)

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report saved to: {output_file}")

    return content


def output_json(results: dict, output_file: Optional[str] = None) -> str:
    """Generate JSON output."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "services": results
    }

    content = json.dumps(output, indent=2, default=str)

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print(f"Report saved to: {output_file}")

    return content


def main():
    parser = argparse.ArgumentParser(
        description="Check subscription usage across all services"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["console", "markdown", "json"],
        default="console",
        help="Output format"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    parser.add_argument(
        "--services", "-s",
        help="Comma-separated list of services to check"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    services = args.services.split(",") if args.services else None

    results = check_all_services(services=services, verbose=args.verbose)

    if args.format == "console":
        output_console(results)
    elif args.format == "markdown":
        content = output_markdown(results, args.output)
        if not args.output and not args.quiet:
            print(content)
    elif args.format == "json":
        content = output_json(results, args.output)
        if not args.output and not args.quiet:
            print(content)

    # Exit with error code if any service failed
    if any(r.get("status") == "error" for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
