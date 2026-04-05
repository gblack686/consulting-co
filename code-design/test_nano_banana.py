#!/usr/bin/env python3
"""
Test script for Nano Banana Pro API
Retrieves Google AI API key from AWS Secrets Manager and makes a test API call
"""

import boto3
import json
import requests
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


def test_nano_banana_api(api_key):
    """
    Test the Nano Banana Pro API with a simple image generation request
    Note: This requires an Enterprise Plan subscription for API access
    """

    # API endpoint (example - check official docs for actual endpoint)
    url = "https://nanobananaproapi.org/v1/generate"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Simple test payload
    payload = {
        "prompt": "A beautiful sunset over mountains",
        "width": 1024,
        "height": 1024,
        "quality": "standard"
    }

    print("=" * 60)
    print("NANO BANANA PRO API TEST")
    print("=" * 60)
    print(f"\nEndpoint: {url}")
    print(f"Prompt: {payload['prompt']}")
    print(f"Dimensions: {payload['width']}x{payload['height']}")
    print("\nSending request...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("\n✓ SUCCESS!")
            result = response.json()
            print(f"\nResponse Data:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✗ ERROR!")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n✗ REQUEST FAILED!")
        print(f"Error: {str(e)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\nRetrieving Google AI API key from AWS Secrets Manager...")

    try:
        # Get the API key from AWS Secrets Manager
        api_key = get_secret("gbautomation/core/google-ai-api-key")
        print(f"✓ API key retrieved: {api_key[:20]}...")

        # Test the Nano Banana API
        test_nano_banana_api(api_key)

    except ClientError as e:
        print(f"\n✗ Failed to retrieve API key from AWS Secrets Manager")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
