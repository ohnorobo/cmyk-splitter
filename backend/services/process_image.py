"""Image processing service for CMYK conversion and SVG generation."""

from PIL import Image
import os
from datetime import datetime
from typing import Dict, Tuple

from backend.services.cmyk_splitter import CMYKSplitter
from backend.services.stringy_plotter import StringyPlotter
from backend.services.svg_combiner import SVGCombiner
from backend.config import DEBUG, DEBUG_DIR

# Maximum dimension for image processing (to improve performance)
# Set to large value to effectively disable resizing (quality > speed for now)
MAX_IMAGE_DIMENSION = 10000


def resize_image_if_needed(image: Image.Image, max_dimension: int = MAX_IMAGE_DIMENSION) -> Image.Image:
    """
    Resize image if either dimension exceeds max_dimension, maintaining aspect ratio.

    Args:
        image: PIL Image to potentially resize
        max_dimension: Maximum width or height in pixels

    Returns:
        Resized PIL Image (or original if already small enough)
    """
    width, height = image.size

    # Check if resize is needed
    if width <= max_dimension and height <= max_dimension:
        return image

    # Calculate new dimensions maintaining aspect ratio
    if width > height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))

    # Resize using high-quality Lanczos resampling
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    print(f"  Resized from {width}x{height} to {new_width}x{new_height} for faster processing")

    return resized


def process_image_to_svg(
    pil_image: Image.Image,
    divisor_c: int = 50,
    divisor_m: int = 50,
    divisor_y: int = 50,
    divisor_k: int = 25,
    skip_paths_longer_than: int = 25,
    threshold_c: int = 128,
    threshold_m: int = 128,
    threshold_y: int = 90,
    threshold_k: int = 128,
) -> Dict:
    """
    Process a PIL Image into CMYK stringy SVG layers.

    Args:
        pil_image: PIL Image in RGB mode
        divisor_c: Sampling divisor for cyan channel (default: 50)
        divisor_m: Sampling divisor for magenta channel (default: 50)
        divisor_y: Sampling divisor for yellow channel (default: 50)
        divisor_k: Sampling divisor for black channel (default: 25)
        skip_paths_longer_than: Max distance for continuous lines (default: 25)
        threshold_c: Cyan threshold 0-255, higher = more ink (default: 128)
        threshold_m: Magenta threshold 0-255, higher = more ink (default: 128)
        threshold_y: Yellow threshold 0-255, higher = more ink (default: 90)
        threshold_k: Black threshold 0-255, higher = more ink (default: 128)

    Returns:
        Dict with combined_svg and metadata
    """
    # Store original dimensions
    original_width, original_height = pil_image.size

    print(f"Processing image: {original_width}x{original_height}")

    # Convert to RGB if not already
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')

    # Resize if needed for faster processing
    pil_image = resize_image_if_needed(pil_image)
    processing_width, processing_height = pil_image.size

    # Split into CMYK channels (with thresholding)
    splitter = CMYKSplitter()
    channels = splitter.split_channels(
        pil_image,
        threshold_c=threshold_c,
        threshold_m=threshold_m,
        threshold_y=threshold_y,
        threshold_k=threshold_k
    )

    # Debug: Save raw CMYK channels and bilevel images
    if DEBUG:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert RGB to CMYK with GCR for debug output
        c, m, y, k = splitter.rgb_to_cmyk_with_gcr(pil_image)

        print(f"Saving debug files to {DEBUG_DIR}/")

        # Save raw CMYK channels (grayscale, 0=full ink, 255=no ink)
        c.save(os.path.join(DEBUG_DIR, f"{timestamp}_raw_cyan.png"))
        m.save(os.path.join(DEBUG_DIR, f"{timestamp}_raw_magenta.png"))
        y.save(os.path.join(DEBUG_DIR, f"{timestamp}_raw_yellow.png"))
        k.save(os.path.join(DEBUG_DIR, f"{timestamp}_raw_black.png"))
        print(f"  Saved raw CMYK channel images")

        # Save bilevel channel images
        for channel_name, channel_img in channels.items():
            debug_path = os.path.join(DEBUG_DIR, f"{timestamp}_bilevel_{channel_name}.png")
            channel_img.save(debug_path)
            print(f"  Saved bilevel {channel_name} image: {debug_path}")

    # Process each channel with StringyPlotter
    channel_configs = {
        "cyan": divisor_c,
        "magenta": divisor_m,
        "yellow": divisor_y,
        "black": divisor_k,
    }

    svg_results = {}
    for channel_name, divisor in channel_configs.items():
        if DEBUG:
            print(f"Processing {channel_name} channel (divisor={divisor})...")

        # Using StringyPlotter for continuous line drawings
        plotter = StringyPlotter(
            divisor=divisor,
            skip_paths_longer_than=skip_paths_longer_than
        )
        svg_string = plotter.process_image(channels[channel_name])
        svg_results[f"{channel_name}_svg"] = svg_string

        # Debug: Save SVG files
        if DEBUG:
            svg_debug_path = os.path.join(DEBUG_DIR, f"{timestamp}_{channel_name}.svg")
            with open(svg_debug_path, 'w') as f:
                f.write(svg_string)
            print(f"  Saved {channel_name} SVG: {svg_debug_path}")
            print(f"  SVG length: {len(svg_string)} chars")

    # Combine all channel SVGs into a single layered SVG
    # Use processing dimensions (resized) for the SVG
    combined_svg = SVGCombiner.combine_cmyk_layers(
        cyan_svg=svg_results["cyan_svg"],
        magenta_svg=svg_results["magenta_svg"],
        yellow_svg=svg_results["yellow_svg"],
        black_svg=svg_results["black_svg"],
        width=processing_width,
        height=processing_height
    )

    if DEBUG:
        print(f"Processing complete! Files saved in {DEBUG_DIR}/")

    return {
        "combined_svg": combined_svg,
        "metadata": {
            "original_dimensions": [original_width, original_height],
            "processing_dimensions": [processing_width, processing_height]
        },
    }
