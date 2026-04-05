#!/usr/bin/env python3
"""
Check Nano Banana Pro usage and billing
Opens the billing dashboard since there's no API endpoint for usage checking
"""

import webbrowser
from datetime import datetime

def display_usage_info():
    """Display Nano Banana Pro usage and billing information"""

    print("=" * 70)
    print("NANO BANANA PRO - USAGE & BILLING CHECK")
    print("=" * 70)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 70)

    print("\n📊 CREDIT USAGE INFORMATION")
    print("-" * 70)
    print("\nNano Banana Pro uses a credit-based system:")
    print("  • ~10 credits per image (varies by complexity)")
    print("  • Failed generations receive automatic refund")
    print("  • One-time credits never expire")
    print("  • Subscription credits reset monthly/annually")

    print("\n" + "=" * 70)
    print("\n💰 SUBSCRIPTION PLANS (Annual)")
    print("-" * 70)

    plans = [
        {
            "name": "Basic",
            "price": "$9.90/month ($118.80/year)",
            "credits": "6,000 credits/year (~50 images/month)",
            "features": ["Commercial license", "1080p HD", "No watermark"]
        },
        {
            "name": "Standard",
            "price": "$19.90/month ($238.80/year)",
            "credits": "24,000 credits/year (~200 images/month)",
            "features": ["All Basic features", "Priority queue", "Priority support"]
        },
        {
            "name": "Pro",
            "price": "$29.90/month ($358.80/year)",
            "credits": "72,000 credits/year (~600 images/month)",
            "features": ["All Standard features", "Fastest speed", "Expert support"]
        },
        {
            "name": "Enterprise",
            "price": "$49.50/month ($594/year)",
            "credits": "30,000 credits/month",
            "features": ["All Pro features", "Full API access", "Batch generation", "2hr support"]
        }
    ]

    for plan in plans:
        print(f"\n{plan['name']}:")
        print(f"  Price: {plan['price']}")
        print(f"  Credits: {plan['credits']}")
        for feature in plan['features']:
            print(f"  • {feature}")

    print("\n" + "=" * 70)
    print("\n📦 ONE-TIME CREDIT PACKS (Never Expire)")
    print("-" * 70)

    packs = [
        ("Starter Pack", "$19.90", "1,000 credits", "~100 images"),
        ("Growth Pack", "$39.90", "3,000 credits", "~300 images"),
        ("Professional Pack", "$99.90", "8,000 credits", "~800 images"),
        ("Max Pack", "$199.90", "20,000 credits", "~2,000 images")
    ]

    for name, price, credits, images in packs:
        print(f"\n{name}:")
        print(f"  {price} → {credits} → {images}")

    print("\n" + "=" * 70)
    print("\n📈 ESTIMATED HOURLY USAGE")
    print("-" * 70)

    # Estimations based on different usage patterns
    scenarios = [
        ("Light usage", "6 images/hour", "~60 credits", "$0.12-$0.50"),
        ("Moderate usage", "20 images/hour", "~200 credits", "$0.40-$1.66"),
        ("Heavy usage", "60 images/hour", "~600 credits", "$1.20-$5.00"),
    ]

    print("\nIf you've been generating for 1 hour:")
    for scenario, images, credits, cost in scenarios:
        print(f"\n  {scenario}: {images}")
        print(f"    Credits used: {credits}")
        print(f"    Estimated value: {cost}")

    print("\n" + "=" * 70)
    print("\n🌐 CHECK YOUR ACTUAL USAGE")
    print("-" * 70)
    print("\nUnfortunately, Nano Banana Pro API doesn't provide a")
    print("programmatic endpoint to check usage/billing.")
    print("\nYou need to check via the web dashboard:")

    print("\n1. Settings & Billing Dashboard:")
    print("   https://nanobananapro.photo/settings/billing")

    print("\n2. Account Settings:")
    print("   https://nanobananapro.photo/settings")

    print("\n3. Main Dashboard:")
    print("   https://nanobananapro.photo/dashboard")

    print("\n" + "=" * 70)
    print("\n🔓 Opening Billing Dashboard...")
    print("-" * 70)

    # Open the billing dashboard
    billing_url = "https://nanobananapro.photo/settings/billing"
    try:
        print(f"\nOpening: {billing_url}")
        webbrowser.open(billing_url)
        print("✓ Browser opened successfully")
        print("\nPlease sign in to view:")
        print("  • Current credit balance")
        print("  • Usage history")
        print("  • Billing statements")
        print("  • Active subscription details")
    except Exception as e:
        print(f"✗ Error opening browser: {e}")
        print(f"\nPlease manually visit: {billing_url}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    display_usage_info()
