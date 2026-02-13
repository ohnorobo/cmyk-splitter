"""CMYK channel splitting service using PIL/Pillow with GCR."""

from PIL import Image
from typing import Dict, Tuple
import numpy as np


class CMYKSplitter:
    """Splits RGB images into CMYK channels with thresholding and GCR."""

    # Threshold values (0-255)
    THRESHOLD_CMK = 127  # 50% threshold for Cyan, Magenta, Black
    THRESHOLD_Y = 165    # 65% threshold for Yellow (yellows need special handling)

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
    def split_channels(image: Image.Image) -> Dict[str, Image.Image]:
        """
        Split an RGB image into CMYK channels and apply thresholds.

        Args:
            image: PIL Image in RGB mode

        Returns:
            Dictionary with keys 'cyan', 'magenta', 'yellow', 'black'
            All returned images are mode '1' (bilevel/monochrome)
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Convert RGB to CMYK with GCR
        c, m, y, k = CMYKSplitter.rgb_to_cmyk_with_gcr(image)

        # Apply thresholds to create bilevel images
        # In CMYK mode, 0 = full ink, 255 = no ink
        # So we invert the comparison: values < threshold get ink (black)
        cyan_bilevel = c.point(lambda x: 0 if x < CMYKSplitter.THRESHOLD_CMK else 255, mode='1')
        magenta_bilevel = m.point(lambda x: 0 if x < CMYKSplitter.THRESHOLD_CMK else 255, mode='1')
        yellow_bilevel = y.point(lambda x: 0 if x < CMYKSplitter.THRESHOLD_Y else 255, mode='1')
        black_bilevel = k.point(lambda x: 0 if x < CMYKSplitter.THRESHOLD_CMK else 255, mode='1')

        return {
            'cyan': cyan_bilevel,
            'magenta': magenta_bilevel,
            'yellow': yellow_bilevel,
            'black': black_bilevel
        }
