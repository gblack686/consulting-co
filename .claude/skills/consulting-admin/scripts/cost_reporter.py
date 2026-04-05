"""
AWS Cost Reporter
==================
Pulls monthly spend breakdown and sends a daily Telegram report with
cost totals, top services, month-over-month change, and optimization tips.

Usage:
    python -m scripts.cost_reporter
    python -m scripts.cost_reporter --dry-run
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent

# Optimization rules: if service cost exceeds threshold, add a tip
OPTIMIZATION_RULES = [
    {
        "service": "AWS Secrets Manager",
        "threshold": 5.0,
        "tip": "Secrets Manager is expensive — cache secrets in memory instead of calling get_secret_value on every run.",
    },
    {
        "service": "Amazon Elastic Load Balancing",
        "threshold": 15.0,
        "tip": "Load Balancer cost is high — verify all ALBs/NLBs are actively used. Idle LBs still bill ~$16/mo.",
    },
    {
        "service": "Amazon Lightsail",
        "threshold": 40.0,
        "tip": "Lightsail is the top spend — review all instances. Shut down dev/staging instances when not in use.",
    },
    {
        "service": "AmazonCloudWatch",
        "threshold": 10.0,
        "tip": "CloudWatch logs are accumulating — set retention policies to 7-14 days on non-critical log groups.",
    },
    {
        "service": "Amazon Virtual Private Cloud",
        "threshold": 8.0,
        "tip": "VPC cost is usually NAT Gateway data transfer — consider VPC endpoints for S3/Secrets Manager to eliminate NAT Gateway fees.",
    },
    {
        "service": "EC2 - Other",
        "threshold": 10.0,
        "tip": "EC2-Other includes NAT Gateway and data transfer — VPC endpoints for AWS services can cut this significantly.",
    },
    {
        "service": "Amazon Elastic Container Service",
        "threshold": 10.0,
        "tip": "ECS cost is high — check for over-provisioned task CPU/memory. Fargate Spot can cut costs 70%.",
    },
    {
        "service": "AWS WAF",
        "threshold": 5.0,
        "tip": "WAF charges per Web ACL + rule. Review if all WAF rules are still needed.",
    },
]


def get_cost_breakdown(start: str, end: str) -> tuple[float, list[dict]]:
    import boto3
    ce = boto3.client("ce", region_name="us-east-1")
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    groups = resp["ResultsByTime"][0]["Groups"]
    services = [
        {"name": g["Keys"][0], "amount": float(g["Metrics"]["UnblendedCost"]["Amount"])}
        for g in groups
        if float(g["Metrics"]["UnblendedCost"]["Amount"]) >= 0.01
    ]
    services.sort(key=lambda x: x["amount"], reverse=True)
    total = sum(s["amount"] for s in services)
    return total, services


def build_report(dry_run: bool = False) -> str:
    today = date.today()

    # Current month (MTD) — end must be tomorrow if today is 1st, else today+1
    mtd_start = today.replace(day=1).isoformat()
    mtd_end = (today + timedelta(days=1)).isoformat()

    # Last month full
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1)

    # Two months ago (for trend)
    two_months_start = (last_month_start - timedelta(days=1)).replace(day=1)
    two_months_end = last_month_start

    mtd_total, mtd_services = get_cost_breakdown(mtd_start, mtd_end)
    last_total, last_services = get_cost_breakdown(
        last_month_start.isoformat(), last_month_end.isoformat()
    )
    two_total, _ = get_cost_breakdown(
        two_months_start.isoformat(), two_months_end.isoformat()
    )

    # Month-over-month change
    mom_change = last_total - two_total
    mom_pct = (mom_change / two_total * 100) if two_total else 0
    mom_arrow = "📈" if mom_change > 0 else "📉"

    # Days elapsed / projected
    days_in_month = (last_month_end - last_month_start).days
    days_elapsed = (today - today.replace(day=1)).days or 1
    projected = (mtd_total / days_elapsed) * days_in_month if days_elapsed > 0 else 0

    # Build message
    lines = [
        f"💰 <b>AWS Cost Report — {today.strftime('%b %d, %Y')}</b>",
        "",
        f"<b>This Month (MTD):</b> ${mtd_total:.2f}",
        f"<b>Projected Month-End:</b> ${projected:.2f}",
        f"<b>Last Month ({last_month_start.strftime('%b')}):</b> ${last_total:.2f}",
        f"{mom_arrow} <b>vs. Prior Month:</b> {'+' if mom_change >= 0 else ''}${mom_change:.2f} ({mom_pct:+.1f}%)",
        "",
        "<b>Top Services (Last Month):</b>",
    ]

    for s in last_services[:8]:
        pct = (s["amount"] / last_total * 100) if last_total else 0
        lines.append(f"  • ${s['amount']:.2f} ({pct:.0f}%)  {s['name']}")

    # Optimization tips
    tips = []
    service_map = {s["name"]: s["amount"] for s in last_services}
    for rule in OPTIMIZATION_RULES:
        amt = service_map.get(rule["service"], 0)
        if amt >= rule["threshold"]:
            tips.append(f"  ⚡ {rule['tip']}")

    if tips:
        lines.append("")
        lines.append("<b>Cost Optimization Opportunities:</b>")
        lines.extend(tips)

    return "\n".join(lines)


def run(dry_run: bool = False):
    from . import telegram_client

    print("Fetching AWS cost data...")
    report = build_report(dry_run=dry_run)

    print("\n" + "="*60)
    print(report)
    print("="*60 + "\n")

    if dry_run:
        print("[DRY RUN] Telegram message not sent")
    else:
        telegram_client.send(report)
        print("✓ Report sent to Telegram")


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Send daily AWS cost report to Telegram")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    os.chdir(SKILL_ROOT)
    sys.path.insert(0, str(SKILL_ROOT))
    run(dry_run=args.dry_run)
