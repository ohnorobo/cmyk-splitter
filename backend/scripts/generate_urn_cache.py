"""
Generate cached response for default urn.png image.
Run this script to create/update the cached response.

Usage: python -m backend.scripts.generate_urn_cache
"""
import json
import asyncio
from pathlib import Path
from backend.api.routes import process_image
from fastapi import UploadFile

async def generate_cache():
    # Path to urn.png
    urn_path = Path(__file__).parent.parent.parent / "static" / "urn.png"

    if not urn_path.exists():
        print(f"❌ Error: urn.png not found at {urn_path}")
        return

    # Read the file
    with open(urn_path, "rb") as f:
        file_content = f.read()

    # Create UploadFile-like object
    class FakeUploadFile:
        def __init__(self, content, filename):
            self.content = content
            self.filename = filename
            self.content_type = "image/png"

        async def read(self):
            return self.content

    upload = FakeUploadFile(file_content, "urn.png")

    print("Processing urn.png with default parameters...")
    print("  divisor_c=50, divisor_m=50, divisor_y=50, divisor_k=25")
    print("  skip_paths_longer_than=25")

    # Process with default parameters
    result = await process_image(
        image=upload,
        divisor_c=50,
        divisor_m=50,
        divisor_y=50,
        divisor_k=25,
        skip_paths_longer_than=25
    )

    # Save to cache file
    cache_dir = Path(__file__).parent.parent / "cache"
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "urn_default.json"

    with open(cache_file, "w") as f:
        json.dump(result, f)

    print(f"✓ Cached response saved to {cache_file}")
    print(f"  Response size: {len(json.dumps(result)):,} bytes")
    print(f"  Cache file size: {cache_file.stat().st_size:,} bytes")

if __name__ == "__main__":
    asyncio.run(generate_cache())
