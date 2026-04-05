#!/usr/bin/env python3
"""
Apify Usage Checker
Checks Apify platform credits and actor run usage.
"""

import argparse
import json
import os
from typing import Optional

import requests

# Try to import boto3 for AWS Secrets Manager
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def get_api_token() -> str:
    """Get Apify API token from various sources."""
    # 1. Environment variable
    if os.environ.get("APIFY_API_TOKEN"):
        return os.environ["APIFY_API_TOKEN"]
    if os.environ.get("APIFY_TOKEN"):
        return os.environ["APIFY_TOKEN"]

    # 2. AWS Secrets Manager
    if BOTO3_AVAILABLE:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(SecretId="gbautomation/core/apify-api-token")
            return response["SecretString"]
        except Exception:
            pass

    raise ValueError("No Apify API token found. Set APIFY_API_TOKEN or store in AWS Secrets Manager.")


def check_apify_usage() -> dict:
    """
    Check Apify platform credits and usage.

    Returns:
        dict with usage information
    """
    api_token = get_api_token()

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        # Get user info and subscription
        response = requests.get(
            f"https://api.apify.com/v2/users/me?token={api_token}",
            timeout=30
        )

        if response.status_code == 200:
            data = response.json().get("data", {})

            # Extract relevant info
            username = data.get("username", "Unknown")
            email = data.get("email", "Unknown")
            plan = data.get("plan", {})

            # Get usage limits
            monthly_usage_credits = plan.get("monthlyUsageCreditsUsd", 0)
            usage_credits_used = data.get("currentBillingPeriod", {}).get("usageCreditsUsedUsd", 0)

            # Calculate remaining
            remaining = max(0, monthly_usage_credits - usage_credits_used)
            percent_used = (usage_credits_used / monthly_usage_credits * 100) if monthly_usage_credits > 0 else 0

            result = {
                "status": "success",
                "username": username,
                "email": email,
                "plan_name": plan.get("name", "Unknown"),
                "monthly_credits": monthly_usage_credits,
                "credits_used": round(usage_credits_used, 2),
                "credits_remaining": round(remaining, 2),
                "percent_used": round(percent_used, 1),
                "used_display": f"${usage_credits_used:.2f}",
                "remaining_display": f"${remaining:.2f}",
                "status_display": f"{percent_used:.0f}% used",
            }

            # Get actor runs info
            try:
                runs_response = requests.get(
                    f"https://api.apify.com/v2/actor-runs?token={api_token}&limit=1",
                    timeout=30
                )
                if runs_response.status_code == 200:
                    runs_data = runs_response.json().get("data", {})
                    result["total_runs"] = runs_data.get("total", 0)
            except Exception:
                pass

            # Get billing period info
            billing_period = data.get("currentBillingPeriod", {})
            if billing_period:
                result["billing_period_start"] = billing_period.get("startedAt", "")[:10]
                result["billing_period_end"] = billing_period.get("endedAt", "")[:10] if billing_period.get("endedAt") else "Ongoing"

            return result

        elif response.status_code == 401:
            return {
                "status": "error",
                "error": "Invalid API token"
            }
        else:
            return {
                "status": "error",
                "error": f"API returned status {response.status_code}"
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
    parser = argparse.ArgumentParser(description="Check Apify platform usage")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_apify_usage()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== Apify Usage ===\n")
        for key, value in result.items():
            if not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
