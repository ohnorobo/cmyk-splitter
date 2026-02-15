"""API routes for CMYK image processing."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from PIL import Image
import io
import time

from backend.services.process_image import process_image_to_svg

router = APIRouter()


@router.post("/process-image")
async def process_image(
    image: UploadFile = File(...),
    divisor_c: int = Form(50),
    divisor_m: int = Form(50),
    divisor_y: int = Form(50),
    divisor_k: int = Form(25),
    skip_paths_longer_than: int = Form(25),
    threshold_c: int = Form(128),
    threshold_m: int = Form(128),
    threshold_y: int = Form(90),
    threshold_k: int = Form(128),
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
        threshold_c: Cyan threshold 0-255, higher = more ink (default: 128)
        threshold_m: Magenta threshold 0-255, higher = more ink (default: 128)
        threshold_y: Yellow threshold 0-255, higher = more ink (default: 90)
        threshold_k: Black threshold 0-255, higher = more ink (default: 128)

    Returns:
        JSON response with SVG strings for each CMYK channel
    """
    start_time = time.time()
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Read uploaded image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))

        # Process image through service layer
        result = process_image_to_svg(
            pil_image=pil_image,
            divisor_c=divisor_c,
            divisor_m=divisor_m,
            divisor_y=divisor_y,
            divisor_k=divisor_k,
            skip_paths_longer_than=skip_paths_longer_than,
            threshold_c=threshold_c,
            threshold_m=threshold_m,
            threshold_y=threshold_y,
            threshold_k=threshold_k
        )

        # Log completion
        elapsed_time = time.time() - start_time
        print(f"✓ Request completed in {elapsed_time:.2f}s (file: {image.filename})")

        return {
            "status": "completed",
            "result": result,
        }

    except Exception as e:
        # Log error and return failure response
        elapsed_time = time.time() - start_time
        print(f"✗ Request failed after {elapsed_time:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )
