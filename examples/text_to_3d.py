#!/usr/bin/env python3
"""
Text to 3D Generation Example

This example demonstrates how to generate 3D models from text prompts.
The API first converts your text to an image, then generates a 3D model.

Note: Text-to-3D is only available for default, high, and ultra quality levels.
Super resolution requires an image input.

Requirements:
    pip install printpal

Usage:
    export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    python text_to_3d.py "a cute robot toy"
"""

import os
import sys

from printpal import PrintPalClient, Quality, Format


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")
DEFAULT_PROMPT = "a small castle with towers"


def main():
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_PROMPT
    
    print("PrintPal Text to 3D Generation")
    print("=" * 50)
    print(f"Prompt: {prompt}")
    print()
    
    # Initialize client
    client = PrintPalClient(api_key=API_KEY)
    
    # Check credits
    credits = client.get_credits()
    print(f"Available credits: {credits.credits}")
    
    if credits.credits < 4:
        print("Error: Not enough credits. Minimum 4 credits required.")
        print("Purchase credits at: https://printpal.io/buy-credits")
        sys.exit(1)
    
    print()
    print("Starting text-to-3D generation...")
    print("This process:")
    print("  1. Converts your text to an image")
    print("  2. Generates a 3D model from the image")
    print()
    
    # Generate from text prompt
    result = client.generate_from_prompt(
        prompt=prompt,
        quality=Quality.DEFAULT,
        format=Format.GLB,
    )
    
    print(f"Generation submitted!")
    print(f"  Generation UID: {result.generation_uid}")
    print(f"  Credits used: {result.credits_used}")
    print()
    
    # Wait for completion
    def on_status(status):
        print(f"  Status: {status.status}")
    
    print("Waiting for completion...")
    try:
        status = client.wait_for_completion(
            result.generation_uid,
            poll_interval=5,
            callback=on_status,
        )
        
        print()
        print("Generation complete!")
        
        # Create safe filename from prompt
        safe_name = "".join(c if c.isalnum() or c in "- " else "" for c in prompt)
        safe_name = safe_name[:30].strip().replace(" ", "_")
        output_name = f"text_to_3d_{safe_name}.glb"
        
        # Download the model
        output_path = client.download(result.generation_uid, output_path=output_name)
        
        print(f"3D model saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
