#!/usr/bin/env python3
"""
Async Generation Example

This example demonstrates how to submit a generation request and check
status later, which is useful for:
  - Long-running super resolution generations
  - Web applications that do not want to block
  - Integrating with task queues

Requirements:
    pip install printpal

Usage:
    # Submit a generation
    export PRINTPAL_API_KEY="pp_live_your_api_key_here"
    python async_generation.py submit image.png
    
    # Check status later
    python async_generation.py status <generation_uid>
    
    # Download when ready
    python async_generation.py download <generation_uid>
"""

import os
import sys
import json
from pathlib import Path

from printpal import PrintPal, Quality, Format


# Configuration
API_KEY = os.environ.get("PRINTPAL_API_KEY", "pp_live_your_api_key_here")
JOBS_FILE = "pending_jobs.json"


def load_jobs():
    """Load pending jobs from file."""
    if Path(JOBS_FILE).exists():
        with open(JOBS_FILE) as f:
            return json.load(f)
    return {}


def save_jobs(jobs):
    """Save pending jobs to file."""
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def submit_generation(client, image_path, quality=Quality.DEFAULT):
    """Submit a generation and save the job info."""
    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        return None
    
    print(f"Submitting generation for: {image_path}")
    print(f"Quality: {quality.value}")
    
    result = client.generate_from_image(
        image_path=image_path,
        quality=quality,
        format=Format.STL,
    )
    
    print()
    print("Generation submitted successfully!")
    print(f"  Generation UID: {result.generation_uid}")
    print(f"  Credits used: {result.credits_used}")
    print(f"  Estimated time: {result.estimated_time_seconds} seconds")
    print()
    print("Save this UID to check status later:")
    print(f"  python async_generation.py status {result.generation_uid}")
    
    # Save job info
    jobs = load_jobs()
    jobs[result.generation_uid] = {
        "image": str(image_path),
        "quality": quality.value,
        "credits_used": result.credits_used,
        "status": "submitted",
    }
    save_jobs(jobs)
    
    return result.generation_uid


def check_status(client, generation_uid):
    """Check the status of a generation."""
    print(f"Checking status for: {generation_uid}")
    
    try:
        status = client.get_status(generation_uid)
        
        print()
        print(f"Status: {status.status}")
        print(f"Quality: {status.quality or 'N/A'}")
        print(f"Format: {status.format or 'N/A'}")
        if status.created_at:
            print(f"Created: {status.created_at}")
        if status.external_state:
            print(f"External state: {status.external_state}")
        
        if status.is_completed:
            print()
            print("Generation is complete! Download with:")
            print(f"  python async_generation.py download {generation_uid}")
            
            # Update job info
            jobs = load_jobs()
            if generation_uid in jobs:
                jobs[generation_uid]["status"] = "completed"
                save_jobs(jobs)
        
        elif status.is_failed:
            print()
            print("Generation has failed.")
            
            jobs = load_jobs()
            if generation_uid in jobs:
                jobs[generation_uid]["status"] = "failed"
                save_jobs(jobs)
        
        else:
            print()
            print("Generation is still processing...")
            print("Check again later with the same command.")
        
        return status
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def download_model(client, generation_uid, output_path=None):
    """Download a completed model."""
    print(f"Downloading model: {generation_uid}")
    
    # Get status first to check if complete
    status = client.get_status(generation_uid)
    
    if not status.is_completed:
        print(f"Error: Generation is not complete (status: {status.status})")
        return None
    
    # Determine output path
    if not output_path:
        jobs = load_jobs()
        if generation_uid in jobs:
            original_image = jobs[generation_uid].get("image", "")
            stem = Path(original_image).stem if original_image else generation_uid[:8]
            output_path = f"{stem}_3d.{status.format or 'stl'}"
        else:
            output_path = f"model_{generation_uid[:8]}.{status.format or 'stl'}"
    
    try:
        path = client.download(generation_uid, output_path=output_path)
        
        print()
        print("Download complete!")
        print(f"  Saved to: {path}")
        print(f"  File size: {path.stat().st_size:,} bytes")
        
        # Update job info
        jobs = load_jobs()
        if generation_uid in jobs:
            jobs[generation_uid]["status"] = "downloaded"
            jobs[generation_uid]["output"] = str(path)
            save_jobs(jobs)
        
        return path
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def list_jobs():
    """List all pending jobs."""
    jobs = load_jobs()
    
    if not jobs:
        print("No pending jobs.")
        return
    
    print("Pending Jobs:")
    print("-" * 70)
    print(f"{'UID':<40} {'Status':<12} {'Image'}")
    print("-" * 70)
    
    for uid, info in jobs.items():
        status = info.get("status", "unknown")
        image = Path(info.get("image", "N/A")).name
        print(f"{uid:<40} {status:<12} {image}")


def main():
    if len(sys.argv) < 2:
        print("PrintPal Async Generation")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python async_generation.py submit <image_path> [quality]")
        print("  python async_generation.py status <generation_uid>")
        print("  python async_generation.py download <generation_uid> [output_path]")
        print("  python async_generation.py list")
        print()
        print("Quality options: default, high, ultra, super, superplus")
        return
    
    command = sys.argv[1].lower()
    client = PrintPal(api_key=API_KEY)
    
    if command == "submit":
        if len(sys.argv) < 3:
            print("Error: Image path required")
            return
        
        image_path = sys.argv[2]
        quality = Quality.DEFAULT
        
        if len(sys.argv) > 3:
            quality_map = {
                "default": Quality.DEFAULT,
                "high": Quality.HIGH,
                "ultra": Quality.ULTRA,
                "super": Quality.SUPER,
                "superplus": Quality.SUPERPLUS,
            }
            quality = quality_map.get(sys.argv[3].lower(), Quality.DEFAULT)
        
        submit_generation(client, image_path, quality)
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("Error: Generation UID required")
            return
        check_status(client, sys.argv[2])
    
    elif command == "download":
        if len(sys.argv) < 3:
            print("Error: Generation UID required")
            return
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        download_model(client, sys.argv[2], output_path)
    
    elif command == "list":
        list_jobs()
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: submit, status, download, list")


if __name__ == "__main__":
    main()
