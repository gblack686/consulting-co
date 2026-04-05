#!/usr/bin/env python3
"""
AWS Cost Checker
Checks AWS Cost Explorer for current billing and usage.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def check_aws_costs(
    profile: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    by_service: bool = False,
    forecast: bool = False
) -> dict:
    """
    Check AWS costs using Cost Explorer API.

    Args:
        profile: AWS profile name (optional)
        start_date: Start date for cost query
        end_date: End date for cost query
        by_service: Break down costs by service
        forecast: Include cost forecast

    Returns:
        dict with cost information
    """
    if not BOTO3_AVAILABLE:
        return {
            "status": "error",
            "error": "boto3 not installed. Run: pip install boto3"
        }

    # Set default date range (current month)
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    try:
        # Create session
        session_kwargs = {}
        if profile:
            session_kwargs["profile_name"] = profile
        elif os.environ.get("AWS_PROFILE"):
            session_kwargs["profile_name"] = os.environ["AWS_PROFILE"]

        session = boto3.Session(**session_kwargs)
        ce_client = session.client("ce", region_name="us-east-1")
        sts_client = session.client("sts", region_name="us-east-1")

        # Get account info
        try:
            identity = sts_client.get_caller_identity()
            account_id = identity["Account"]
        except Exception:
            account_id = "Unknown"

        # Get cost and usage
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                "Start": start_date,
                "End": end_date
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost", "UsageQuantity"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}] if by_service else []
        )

        # Parse results
        results = response.get("ResultsByTime", [])
        total_cost = 0.0
        service_costs = {}

        for result in results:
            if by_service:
                for group in result.get("Groups", []):
                    service = group["Keys"][0]
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    service_costs[service] = service_costs.get(service, 0) + cost
                    total_cost += cost
            else:
                total_cost += float(result.get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))

        result_data = {
            "status": "success",
            "account_id": account_id,
            "period": f"{start_date} to {end_date}",
            "total_cost": round(total_cost, 2),
            "currency": "USD",
            "used_display": f"${total_cost:.2f}",
            "remaining_display": "N/A (pay-as-you-go)",
            "status_display": f"MTD ${total_cost:.2f}",
            "percent_used": 0  # AWS is pay-as-you-go
        }

        if by_service:
            # Sort by cost descending
            sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
            result_data["top_services"] = [
                {"service": s, "cost": round(c, 2)}
                for s, c in sorted_services[:10]
            ]

        # Get forecast if requested
        if forecast:
            try:
                # Forecast requires at least 14 days of historical data
                forecast_start = datetime.now().strftime("%Y-%m-%d")
                forecast_end = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")

                forecast_response = ce_client.get_cost_forecast(
                    TimePeriod={
                        "Start": forecast_start,
                        "End": forecast_end
                    },
                    Metric="UNBLENDED_COST",
                    Granularity="MONTHLY"
                )

                result_data["forecast"] = {
                    "end_of_month": round(float(forecast_response.get("Total", {}).get("Amount", 0)), 2),
                    "confidence_level": forecast_response.get("Total", {}).get("Unit", "80%")
                }
            except ClientError as e:
                if "NotEnoughData" in str(e):
                    result_data["forecast"] = {"note": "Not enough historical data for forecast"}
                else:
                    result_data["forecast"] = {"error": str(e)}

        return result_data

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "AccessDeniedException":
            return {
                "status": "error",
                "error": "Access denied. Ensure Cost Explorer is enabled and IAM has ce:GetCostAndUsage permission."
            }
        return {
            "status": "error",
            "error": f"AWS Error: {error_code} - {e.response.get('Error', {}).get('Message', str(e))}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Check AWS costs")
    parser.add_argument("--profile", help="AWS profile name")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--by-service", action="store_true", help="Break down by service")
    parser.add_argument("--forecast", action="store_true", help="Include cost forecast")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = check_aws_costs(
        profile=args.profile,
        start_date=args.start,
        end_date=args.end,
        by_service=args.by_service,
        forecast=args.forecast
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n=== AWS Costs ===\n")
        for key, value in result.items():
            if key == "top_services":
                print("  Top Services:")
                for svc in value:
                    print(f"    - {svc['service']}: ${svc['cost']:.2f}")
            elif key == "forecast":
                print(f"  Forecast: ${value.get('end_of_month', 'N/A')}")
            elif not key.endswith("_display"):
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
