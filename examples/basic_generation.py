#!/usr/bin/env python3
"""
Basic 3D Generation Example

This example demonstrates the simplest way to generate a 3D model from an image
using the PrintPal API.

Requirements:
    pip install printpal

Usage:
    1. Set your API key as an environment variable:
       export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    
    2. Run the script with an image:
       python basic_generation.py path/to/your/image.png
    
    3. Or modify IMAGE_PATH below and run directly:
       python basic_generation.py
"""

import os
import sys
from pathlib import Path

from printpal import PrintPal, Quality, Format


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")
IMAGE_PATH = "example_image.png"  # Change this to your image path
OUTPUT_PATH = "output_model.stl"  # Where to save the 3D model


def main():
    # Get image path from command line if provided
    image_path = sys.argv[1] if len(sys.argv) > 1 else IMAGE_PATH
    
    # Check if image exists
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        print("\nUsage: python basic_generation.py <image_path>")
        print("\nSupported formats: PNG, JPG, JPEG, WebP")
        sys.exit(1)
    
    print("PrintPal Basic 3D Generation Example")
    print("=" * 50)
    print(f"Image: {image_path}")
    print(f"Output: {OUTPUT_PATH}")
    print()
    
    # Initialize the client
    client = PrintPal(api_key=API_KEY)
    
    # Check credits first
    credits = client.get_credits()
    print(f"Available credits: {credits.credits}")
    
    if credits.credits < 4:
        print("Error: Not enough credits. Default generation requires 4 credits.")
        print("Purchase credits at: https://printpal.io/buy-credits")
        sys.exit(1)
    
    print()
    print("Starting 3D generation...")
    print("This will take approximately 20-30 seconds for default quality.")
    print()
    
    # Generate and download in one call (simplest method)
    def on_status(status):
        print(f"  Status: {status.status}")
    
    try:
        output_path = client.generate_and_download(
            image_path=image_path,
            output_path=OUTPUT_PATH,
            quality=Quality.DEFAULT,
            format=Format.STL,
            callback=on_status,
        )
        
        print()
        print("Generation complete!")
        print(f"3D model saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")
        
        # Show remaining credits
        credits = client.get_credits()
        print(f"Remaining credits: {credits.credits}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
