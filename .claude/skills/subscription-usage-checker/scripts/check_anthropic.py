#!/usr/bin/env python3
"""
Anthropic API Usage Checker
Checks Claude API usage, costs, and quota information.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Optional

import requests

# Try to import boto3 for AWS Secrets Manager
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_api_key() -> str:
    """Get Anthropic API key from various sources."""
    # 1. Environment variable
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(SecretId="gbautomation/core/anthropic-api-key")
            return response["SecretString"]
        except Exception:
            pass

    raise ValueError("No Anthropic API key found. Set ANTHROPIC_API_KEY or store in AWS Secrets Manager.")


def check_anthropic_usage(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    """
    Check Anthropic API usage and return usage data.

    Note: Anthropic's usage API may have different endpoints based on plan type.
    This uses the standard billing/usage endpoints.
    """
    api_key = get_api_key()

    # Set default date range (current billing period)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    # Try to get usage from the API
    # Note: The exact endpoint depends on your plan (API vs Claude Code Max)
    try:
        # For API users - check organization usage
        response = requests.get(
            "https://api.anthropic.com/v1/organizations/me",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            org_data = response.json()

            # Try to get usage data
            usage_response = requests.get(
                "https://api.anthropic.com/v1/usage",
                headers=headers,
                params={
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=30
            )

            if usage_response.status_code == 200:
                usage_data = usage_response.json()

                total_cost = usage_data.get("total_cost", 0)
                total_tokens = usage_data.get("total_tokens", 0)

                # Calculate based on typical plan limits
                monthly_limit = 100.0  # Adjust based on your plan

                return {
                    "status": "success",
                    "period": f"{start_date} to {end_date}",
                    "total_cost": total_cost,
                    "total_tokens": total_tokens,
                    "monthly_limit": monthly_limit,
                    "remaining": monthly_limit - total_cost,
                    "percent_used": (total_cost / monthly_limit * 100) if monthly_limit > 0 else 0,
                    "used_display": f"${total_cost:.2f}",
                    "remaining_display": f"${monthly_limit - total_cost:.2f}",
                    "status_display": f"{total_cost/monthly_limit*100:.0f}% used" if monthly_limit > 0 else "Active"
                }

        # If we can't get usage data, try a simple validation
        # Make a minimal API call to verify the key works
        test_response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=30
        )

        if test_response.status_code == 200:
            return {
                "status": "success",
                "api_status": "Active",
                "message": "API key is valid. Usage data not available via API.",
                "note": "Check console.anthropic.com for detailed usage",
                "used_display": "See Console",
                "remaining_display": "See Console",
                "status_display": "Active (check console)",
                "percent_used": 0
            }
        elif test_response.status_code == 401:
            return {
                "status": "error",
                "error": "Invalid API key"
            }
        elif test_response.status_code == 429:
            return {
                "status": "success",
                "api_status": "Rate Limited",
                "message": "API key valid but rate limited",
                "used_display": "Rate Limited",
                "remaining_display": "Retry later",
                "status_display": "Rate limited",
                "percent_used": 100
            }
        else:
            # For Claude Code Max users, the key format is different
            # Check if it's an OAuth token
            if api_key.startswith("sk-ant-oat"):
                return {
                    "status": "success",
                    "plan": "Claude Code (OAuth)",
                    "message": "Claude Code Max plan detected. Usage tracked at console.anthropic.com",
                    "used_display": "See Console",
                    "remaining_display": "Unlimited*",
                    "status_display": "Max Plan Active",
                    "percent_used": 0,
                    "note": "*Subject to fair use policy"
                }

            return {
                "status": "error",
                "error": f"API returned status {test_response.status_code}"
            }

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
    parser = argparse.ArgumentParser(description="Check Anthropic API usage")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_anthropic_usage(start_date=args.start, end_date=args.end)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Anthropic API Usage ===\n")
        for key, value in result.items():
            if not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
