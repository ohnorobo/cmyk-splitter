"""CMYK channel splitting service using PIL/Pillow with GCR."""

from PIL import Image
from typing import Dict, Tuple
import numpy as np


class CMYKSplitter:
    """Splits RGB images into CMYK channels with thresholding and GCR."""

    # Threshold values (0-255)
    THRESHOLD_C = 127  # 50% threshold for Cyan
    THRESHOLD_M = 127  # 50% threshold for Magenta
    THRESHOLD_Y = 165  # 65% threshold for Yellow (yellows need special handling)
    THRESHOLD_K = 127  # 50% threshold for Black

    @staticmethod
    def rgb_to_cmyk_with_gcr(image: Image.Image) -> Tuple[Image.Image, Image.Image, Image.Image, Image.Image]:
        """
        Convert RGB image to CMYK with proper Gray Component Replacement (GCR).

        This mimics ImageMagick's CMYK conversion by extracting the gray component
        from C+M+Y into the K channel.

        Args:
            image: PIL Image in RGB mode

        Returns:
            Tuple of (cyan, magenta, yellow, black) PIL Images in mode 'L' (grayscale)
            Values: 0 = full ink, 255 = no ink
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert to numpy array and normalize to 0-1 range
        rgb = np.array(image, dtype=np.float32) / 255.0
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

        # Convert RGB to CMY (subtract from 1)
        c = 1.0 - r
        m = 1.0 - g
        y = 1.0 - b

        # Calculate K as the minimum of C, M, Y (gray component)
        k = np.minimum(np.minimum(c, m), y)

        # Extract gray from CMY (GCR - Gray Component Replacement)
        # If K == 1, all are full ink, so CMY should be 0
        # Otherwise, remove the gray component from CMY
        with np.errstate(divide='ignore', invalid='ignore'):
            c = np.where(k < 1.0, (c - k) / (1.0 - k), 0.0)
            m = np.where(k < 1.0, (m - k) / (1.0 - k), 0.0)
            y = np.where(k < 1.0, (y - k) / (1.0 - k), 0.0)

        # Clamp values to 0-1 range
        c = np.clip(c, 0.0, 1.0)
        m = np.clip(m, 0.0, 1.0)
        y = np.clip(y, 0.0, 1.0)
        k = np.clip(k, 0.0, 1.0)

        # Convert to 0-255 range (0 = full ink, 255 = no ink - same as PIL CMYK)
        c = (c * 255).astype(np.uint8)
        m = (m * 255).astype(np.uint8)
        y = (y * 255).astype(np.uint8)
        k = (k * 255).astype(np.uint8)

        # Convert back to PIL Images
        c_img = Image.fromarray(c, mode='L')
        m_img = Image.fromarray(m, mode='L')
        y_img = Image.fromarray(y, mode='L')
        k_img = Image.fromarray(k, mode='L')

        return c_img, m_img, y_img, k_img

    @staticmethod
    def split_channels(
        image: Image.Image,
        threshold_c: int = None,
        threshold_m: int = None,
        threshold_y: int = None,
        threshold_k: int = None
    ) -> Dict[str, Image.Image]:
        """
        Split an RGB image into CMYK channels and apply thresholds.

        Args:
            image: PIL Image in RGB mode
            threshold_c: Cyan threshold (0-255), higher = more ink, defaults to class constant
            threshold_m: Magenta threshold (0-255), higher = more ink, defaults to class constant
            threshold_y: Yellow threshold (0-255), higher = more ink, defaults to class constant
            threshold_k: Black threshold (0-255), higher = more ink, defaults to class constant

        Returns:
            Dictionary with keys 'cyan', 'magenta', 'yellow', 'black'
            All returned images are mode '1' (bilevel/monochrome)
        """
        # Use provided thresholds or fall back to class defaults
        threshold_c = threshold_c if threshold_c is not None else CMYKSplitter.THRESHOLD_C
        threshold_m = threshold_m if threshold_m is not None else CMYKSplitter.THRESHOLD_M
        threshold_y = threshold_y if threshold_y is not None else CMYKSplitter.THRESHOLD_Y
        threshold_k = threshold_k if threshold_k is not None else CMYKSplitter.THRESHOLD_K

        # Invert thresholds to make higher values = more ink (more intuitive)
        # User provides 0-255 where higher = more ink
        # We convert to CMYK space where lower = more ink
        threshold_c = 255 - threshold_c
        threshold_m = 255 - threshold_m
        threshold_y = 255 - threshold_y
        threshold_k = 255 - threshold_k

        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert RGB to CMYK with GCR
        c, m, y, k = CMYKSplitter.rgb_to_cmyk_with_gcr(image)

        # Apply thresholds to create bilevel images
        # In CMYK mode, 0 = full ink, 255 = no ink
        # So we invert the comparison: values < threshold get ink (black)
        cyan_bilevel = c.point(lambda x: 0 if x < threshold_c else 255, mode='1')
        magenta_bilevel = m.point(lambda x: 0 if x < threshold_m else 255, mode='1')
        yellow_bilevel = y.point(lambda x: 0 if x < threshold_y else 255, mode='1')
        black_bilevel = k.point(lambda x: 0 if x < threshold_k else 255, mode='1')

        return {
            'cyan': cyan_bilevel,
            'magenta': magenta_bilevel,
            'yellow': yellow_bilevel,
            'black': black_bilevel
        }
