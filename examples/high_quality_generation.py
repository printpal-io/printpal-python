#!/usr/bin/env python3
"""
High Quality 3D Generation Example

This example demonstrates how to generate high-resolution 3D models using
the super and superplus quality levels.

Quality Levels:
    - default: 256 cubed resolution, 4 credits, ~20 seconds
    - high: 384 cubed resolution, 6 credits, ~30 seconds
    - ultra: 512 cubed resolution, 8 credits, ~60 seconds
    - super: 768 cubed resolution, 20 credits, ~3 minutes
    - super_texture: 768 cubed with textures, 40 credits, ~6 minutes
    - superplus: 1024 cubed resolution, 30 credits, ~4 minutes
    - superplus_texture: 1024 cubed with textures, 50 credits, ~12 minutes

Requirements:
    pip install printpal

Usage:
    export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    python high_quality_generation.py path/to/image.png
"""

import os
import sys
from pathlib import Path

from printpal import PrintPalClient, Quality, Format, CREDIT_COSTS, ESTIMATED_TIMES


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")
IMAGE_PATH = "example_image.png"
QUALITY = Quality.SUPER  # Change to SUPERPLUS for highest resolution
OUTPUT_FORMAT = Format.STL


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else IMAGE_PATH
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    # Get quality from second argument if provided
    quality = QUALITY
    if len(sys.argv) > 2:
        quality_arg = sys.argv[2].lower()
        quality_map = {
            "default": Quality.DEFAULT,
            "high": Quality.HIGH,
            "ultra": Quality.ULTRA,
            "super": Quality.SUPER,
            "super_texture": Quality.SUPER_TEXTURE,
            "superplus": Quality.SUPERPLUS,
            "superplus_texture": Quality.SUPERPLUS_TEXTURE,
        }
        quality = quality_map.get(quality_arg, QUALITY)
    
    credits_needed = CREDIT_COSTS[quality]
    estimated_time = ESTIMATED_TIMES[quality]
    
    print("PrintPal High Quality 3D Generation")
    print("=" * 50)
    print(f"Image: {image_path}")
    print(f"Quality: {quality.value}")
    print(f"Credits needed: {credits_needed}")
    print(f"Estimated time: {estimated_time} seconds ({estimated_time // 60} minutes)")
    print()
    
    client = PrintPalClient(api_key=API_KEY)
    
    # Check credits
    credits = client.get_credits()
    print(f"Available credits: {credits.credits}")
    
    if credits.credits < credits_needed:
        print(f"Error: Not enough credits. Need {credits_needed}, have {credits.credits}.")
        print("Purchase credits at: https://printpal.io/buy-credits")
        sys.exit(1)
    
    print()
    print("Starting high-quality 3D generation...")
    print(f"This will take approximately {estimated_time // 60} minutes.")
    print()
    
    # Start generation
    result = client.generate_from_image(
        image_path=image_path,
        quality=quality,
        format=OUTPUT_FORMAT,
    )
    
    print(f"Generation submitted!")
    print(f"  Generation UID: {result.generation_uid}")
    print(f"  Credits used: {result.credits_used}")
    print(f"  Credits remaining: {result.credits_remaining}")
    print()
    
    # Wait with progress updates
    poll_count = 0
    
    def on_status(status):
        nonlocal poll_count
        poll_count += 1
        external = f" (external: {status.external_state})" if status.external_state else ""
        print(f"  [{poll_count}] Status: {status.status}{external}")
    
    print("Waiting for completion...")
    try:
        status = client.wait_for_completion(
            result.generation_uid,
            poll_interval=10,  # Check every 10 seconds for high-quality
            callback=on_status,
        )
        
        print()
        print("Generation complete!")
        
        # Download the model
        output_name = f"hq_model_{quality.value}.{OUTPUT_FORMAT.value}"
        output_path = client.download(result.generation_uid, output_path=output_name)
        
        print(f"3D model saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
