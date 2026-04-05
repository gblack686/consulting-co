#!/usr/bin/env python3
"""
OpenAI API Usage Checker
Checks OpenAI API usage, costs, and quota information.
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
    """Get OpenAI API key from various sources."""
    # 1. Environment variable
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(SecretId="gbautomation/core/openai-api-key")
            return response["SecretString"]
        except Exception:
            pass

    raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY or store in AWS Secrets Manager.")


def check_openai_usage(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    by_model: bool = False
) -> dict:
    """
    Check OpenAI API usage and billing.

    Args:
        start_date: Start date for usage query
        end_date: End date for usage query
        by_model: Break down usage by model

    Returns:
        dict with usage information
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Set default dates
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    try:
        # First verify the key works with a models request
        models_response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=30
        )

        if models_response.status_code == 401:
            return {
                "status": "error",
                "error": "Invalid API key"
            }
        elif models_response.status_code != 200:
            return {
                "status": "error",
                "error": f"API returned status {models_response.status_code}"
            }

        # Try to get organization info
        org_info = None
        try:
            org_response = requests.get(
                "https://api.openai.com/v1/organization",
                headers=headers,
                timeout=30
            )
            if org_response.status_code == 200:
                org_info = org_response.json()
        except Exception:
            pass

        # Try to get usage data
        # Note: OpenAI's usage API requires organization-level access
        usage_data = None
        try:
            # This endpoint may require specific permissions
            usage_response = requests.get(
                "https://api.openai.com/v1/usage",
                headers=headers,
                params={
                    "date": start_date
                },
                timeout=30
            )
            if usage_response.status_code == 200:
                usage_data = usage_response.json()
        except Exception:
            pass

        # Try the dashboard billing endpoint
        billing_data = None
        try:
            # Check subscription
            sub_response = requests.get(
                "https://api.openai.com/dashboard/billing/subscription",
                headers=headers,
                timeout=30
            )
            if sub_response.status_code == 200:
                billing_data = sub_response.json()
        except Exception:
            pass

        # Try to get current usage
        current_usage = None
        try:
            usage_response = requests.get(
                f"https://api.openai.com/dashboard/billing/usage?start_date={start_date}&end_date={end_date}",
                headers=headers,
                timeout=30
            )
            if usage_response.status_code == 200:
                current_usage = usage_response.json()
        except Exception:
            pass

        # Build result based on available data
        result = {
            "status": "success",
            "api_status": "Active",
            "period": f"{start_date} to {end_date}"
        }

        if billing_data:
            hard_limit = billing_data.get("hard_limit_usd", 0)
            result["monthly_limit"] = hard_limit
            result["plan"] = billing_data.get("plan", {}).get("title", "Unknown")

        if current_usage:
            total_usage = current_usage.get("total_usage", 0) / 100  # Convert cents to dollars
            result["total_cost"] = round(total_usage, 2)
            result["used_display"] = f"${total_usage:.2f}"

            if billing_data and billing_data.get("hard_limit_usd"):
                remaining = max(0, billing_data["hard_limit_usd"] - total_usage)
                percent_used = (total_usage / billing_data["hard_limit_usd"] * 100) if billing_data["hard_limit_usd"] > 0 else 0
                result["remaining"] = round(remaining, 2)
                result["percent_used"] = round(percent_used, 1)
                result["remaining_display"] = f"${remaining:.2f}"
                result["status_display"] = f"{percent_used:.0f}% used"
            else:
                result["remaining_display"] = "No limit set"
                result["status_display"] = f"${total_usage:.2f} used"
                result["percent_used"] = 0
        else:
            # Fallback - key is valid but can't get usage
            result["used_display"] = "See Dashboard"
            result["remaining_display"] = "See Dashboard"
            result["status_display"] = "Active (check dashboard)"
            result["percent_used"] = 0
            result["note"] = "Visit platform.openai.com/usage for detailed usage"

        if org_info:
            result["organization"] = org_info.get("name", "Unknown")

        # Count available models
        if models_response.status_code == 200:
            models = models_response.json().get("data", [])
            gpt4_models = [m for m in models if "gpt-4" in m.get("id", "")]
            result["available_models"] = len(models)
            result["gpt4_access"] = len(gpt4_models) > 0

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
    parser = argparse.ArgumentParser(description="Check OpenAI API usage")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--by-model", action="store_true", help="Break down by model")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_openai_usage(
        start_date=args.start,
        end_date=args.end,
        by_model=args.by_model
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== OpenAI API Usage ===\n")
        for key, value in result.items():
            if not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
