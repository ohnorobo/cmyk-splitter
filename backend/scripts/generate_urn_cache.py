"""
Generate cached response for default urn.png image.
Run this script to create/update the cached response.

Usage: python -m backend.scripts.generate_urn_cache
"""
import json
from pathlib import Path
from PIL import Image
from backend.services.process_image import process_image_to_svg

def generate_cache():
    # Path to urn.png
    urn_path = Path(__file__).parent.parent.parent / "frontend" / "static" / "urn.png"

    if not urn_path.exists():
        print(f"❌ Error: urn.png not found at {urn_path}")
        return

    # Load the image
    pil_image = Image.open(urn_path)

    print("Processing urn.png with default parameters...")
    print("  divisor_c=50, divisor_m=50, divisor_y=50, divisor_k=25")
    print("  skip_paths_longer_than=25")

    # Process with default parameters using service layer
    result = process_image_to_svg(
        pil_image=pil_image,
        divisor_c=50,
        divisor_m=50,
        divisor_y=50,
        divisor_k=25,
        skip_paths_longer_than=25
    )

    # Wrap result in API response format
    api_response = {
        "status": "completed",
        "result": result
    }

    # Save to frontend cache file (no backend dependency)
    cache_dir = Path(__file__).parent.parent.parent / "frontend" / "cache"
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "urn_default.json"

    with open(cache_file, "w") as f:
        json.dump(api_response, f)

    print(f"✓ Cached response saved to {cache_file}")
    print(f"  Response size: {len(json.dumps(api_response)):,} bytes")
    print(f"  Cache file size: {cache_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    generate_cache()
