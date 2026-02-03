#!/usr/bin/env python3
"""
Batch 3D Generation Example

This example demonstrates how to generate 3D models from multiple images
in batch, processing them in parallel for efficiency.

Requirements:
    pip install printpal

Usage:
    export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    python batch_generation.py image1.png image2.png image3.png
    
    Or process a directory:
    python batch_generation.py ./images/
"""

import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from printpal import PrintPal, Quality, Format, CREDIT_COSTS


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")
QUALITY = Quality.DEFAULT
OUTPUT_FORMAT = Format.STL
MAX_CONCURRENT = 5  # Maximum concurrent generations (API limit)
OUTPUT_DIR = "batch_output"


def get_images_from_args():
    """Get image paths from command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python batch_generation.py <image1> [image2] [image3] ...")
        print("       python batch_generation.py <directory>")
        sys.exit(1)
    
    images = []
    supported_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_dir():
            # Get all images from directory
            for ext in supported_extensions:
                images.extend(path.glob(f"*{ext}"))
                images.extend(path.glob(f"*{ext.upper()}"))
        elif path.is_file():
            if path.suffix.lower() in supported_extensions:
                images.append(path)
            else:
                print(f"Warning: Skipping unsupported file: {path}")
        else:
            print(f"Warning: Path not found: {path}")
    
    return images


def process_image(client, image_path, output_dir):
    """Process a single image and return the result."""
    output_name = f"{image_path.stem}.{OUTPUT_FORMAT.value}"
    output_path = output_dir / output_name
    
    try:
        # Submit generation
        result = client.generate_from_image(
            image_path=image_path,
            quality=QUALITY,
            format=OUTPUT_FORMAT,
        )
        
        # Wait and download
        client.wait_for_completion(result.generation_uid, poll_interval=5)
        client.download(result.generation_uid, output_path=output_path)
        
        return {
            "image": str(image_path),
            "output": str(output_path),
            "status": "success",
            "credits_used": result.credits_used,
        }
        
    except Exception as e:
        return {
            "image": str(image_path),
            "output": None,
            "status": "failed",
            "error": str(e),
        }


def main():
    images = get_images_from_args()
    
    if not images:
        print("No valid images found.")
        sys.exit(1)
    
    credits_per_image = CREDIT_COSTS[QUALITY]
    total_credits_needed = len(images) * credits_per_image
    
    print("PrintPal Batch 3D Generation")
    print("=" * 50)
    print(f"Images to process: {len(images)}")
    print(f"Quality: {QUALITY.value}")
    print(f"Credits per image: {credits_per_image}")
    print(f"Total credits needed: {total_credits_needed}")
    print()
    
    # Initialize client
    client = PrintPal(api_key=API_KEY)
    
    # Check credits
    credits = client.get_credits()
    print(f"Available credits: {credits.credits}")
    
    if credits.credits < total_credits_needed:
        print(f"Warning: May not have enough credits for all images.")
        print(f"  Need: {total_credits_needed}, Have: {credits.credits}")
        print(f"  Can process: {credits.credits // credits_per_image} images")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(0)
    
    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()
    
    # Process images
    print("Starting batch processing...")
    start_time = time.time()
    results = []
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = {
            executor.submit(process_image, client, img, output_dir): img
            for img in images
        }
        
        for future in as_completed(futures):
            image = futures[future]
            result = future.result()
            results.append(result)
            
            status_symbol = "[OK]" if result["status"] == "success" else "[FAIL]"
            print(f"  {status_symbol} {image.name}")
    
    # Summary
    elapsed = time.time() - start_time
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    credits_used = sum(r.get("credits_used", 0) for r in results)
    
    print()
    print("=" * 50)
    print("Batch Processing Complete")
    print("=" * 50)
    print(f"Total images: {len(images)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Credits used: {credits_used}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Output directory: {output_dir}")
    
    # Show failed images
    if failed > 0:
        print()
        print("Failed images:")
        for result in results:
            if result["status"] == "failed":
                print(f"  - {result['image']}: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
