#!/usr/bin/env python3
"""
AWS CloudWatch Alerts Manager - Manage CloudWatch alarms and metrics.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

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
    region = region or settings.get("defaultRegion", "us-east-1")
    return boto3.Session(profile_name=profile, region_name=region)


def state_color(state: str) -> str:
    """Get color for alarm state."""
    colors = {
        "OK": "green",
        "ALARM": "red",
        "INSUFFICIENT_DATA": "yellow",
    }
    return colors.get(state, "white")


def list_alarms(profile: str = None, region: str = None, state_filter: str = None,
                prefix: str = None, namespace: str = None):
    """List all CloudWatch alarms."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    alarms = []
    params = {}

    if state_filter:
        params["StateValue"] = state_filter
    if prefix:
        params["AlarmNamePrefix"] = prefix

    try:
        paginator = client.get_paginator("describe_alarms")

        for page in paginator.paginate(**params):
            for alarm in page.get("MetricAlarms", []):
                if namespace and alarm.get("Namespace") != namespace:
                    continue

                alarms.append({
                    "name": alarm["AlarmName"],
                    "state": alarm["StateValue"],
                    "metric": alarm["MetricName"],
                    "namespace": alarm["Namespace"],
                    "threshold": alarm["Threshold"],
                    "comparison": alarm["ComparisonOperator"],
                    "period": alarm["Period"],
                    "evaluation_periods": alarm["EvaluationPeriods"],
                    "statistic": alarm.get("Statistic") or alarm.get("ExtendedStatistic"),
                    "description": alarm.get("AlarmDescription", ""),
                    "actions_enabled": alarm["ActionsEnabled"],
                    "last_updated": alarm.get("StateUpdatedTimestamp", "").isoformat() if alarm.get("StateUpdatedTimestamp") else None,
                })

            # Also get composite alarms
            for alarm in page.get("CompositeAlarms", []):
                alarms.append({
                    "name": alarm["AlarmName"],
                    "state": alarm["StateValue"],
                    "type": "composite",
                    "rule": alarm.get("AlarmRule", ""),
                    "description": alarm.get("AlarmDescription", ""),
                    "actions_enabled": alarm["ActionsEnabled"],
                })

        return {"success": True, "alarms": alarms, "count": len(alarms)}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_alarm_details(name: str, profile: str = None, region: str = None):
    """Get detailed information about a specific alarm."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    try:
        response = client.describe_alarms(AlarmNames=[name])

        alarms = response.get("MetricAlarms", []) + response.get("CompositeAlarms", [])

        if not alarms:
            return {"success": False, "error": f"Alarm '{name}' not found"}

        alarm = alarms[0]

        # Determine if metric or composite
        is_composite = "AlarmRule" in alarm

        details = {
            "success": True,
            "name": alarm["AlarmName"],
            "arn": alarm["AlarmArn"],
            "state": alarm["StateValue"],
            "state_reason": alarm.get("StateReason", ""),
            "description": alarm.get("AlarmDescription", ""),
            "actions_enabled": alarm["ActionsEnabled"],
            "ok_actions": alarm.get("OKActions", []),
            "alarm_actions": alarm.get("AlarmActions", []),
            "insufficient_data_actions": alarm.get("InsufficientDataActions", []),
            "state_updated": alarm.get("StateUpdatedTimestamp", "").isoformat() if alarm.get("StateUpdatedTimestamp") else None,
        }

        if is_composite:
            details["type"] = "composite"
            details["rule"] = alarm.get("AlarmRule", "")
        else:
            details["type"] = "metric"
            details["metric"] = alarm["MetricName"]
            details["namespace"] = alarm["Namespace"]
            details["statistic"] = alarm.get("Statistic") or alarm.get("ExtendedStatistic")
            details["period"] = alarm["Period"]
            details["evaluation_periods"] = alarm["EvaluationPeriods"]
            details["threshold"] = alarm["Threshold"]
            details["comparison"] = alarm["ComparisonOperator"]
            details["dimensions"] = {d["Name"]: d["Value"] for d in alarm.get("Dimensions", [])}
            details["treat_missing_data"] = alarm.get("TreatMissingData", "missing")

        return details
    except ClientError as e:
        return {"success": False, "error": str(e)}


def get_alarm_history(name: str, profile: str = None, region: str = None,
                      history_type: str = None, days: int = 7):
    """Get alarm history."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    start_date = datetime.utcnow() - timedelta(days=days)

    params = {
        "AlarmName": name,
        "StartDate": start_date,
        "EndDate": datetime.utcnow(),
    }

    if history_type:
        params["HistoryItemType"] = history_type

    try:
        history = []
        paginator = client.get_paginator("describe_alarm_history")

        for page in paginator.paginate(**params):
            for item in page.get("AlarmHistoryItems", []):
                history.append({
                    "timestamp": item["Timestamp"].isoformat(),
                    "type": item["HistoryItemType"],
                    "summary": item["HistorySummary"],
                })

        return {"success": True, "alarm": name, "history": history}
    except ClientError as e:
        return {"success": False, "error": str(e)}


def create_alarm(name: str, metric: str, namespace: str, threshold: float,
                 comparison: str, profile: str = None, region: str = None,
                 period: int = 300, evaluation_periods: int = 2,
                 statistic: str = "Average", description: str = None,
                 dimensions: dict = None, alarm_actions: list = None):
    """Create a new CloudWatch alarm."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    params = {
        "AlarmName": name,
        "MetricName": metric,
        "Namespace": namespace,
        "Threshold": threshold,
        "ComparisonOperator": comparison,
        "Period": period,
        "EvaluationPeriods": evaluation_periods,
        "Statistic": statistic,
        "ActionsEnabled": True,
    }

    if description:
        params["AlarmDescription"] = description

    if dimensions:
        params["Dimensions"] = [{"Name": k, "Value": v} for k, v in dimensions.items()]

    if alarm_actions:
        params["AlarmActions"] = alarm_actions

    try:
        client.put_metric_alarm(**params)
        return {
            "success": True,
            "message": f"Alarm '{name}' created successfully",
            "alarm_name": name,
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def delete_alarm(names: list, profile: str = None, region: str = None):
    """Delete CloudWatch alarms."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    try:
        client.delete_alarms(AlarmNames=names)
        return {
            "success": True,
            "message": f"Deleted {len(names)} alarm(s)",
            "deleted": names,
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def set_alarm_state(name: str, state: str, reason: str = None,
                    profile: str = None, region: str = None):
    """Manually set alarm state (for testing)."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    reason = reason or f"Manual state change to {state}"

    try:
        client.set_alarm_state(
            AlarmName=name,
            StateValue=state,
            StateReason=reason
        )
        return {
            "success": True,
            "alarm": name,
            "new_state": state,
            "reason": reason,
        }
    except ClientError as e:
        return {"success": False, "error": str(e)}


def list_metrics(profile: str = None, region: str = None, namespace: str = None):
    """List available CloudWatch metrics."""
    session = get_session(profile, region)
    client = session.client("cloudwatch")

    params = {}
    if namespace:
        params["Namespace"] = namespace

    try:
        metrics = []
        paginator = client.get_paginator("list_metrics")

        for page in paginator.paginate(**params):
            for metric in page.get("Metrics", []):
                metrics.append({
                    "namespace": metric["Namespace"],
                    "metric": metric["MetricName"],
                    "dimensions": {d["Name"]: d["Value"] for d in metric.get("Dimensions", [])},
                })

        return {"success": True, "metrics": metrics, "count": len(metrics)}
    except ClientError as e:
        return {"success": False, "error": str(e)}


@click.command()
@click.option("--action", "-a", required=True,
              type=click.Choice(["list-alarms", "get-alarm", "alarm-history",
                                "create-alarm", "delete-alarm", "set-state",
                                "list-metrics"]))
@click.option("--name", "-n", default=None, help="Alarm name")
@click.option("--names", default=None, help="Comma-separated alarm names for delete")
@click.option("--profile", "-p", default=None, help="AWS profile")
@click.option("--region", "-r", default=None, help="AWS region")
@click.option("--state", default=None,
              type=click.Choice(["OK", "ALARM", "INSUFFICIENT_DATA"]),
              help="Alarm state filter or new state")
@click.option("--prefix", default=None, help="Alarm name prefix filter")
@click.option("--namespace", default=None, help="CloudWatch namespace")
@click.option("--metric", default=None, help="Metric name")
@click.option("--threshold", default=None, type=float, help="Alarm threshold")
@click.option("--comparison", default=None,
              type=click.Choice(["GreaterThanThreshold", "GreaterThanOrEqualToThreshold",
                                "LessThanThreshold", "LessThanOrEqualToThreshold"]))
@click.option("--period", default=300, type=int, help="Period in seconds")
@click.option("--evaluation-periods", default=2, type=int, help="Evaluation periods")
@click.option("--statistic", default="Average",
              type=click.Choice(["Average", "Sum", "Minimum", "Maximum", "SampleCount"]))
@click.option("--description", default=None, help="Alarm description")
@click.option("--days", default=7, type=int, help="Days of history to fetch")
@click.option("--reason", default=None, help="Reason for state change")
@click.option("--output", "-o", default="table", type=click.Choice(["table", "json"]))
def main(action, name, names, profile, region, state, prefix, namespace, metric,
         threshold, comparison, period, evaluation_periods, statistic, description,
         days, reason, output):
    """CloudWatch Alarms Manager CLI."""

    if action == "list-alarms":
        result = list_alarms(profile, region, state, prefix, namespace)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"CloudWatch Alarms ({result['count']})")
                table.add_column("Name", style="cyan")
                table.add_column("State", style="white")
                table.add_column("Metric", style="white")
                table.add_column("Namespace", style="dim")
                table.add_column("Threshold", style="yellow")

                for a in result["alarms"]:
                    state_styled = f"[{state_color(a['state'])}]{a['state']}[/{state_color(a['state'])}]"
                    metric_display = a.get("metric", a.get("type", "-"))
                    threshold_display = str(a.get("threshold", "-"))

                    table.add_row(
                        a["name"],
                        state_styled,
                        metric_display,
                        a.get("namespace", "-"),
                        threshold_display
                    )

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "get-alarm":
        if not name:
            console.print("[red]Error: --name required[/red]")
            sys.exit(1)

        result = get_alarm_details(name, profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                state_styled = f"[{state_color(result['state'])}]{result['state']}[/{state_color(result['state'])}]"

                info = f"Name: {result['name']}\n"
                info += f"State: {state_styled}\n"
                info += f"Type: {result['type']}\n"

                if result["type"] == "metric":
                    info += f"Metric: {result['metric']} ({result['namespace']})\n"
                    info += f"Threshold: {result['comparison']} {result['threshold']}\n"
                    info += f"Period: {result['period']}s, Eval Periods: {result['evaluation_periods']}\n"
                    info += f"Statistic: {result['statistic']}\n"
                    if result.get("dimensions"):
                        info += f"Dimensions: {result['dimensions']}\n"
                else:
                    info += f"Rule: {result.get('rule', 'N/A')}\n"

                info += f"\nDescription: {result.get('description', 'N/A')}\n"
                info += f"State Reason: {result.get('state_reason', 'N/A')}\n"
                info += f"Last Updated: {result.get('state_updated', 'N/A')}"

                console.print(Panel(info, title=f"Alarm: {name}"))

                if result.get("alarm_actions"):
                    console.print("\n[bold]Alarm Actions:[/bold]")
                    for action_arn in result["alarm_actions"]:
                        console.print(f"  - {action_arn}")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "alarm-history":
        if not name:
            console.print("[red]Error: --name required[/red]")
            sys.exit(1)

        result = get_alarm_history(name, profile, region, days=days)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"Alarm History: {name} (Last {days} days)")
                table.add_column("Timestamp", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Summary", style="white")

                for h in result["history"]:
                    table.add_row(h["timestamp"], h["type"], h["summary"][:60] + "..." if len(h["summary"]) > 60 else h["summary"])

                console.print(table)
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "create-alarm":
        if not all([name, metric, namespace, threshold, comparison]):
            console.print("[red]Error: --name, --metric, --namespace, --threshold, and --comparison required[/red]")
            sys.exit(1)

        result = create_alarm(
            name=name, metric=metric, namespace=namespace, threshold=threshold,
            comparison=comparison, profile=profile, region=region,
            period=period, evaluation_periods=evaluation_periods,
            statistic=statistic, description=description
        )

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "delete-alarm":
        alarm_names = []
        if name:
            alarm_names = [name]
        elif names:
            alarm_names = [n.strip() for n in names.split(",")]
        else:
            console.print("[red]Error: --name or --names required[/red]")
            sys.exit(1)

        result = delete_alarm(alarm_names, profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "set-state":
        if not name or not state:
            console.print("[red]Error: --name and --state required[/red]")
            sys.exit(1)

        result = set_alarm_state(name, state, reason, profile, region)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                console.print(f"[green]✓ Set {result['alarm']} to {result['new_state']}[/green]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")

    elif action == "list-metrics":
        result = list_metrics(profile, region, namespace)

        if output == "json":
            console.print_json(data=result)
        else:
            if result["success"]:
                table = Table(title=f"CloudWatch Metrics ({result['count']})")
                table.add_column("Namespace", style="cyan")
                table.add_column("Metric", style="white")
                table.add_column("Dimensions", style="dim")

                for m in result["metrics"][:50]:  # Limit display
                    dims = ", ".join([f"{k}={v}" for k, v in m["dimensions"].items()])
                    table.add_row(m["namespace"], m["metric"], dims[:40])

                console.print(table)
                if result["count"] > 50:
                    console.print(f"[dim]... and {result['count'] - 50} more metrics[/dim]")
            else:
                console.print(f"[red]Error: {result['error']}[/red]")


if __name__ == "__main__":
    main()
