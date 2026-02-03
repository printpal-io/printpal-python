#!/usr/bin/env python3
"""
Check Credits and API Status

This example shows how to check your credit balance, API key usage,
and get pricing information.

Requirements:
    pip install printpal

Usage:
    export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    python check_credits.py
"""

import os
from printpal import PrintPalClient


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")


def main():
    print("PrintPal API Status Check")
    print("=" * 50)
    
    # Initialize client
    client = PrintPalClient(api_key=API_KEY)
    
    # Check API health (does not require authentication)
    try:
        health = client.health_check()
        print(f"API Status: {health.get('status', 'unknown')}")
        print(f"API Version: {health.get('version', 'unknown')}")
    except Exception as e:
        print(f"API Health Check Failed: {e}")
        return
    
    print()
    
    # Get credits
    try:
        credits = client.get_credits()
        print("Account Information:")
        print(f"  Username: {credits.username}")
        print(f"  User ID: {credits.user_id}")
        print(f"  Credits: {credits.credits}")
    except Exception as e:
        print(f"Failed to get credits: {e}")
        return
    
    print()
    
    # Get usage stats
    try:
        usage = client.get_usage()
        print("API Key Usage:")
        print(f"  Key Name: {usage.api_key.name}")
        print(f"  Total Requests: {usage.api_key.total_requests}")
        print(f"  Credits Used: {usage.api_key.credits_used}")
        if usage.api_key.last_used:
            print(f"  Last Used: {usage.api_key.last_used}")
    except Exception as e:
        print(f"Failed to get usage: {e}")
    
    print()
    
    # Get pricing
    try:
        pricing = client.get_pricing()
        print("Pricing Information:")
        print("-" * 40)
        print(f"{'Quality':<25} {'Credits':<10} {'Resolution':<15}")
        print("-" * 40)
        for name, tier in pricing.credits.items():
            print(f"{name:<25} {tier.cost:<10} {tier.resolution:<15}")
        print("-" * 40)
        print()
        print(f"Supported formats: {', '.join(pricing.supported_formats)}")
        print(f"Rate limits:")
        for limit_name, limit_value in pricing.rate_limits.items():
            print(f"  {limit_name}: {limit_value}")
    except Exception as e:
        print(f"Failed to get pricing: {e}")
    
    print()
    
    # Calculate what you can generate
    if credits.credits > 0:
        print("What you can generate:")
        tiers = [
            ("Default (256 cubed)", 4),
            ("High (384 cubed)", 6),
            ("Ultra (512 cubed)", 8),
            ("Super (768 cubed)", 20),
            ("Super+Texture (768 cubed)", 40),
            ("SuperPlus (1024 cubed)", 30),
            ("SuperPlus+Texture (1024 cubed)", 50),
        ]
        for name, cost in tiers:
            count = credits.credits // cost
            if count > 0:
                print(f"  {name}: {count} generations")


if __name__ == "__main__":
    main()
