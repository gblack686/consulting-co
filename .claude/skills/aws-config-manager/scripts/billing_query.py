#!/usr/bin/env python3
"""
AWS Cost Explorer - Query billing and cost data.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
    """Create boto3 session."""
    settings = load_settings()
    # Cost Explorer is only available in us-east-1
    region = "us-east-1"
    return boto3.Session(profile_name=profile, region_name=region)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency."""
    return f"${amount:,.2f} {currency}"


def get_date_range(period: str = "current-month", start: str = None, end: str = None, days: int = None):
    """Calculate date range based on period type."""
    today = datetime.now().date()

    if start and end:
        return start, end

    if days:
        start_date = today - timedelta(days=days)
        return start_date.isoformat(), today.isoformat()

    if period == "current-month":
        start_date = today.replace(day=1)
        return start_date.isoformat(), today.isoformat()

    elif period == "last-month":
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        return last_month_start.isoformat(), first_of_month.isoformat()

    elif period == "last-30-days":
        start_date = today - timedelta(days=30)
        return start_date.isoformat(), today.isoformat()

    elif period == "last-90-days":
        start_date = today - timedelta(days=90)
        return start_date.isoformat(), today.isoformat()

    elif period == "ytd":  # Year to date
        start_date = today.replace(month=1, day=1)
        return start_date.isoformat(), today.isoformat()

    # Default to current month
    start_date = today.replace(day=1)
    return start_date.isoformat(), today.isoformat()


def get_cost_and_usage(profile: str = None, start: str = None, end: str = None,
                       granularity: str = "MONTHLY", group_by: str = None,
                       filter_service: str = None):
    """Get cost and usage data from Cost Explorer."""
    session = get_session(profile)
    client = session.client("ce")

    start_date, end_date = get_date_range(start=start, end=end)

    params = {
        "TimePeriod": {"Start": start_date, "End": end_date},
        "Granularity": granularity,
        "Metrics": ["UnblendedCost", "UsageQuantity"],
    }

    if group_by:
        if group_by == "SERVICE":
            params["GroupBy"] = [{"Type": "DIMENSION", "Key": "SERVICE"}]
        elif group_by == "REGION":
            params["GroupBy"] = [{"Type": "DIMENSION", "Key": "REGION"}]
        elif group_by == "LINKED_ACCOUNT":
            params["GroupBy"] = [{"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"}]
        elif group_by.startswith("TAG:"):
            tag_key = group_by.replace("TAG:", "")
            params["GroupBy"] = [{"Type": "TAG", "Key": tag_key}]

    if filter_service:
        params["Filter"] = {
            "Dimensions": {
                "Key": "SERVICE",
                "Values": [filter_service]
            }
        }

    try:
        response = client.get_cost_and_usage(**params)

        results = []
        total_cost = 0.0

        for result in response.get("ResultsByTime", []):
            period_start = result["TimePeriod"]["Start"]
            period_end = result["TimePeriod"]["End"]

            if group_by:
                for group in result.get("Groups", []):
                    key = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    total_cost += amount
                    results.append({
                        "period": f"{period_start} to {period_end}",
                        "group": key,
                        "cost": amount,
                        "currency": group["Metrics"]["UnblendedCost"]["Unit"],
                    })
            else:
                amount = float(result["Total"]["UnblendedCost"]["Amount"])
                total_cost += amount
                results.append({
                    "period": f"{period_start} to {period_end}",
                    "cost": amount,
                    "currency": result["Total"]["UnblendedCost"]["Unit"],
                })

        return {
            "success": True,
            "period": f"{start_date} to {end_date}",
            "granularity": granularity,
            "total_cost": total_cost,
            "currency": "USD",
            "results": results,
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_cost_by_service(profile: str = None, period: str = "current-month",
                        start: str = None, end: str = None, top_n: int = 10):
    """Get cost breakdown by AWS service."""
    start_date, end_date = get_date_range(period, start, end)

    session = get_session(profile)
    client = session.client("ce")

    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )

        services = []
        for result in response.get("ResultsByTime", []):
            for group in result.get("Groups", []):
                service = group["Keys"][0]
                amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                if amount > 0:
                    services.append({"service": service, "cost": amount})

        # Sort by cost descending
        services.sort(key=lambda x: x["cost"], reverse=True)

        total = sum(s["cost"] for s in services)

        return {
            "success": True,
            "period": f"{start_date} to {end_date}",
            "total": total,
            "currency": "USD",
            "services": services[:top_n] if top_n else services,
            "other_count": len(services) - top_n if top_n and len(services) > top_n else 0,
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_cost_forecast(profile: str = None, days: int = 30):
    """Get cost forecast for the specified period."""
    session = get_session(profile)
    client = session.client("ce")

    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    # For forecast, we need to start from tomorrow at minimum
    start_date = today + timedelta(days=1)

    try:
        response = client.get_cost_forecast(
            TimePeriod={"Start": start_date.isoformat(), "End": end_date.isoformat()},
            Metric="UNBLENDED_COST",
            Granularity="MONTHLY"
        )

        forecast = float(response["Total"]["Amount"])

        return {
            "success": True,
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "forecast": forecast,
            "currency": response["Total"]["Unit"],
            "prediction_intervals": response.get("ForecastResultsByTime", []),
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_monthly_comparison(profile: str = None, months: int = 3):
    """Compare costs across recent months."""
    session = get_session(profile)
    client = session.client("ce")

    today = datetime.now().date()
    start_date = (today - relativedelta(months=months)).replace(day=1)

    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_date.isoformat(), "End": today.isoformat()},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )

        months_data = []
        for result in response.get("ResultsByTime", []):
            period = result["TimePeriod"]["Start"][:7]  # YYYY-MM
            amount = float(result["Total"]["UnblendedCost"]["Amount"])
            months_data.append({"month": period, "cost": amount})

        # Calculate month-over-month change
        for i in range(1, len(months_data)):
            prev = months_data[i-1]["cost"]
            curr = months_data[i]["cost"]
            if prev > 0:
                change = ((curr - prev) / prev) * 100
                months_data[i]["change_percent"] = round(change, 2)

        return {
            "success": True,
            "months": months_data,
            "currency": "USD",
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_daily_costs(profile: str = None, days: int = 7):
    """Get daily cost breakdown for recent days."""
    start_date, end_date = get_date_range(days=days)

    session = get_session(profile)
    client = session.client("ce")

    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="DAILY",
            Metrics=["UnblendedCost"]
        )

        days_data = []
        for result in response.get("ResultsByTime", []):
            date = result["TimePeriod"]["Start"]
            amount = float(result["Total"]["UnblendedCost"]["Amount"])
            days_data.append({"date": date, "cost": amount})

        total = sum(d["cost"] for d in days_data)
        avg = total / len(days_data) if days_data else 0

        return {
            "success": True,
            "period": f"{start_date} to {end_date}",
            "days": days_data,
            "total": total,
            "average_daily": avg,
            "currency": "USD",
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


@click.command()
@click.option("--action", "-a", required=True,
              type=click.Choice(["current-month", "by-service", "forecast",
                                "monthly-comparison", "daily", "custom"]))
@click.option("--profile", "-p", default=None, help="AWS profile")
@click.option("--start", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end", default=None, help="End date (YYYY-MM-DD)")
@click.option("--days", default=None, type=int, help="Number of days to look back")
@click.option("--months", default=3, type=int, help="Number of months for comparison")
@click.option("--top", default=10, type=int, help="Top N services to show")
@click.option("--group-by", default=None,
              type=click.Choice(["SERVICE", "REGION", "LINKED_ACCOUNT"]),
              help="Group results by dimension")
@click.option("--granularity", default="MONTHLY",
              type=click.Choice(["DAILY", "MONTHLY"]))
@click.option("--output", "-o", default="table", type=click.Choice(["table", "json"]))
def main(action, profile, start, end, days, months, top, group_by, granularity, output):
    """AWS Cost Explorer CLI."""

    if action == "current-month":
        result = get_cost_by_service(profile, "current-month", top_n=top)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"Period: {result['period']}\n"
                    f"Total: {format_currency(result['total'])}",
                    title="Current Month Costs"
                ))

                table = Table(title="Cost by Service")
                table.add_column("Service", style="cyan")
                table.add_column("Cost", style="green", justify="right")
                table.add_column("% of Total", style="yellow", justify="right")

                for s in result["services"]:
                    pct = (s["cost"] / result["total"]) * 100 if result["total"] > 0 else 0
                    table.add_row(
                        s["service"],
                        format_currency(s["cost"]),
                        f"{pct:.1f}%"
                    )

                if result["other_count"] > 0:
                    table.add_row(
                        f"[dim]... and {result['other_count']} more services[/dim]",
                        "", ""
                    )

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "by-service":
        result = get_cost_by_service(profile, start=start, end=end, top_n=top)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Cost by Service ({result['period']})")
                table.add_column("Service", style="cyan")
                table.add_column("Cost", style="green", justify="right")

                for s in result["services"]:
                    table.add_row(s["service"], format_currency(s["cost"]))

                console.print(table)
                console.print(f"\n[bold]Total: {format_currency(result['total'])}[/bold]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "forecast":
        forecast_days = days or 30
        result = get_cost_forecast(profile, forecast_days)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"Forecast Period: {result['period']}\n"
                    f"Predicted Cost: {format_currency(result['forecast'])}",
                    title="Cost Forecast"
                ))
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "monthly-comparison":
        result = get_monthly_comparison(profile, months)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Monthly Cost Comparison (Last {months} Months)")
                table.add_column("Month", style="cyan")
                table.add_column("Cost", style="green", justify="right")
                table.add_column("Change", style="yellow", justify="right")

                for m in result["months"]:
                    change = m.get("change_percent")
                    change_str = ""
                    if change is not None:
                        if change > 0:
                            change_str = f"[red]+{change}%[/red]"
                        elif change < 0:
                            change_str = f"[green]{change}%[/green]"
                        else:
                            change_str = "0%"

                    table.add_row(m["month"], format_currency(m["cost"]), change_str)

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "daily":
        num_days = days or 7
        result = get_daily_costs(profile, num_days)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Daily Costs (Last {num_days} Days)")
                table.add_column("Date", style="cyan")
                table.add_column("Cost", style="green", justify="right")

                for d in result["days"]:
                    table.add_row(d["date"], format_currency(d["cost"]))

                console.print(table)
                console.print(f"\n[bold]Total: {format_currency(result['total'])}[/bold]")
                console.print(f"[dim]Daily Average: {format_currency(result['average_daily'])}[/dim]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "custom":
        if not start or not end:
            console.print("[red]Error: --start and --end required for custom queries[/red]")
            sys.exit(1)

        result = get_cost_and_usage(profile, start, end, granularity, group_by)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(Panel(
                    f"Period: {result['period']}\n"
                    f"Granularity: {result['granularity']}\n"
                    f"Total: {format_currency(result['total_cost'])}",
                    title="Cost Query Results"
                ))

                if group_by:
                    table = Table()
                    table.add_column("Period")
                    table.add_column("Group")
                    table.add_column("Cost", justify="right")

                    for r in result["results"]:
                        table.add_row(r["period"], r.get("group", "-"), format_currency(r["cost"]))

                    console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")


if __name__ == "__main__":
    main()
