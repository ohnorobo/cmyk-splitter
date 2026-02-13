"""API routes for CMYK image processing."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from PIL import Image
import io
import os
from datetime import datetime
from typing import Optional

from backend.services.cmyk_splitter import CMYKSplitter
from backend.services.halftone_dots import HalftoneDotPlotter
from backend.services.svg_combiner import SVGCombiner

router = APIRouter()


@router.post("/process-image")
async def process_image(
    image: UploadFile = File(...),
    divisor_c: int = Form(50),
    divisor_m: int = Form(50),
    divisor_y: int = Form(50),
    divisor_k: int = Form(25),
    skip_paths_longer_than: int = Form(25),
):
    """
    Process an uploaded image into CMYK stringy SVG layers.

    Args:
        image: Uploaded image file (JPEG, PNG, GIF)
        divisor_c: Sampling divisor for cyan channel (default: 50)
        divisor_m: Sampling divisor for magenta channel (default: 50)
        divisor_y: Sampling divisor for yellow channel (default: 50)
        divisor_k: Sampling divisor for black channel (default: 25)
        skip_paths_longer_than: Max distance for continuous lines (default: 25)

    Returns:
        JSON response with SVG strings for each CMYK channel
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Read uploaded image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))

        # Store original dimensions
        original_width, original_height = pil_image.size

        print(f"Processing image: {original_width}x{original_height}")

        # Debug: Save raw CMYK channels before thresholding
        debug_dir = "backend/services/debug_files"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to RGB if not already
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert RGB to CMYK with GCR
        splitter = CMYKSplitter()
        c, m, y, k = splitter.rgb_to_cmyk_with_gcr(pil_image)

        print(f"Saving debug files to {debug_dir}/")
        # Save raw CMYK channels (grayscale, 0=full ink, 255=no ink)
        c.save(os.path.join(debug_dir, f"{timestamp}_raw_cyan.png"))
        m.save(os.path.join(debug_dir, f"{timestamp}_raw_magenta.png"))
        y.save(os.path.join(debug_dir, f"{timestamp}_raw_yellow.png"))
        k.save(os.path.join(debug_dir, f"{timestamp}_raw_black.png"))
        print(f"  Saved raw CMYK channel images")

        # Split into CMYK channels (with thresholding)
        channels = splitter.split_channels(pil_image)

        # Save bilevel channel images
        for channel_name, channel_img in channels.items():
            debug_path = os.path.join(debug_dir, f"{timestamp}_bilevel_{channel_name}.png")
            channel_img.save(debug_path)
            print(f"  Saved bilevel {channel_name} image: {debug_path}")

        # Process each channel with HalftoneDotPlotter
        channel_configs = {
            "cyan": divisor_c,
            "magenta": divisor_m,
            "yellow": divisor_y,
            "black": divisor_k,
        }

        svg_results = {}
        for channel_name, divisor in channel_configs.items():
            # print(f"Processing {channel_name} channel (divisor={divisor})...")

            # Using HalftoneDotPlotter for simple halftone visualization
            # TODO: Switch to StringyPlotter for continuous line drawings
            plotter = HalftoneDotPlotter(
                divisor=divisor,
                dot_size=10.0,     # Large dots for visibility
                max_dots=2000      # Hard cap to keep SVG files small
            )
            svg_string = plotter.process_image(channels[channel_name])
            svg_results[f"{channel_name}_svg"] = svg_string

            # Debug: Save SVG files
            svg_debug_path = os.path.join(debug_dir, f"{timestamp}_{channel_name}.svg")
            with open(svg_debug_path, 'w') as f:
                f.write(svg_string)
            print(f"  Saved {channel_name} SVG: {svg_debug_path}")
            print(f"  SVG length: {len(svg_string)} chars")

        # Combine all channel SVGs into a single layered SVG
        combined_svg = SVGCombiner.combine_cmyk_layers(
            cyan_svg=svg_results["cyan_svg"],
            magenta_svg=svg_results["magenta_svg"],
            yellow_svg=svg_results["yellow_svg"],
            black_svg=svg_results["black_svg"],
            width=original_width,
            height=original_height
        )

        # Return response
        print(f"Processing complete! Files saved in {debug_dir}/")
        return {
            "status": "completed",
            "result": {
                "combined_svg": combined_svg,
                "metadata": {
                    "original_dimensions": [original_width, original_height]
                },
            },
        }

    except Exception as e:
        # Log error and return failure response
        print(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )
