"""API routes for CMYK image processing."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from PIL import Image
import io
from typing import Optional

from backend.services.cmyk_splitter import CMYKSplitter
from backend.services.stringy_plotter import StringyPlotter

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

        # Split into CMYK channels
        splitter = CMYKSplitter()
        channels = splitter.split_channels(pil_image)

        # Process each channel with StringyPlotter
        channel_configs = {
            "cyan": divisor_c,
            "magenta": divisor_m,
            "yellow": divisor_y,
            "black": divisor_k,
        }

        svg_results = {}
        for channel_name, divisor in channel_configs.items():
            plotter = StringyPlotter(
                divisor=divisor, skip_paths_longer_than=skip_paths_longer_than
            )
            svg_string = plotter.process_image(channels[channel_name])
            svg_results[f"{channel_name}_svg"] = svg_string

        # Return response
        return {
            "status": "completed",
            "result": {
                **svg_results,
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
