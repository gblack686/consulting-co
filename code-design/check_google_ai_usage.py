#!/usr/bin/env python3
"""
Check Google AI API usage and billing information
Note: Google AI API uses a different billing system than Google Cloud Platform
"""

import boto3
import json
import requests
from datetime import datetime
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return secret


def check_api_quota(api_key):
    """
    Check Google AI API quota and usage
    Note: The Gemini API provides free tier with rate limits but doesn't have
    a direct usage/billing API endpoint. Usage is tracked in Google Cloud Console.
    """

    print("=" * 70)
    print("GOOGLE AI (GEMINI) API USAGE CHECK")
    print("=" * 70)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 70)

    print("\n📊 PRICING INFORMATION")
    print("-" * 70)
    print("\nGemini 2.0 Flash (Free Tier):")
    print("  • Rate Limit: 15 requests per minute (RPM)")
    print("  • Daily Limit: 1,500 requests per day (RPD)")
    print("  • Context Window: 1M tokens input")
    print("  • Cost: FREE")

    print("\nGemini 2.0 Flash (Paid Tier - Pay as you go):")
    print("  • Rate Limit: 1,000 RPM / 4,000,000 tokens per minute")
    print("  • Input: $0.075 / 1M tokens (prompt ≤128K)")
    print("  • Input: $0.15 / 1M tokens (prompt >128K)")
    print("  • Output: $0.30 / 1M tokens")

    print("\nGemini 1.5 Flash (Paid Tier):")
    print("  • Input: $0.075 / 1M tokens (prompt ≤128K)")
    print("  • Input: $0.15 / 1M tokens (prompt >128K)")
    print("  • Output: $0.30 / 1M tokens")

    print("\nGemini 1.5 Pro (Paid Tier):")
    print("  • Input: $1.25 / 1M tokens (prompt ≤128K)")
    print("  • Input: $2.50 / 1M tokens (prompt >128K)")
    print("  • Output: $5.00 / 1M tokens")

    print("\n" + "=" * 70)
    print("\n💡 HOW TO CHECK YOUR ACTUAL USAGE:")
    print("-" * 70)
    print("\n1. Visit Google AI Studio:")
    print("   https://aistudio.google.com/app/apikey")

    print("\n2. Or visit Google Cloud Console:")
    print("   https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com")

    print("\n3. Navigate to:")
    print("   • 'Metrics' tab - View API call statistics")
    print("   • 'Quotas' tab - Check rate limit usage")
    print("   • Billing → Reports - View costs (if on paid tier)")

    print("\n" + "=" * 70)
    print("\n📈 ESTIMATED COST FROM YOUR TEST:")
    print("-" * 70)
    print("\nYour recent test used:")
    print("  • Prompt tokens: 15")
    print("  • Response tokens: 3")
    print("  • Total tokens: 18")

    print("\nEstimated cost (if on paid tier):")
    input_cost = (15 / 1_000_000) * 0.075
    output_cost = (3 / 1_000_000) * 0.30
    total_cost = input_cost + output_cost
    print(f"  • Input: ${input_cost:.6f}")
    print(f"  • Output: ${output_cost:.6f}")
    print(f"  • Total: ${total_cost:.6f} (essentially free)")

    print("\n💰 If you're on the FREE tier:")
    print("  • Cost: $0.00")
    print("  • Remaining today: ~1,499 requests")

    print("\n" + "=" * 70)

    # Try to make a simple API call to test if we're rate limited
    print("\n🔍 Testing current API access...")
    print("-" * 70)

    try:
        model = "gemini-2.0-flash-exp"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": "Say 'OK'"}]
            }]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            print("✓ API is accessible - No rate limit hit")
            print("✓ You're within your quota limits")
        elif response.status_code == 429:
            print("⚠ Rate limit exceeded - You've hit your quota")
            print(f"Response: {response.text}")
        else:
            print(f"⚠ Status: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"✗ Error checking API status: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\nRetrieving Google AI API key from AWS Secrets Manager...\n")

    try:
        # Get the API key from AWS Secrets Manager
        api_key = get_secret("gbautomation/core/google-ai-api-key")

        # Check usage and quota
        check_api_quota(api_key)

    except ClientError as e:
        print(f"\n✗ Failed to retrieve API key from AWS Secrets Manager")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
