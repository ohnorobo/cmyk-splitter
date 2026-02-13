"""Halftone dots plotter - simple dot-based visualization for CMYK channels."""

import numpy as np
from PIL import Image


class HalftoneDotPlotter:
    """
    Simple halftone dot plotter for testing and visualization.

    Places dots (SVG circles) at sampled black pixel locations,
    creating a halftone/stipple effect that represents the image.
    Very fast (no path-finding) and shows actual image content.
    """

    def __init__(self, divisor: int = 50, dot_size: float = 1.5):
        """
        Initialize HalftoneDotPlotter.

        Args:
            divisor: Sample every Nth pixel (higher = fewer dots, faster)
            dot_size: Radius of each dot in pixels (default 1.5)
        """
        self.divisor = divisor
        self.dot_size = dot_size

    def process_image(self, image: Image.Image) -> str:
        """
        Convert a bilevel PIL Image to an SVG with dots at black pixel locations.

        Args:
            image: PIL Image in mode '1' (bilevel) where 1=white, 0=black

        Returns:
            SVG string with circle elements
        """
        # Convert image to numpy array
        img_array = np.array(image)

        # Find coordinates of black pixels (value = 0 in mode '1')
        black_pixel_coords = np.where(img_array == 0)

        # Stack coordinates and swap to (x, y) format
        points = np.column_stack(list(reversed(black_pixel_coords)))

        # Check if there are any black pixels
        if points.shape[0] == 0:
            # No black pixels - return empty SVG
            return self._create_svg(image.width, image.height, "")

        # Sample points based on divisor
        sample_size = max(1, points.shape[0] // self.divisor)
        sampled_points = points[
            np.random.choice(points.shape[0], sample_size, replace=False), :
        ]

        # Create SVG circles
        circles = self._create_circles(sampled_points)

        # Generate final SVG
        return self._create_svg(image.width, image.height, circles)

    def _create_circles(self, points: np.ndarray) -> str:
        """
        Create SVG circle elements for each point.

        Args:
            points: Array of shape (N, 2) with (x, y) coordinates

        Returns:
            String of SVG circle elements
        """
        if points.shape[0] == 0:
            return ""

        circle_elements = []
        for point in points:
            x, y = point[0], point[1]
            circle_elements.append(
                f'<circle cx="{x}" cy="{y}" r="{self.dot_size}" fill="black" />'
            )

        return "\n".join(circle_elements)

    def _create_svg(self, width: int, height: int, content: str) -> str:
        """
        Create complete SVG document string.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            content: SVG content (circle elements)

        Returns:
            Complete SVG document as string
        """
        return (
            f'<svg width="{width}" height="{height}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'{content}'
            f'</svg>'
        )
