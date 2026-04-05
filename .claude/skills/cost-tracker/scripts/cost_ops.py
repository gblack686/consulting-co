#!/usr/bin/env python3
"""
Cost Operations Module

Core operations for cost tracking.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class UsageEntry:
    """Single usage entry"""
    timestamp: str
    input_tokens: int
    output_tokens: int
    cost: float
    model: str
    task: Optional[str] = None


@dataclass
class BudgetStatus:
    """Current budget status"""
    daily_budget: float
    used_today: float
    remaining: float
    percentage_used: float
    is_over_budget: bool
    is_near_limit: bool


def load_settings() -> Dict[str, Any]:
    """Load skill settings from config file"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def get_usage_log_path() -> Path:
    """Get path to usage log file"""
    return Path(__file__).parent.parent / "data" / "usage_log.json"


def load_usage_log() -> Dict[str, Any]:
    """Load usage log from file"""
    log_path = get_usage_log_path()
    if log_path.exists():
        with open(log_path, "r") as f:
            return json.load(f)
    return {"entries": {}, "daily_totals": {}, "metadata": {}}


def save_usage_log(data: Dict[str, Any]):
    """Save usage log to file"""
    log_path = get_usage_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(data, f, indent=2)


def calculate_cost(input_tokens: int, output_tokens: int, model: str = "haiku") -> float:
    """
    Calculate cost for API call.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (haiku, sonnet, opus)

    Returns:
        Cost in USD
    """
    settings = load_settings()
    pricing = settings.get("pricing", {}).get(model.lower(), {})

    input_rate = pricing.get("input_per_1k", 0.001)
    output_rate = pricing.get("output_per_1k", 0.005)

    input_cost = (input_tokens / 1000) * input_rate
    output_cost = (output_tokens / 1000) * output_rate

    return round(input_cost + output_cost, 6)


def log_usage(input_tokens: int, output_tokens: int, model: str = "haiku", task: Optional[str] = None) -> UsageEntry:
    """
    Log a usage entry.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        task: Optional task description

    Returns:
        UsageEntry
    """
    cost = calculate_cost(input_tokens, output_tokens, model)
    timestamp = datetime.now().isoformat()
    today = datetime.now().strftime("%Y-%m-%d")

    entry = UsageEntry(
        timestamp=timestamp,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        model=model,
        task=task
    )

    # Update log file
    data = load_usage_log()

    if today not in data["entries"]:
        data["entries"][today] = []

    data["entries"][today].append({
        "timestamp": entry.timestamp,
        "input_tokens": entry.input_tokens,
        "output_tokens": entry.output_tokens,
        "cost": entry.cost,
        "model": entry.model,
        "task": entry.task
    })

    # Update daily total
    data["daily_totals"][today] = sum(
        e["cost"] for e in data["entries"][today]
    )

    save_usage_log(data)

    return entry


def get_budget_status() -> BudgetStatus:
    """
    Get current budget status.

    Returns:
        BudgetStatus
    """
    settings = load_settings()
    budget_config = settings.get("budget", {})
    daily_budget = budget_config.get("daily_budget", 1.00)
    alert_threshold = budget_config.get("alert_threshold", 0.80)

    data = load_usage_log()
    today = datetime.now().strftime("%Y-%m-%d")
    used_today = data.get("daily_totals", {}).get(today, 0)

    remaining = max(0, daily_budget - used_today)
    percentage = (used_today / daily_budget) * 100 if daily_budget > 0 else 0

    return BudgetStatus(
        daily_budget=daily_budget,
        used_today=used_today,
        remaining=remaining,
        percentage_used=round(percentage, 2),
        is_over_budget=used_today >= daily_budget,
        is_near_limit=percentage >= (alert_threshold * 100)
    )


def get_daily_entries(date: Optional[str] = None) -> List[UsageEntry]:
    """
    Get usage entries for a specific date.

    Args:
        date: Date string (YYYY-MM-DD) or None for today

    Returns:
        List of UsageEntry
    """
    data = load_usage_log()
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    entries_data = data.get("entries", {}).get(target_date, [])

    return [
        UsageEntry(
            timestamp=e["timestamp"],
            input_tokens=e["input_tokens"],
            output_tokens=e["output_tokens"],
            cost=e["cost"],
            model=e["model"],
            task=e.get("task")
        )
        for e in entries_data
    ]


def get_weekly_summary() -> Dict[str, float]:
    """
    Get weekly cost summary.

    Returns:
        Dict of date -> cost
    """
    data = load_usage_log()
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    summary = {}
    for i in range(7):
        date = (week_ago + timedelta(days=i+1)).strftime("%Y-%m-%d")
        summary[date] = data.get("daily_totals", {}).get(date, 0)

    return summary


def cleanup_old_entries(days_to_keep: int = 30):
    """
    Remove entries older than specified days.

    Args:
        days_to_keep: Number of days to retain
    """
    data = load_usage_log()
    cutoff = datetime.now() - timedelta(days=days_to_keep)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    entries_to_remove = [
        date for date in data.get("entries", {}).keys()
        if date < cutoff_str
    ]

    for date in entries_to_remove:
        del data["entries"][date]
        if date in data.get("daily_totals", {}):
            del data["daily_totals"][date]

    save_usage_log(data)


if __name__ == "__main__":
    # Quick test
    status = get_budget_status()
    print(f"Budget Status:")
    print(f"  Daily Budget: ${status.daily_budget:.2f}")
    print(f"  Used Today: ${status.used_today:.4f}")
    print(f"  Remaining: ${status.remaining:.4f}")
    print(f"  Percentage: {status.percentage_used:.1f}%")
    print(f"  Near Limit: {status.is_near_limit}")
