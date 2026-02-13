"""CMYK channel splitting service using PIL/Pillow."""

from PIL import Image
from typing import Dict


class CMYKSplitter:
    """Splits RGB images into CMYK channels with thresholding."""

    # Threshold values (0-255)
    THRESHOLD_CMK = 127  # 50% threshold for Cyan, Magenta, Black
    THRESHOLD_Y = 165    # 65% threshold for Yellow (yellows need special handling)

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

        # Convert RGB to CMYK
        cmyk_image = image.convert('CMYK')

        # Split into individual channels
        c, m, y, k = cmyk_image.split()

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
