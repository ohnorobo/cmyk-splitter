"""Fast test plotter - O(n) scan-order algorithm for testing the pipeline."""

import numpy as np
from PIL import Image
from typing import Tuple


class FastTestPlotter:
    """
    Fast version of StringyPlotter for testing.

    Uses simple scan-order (left-to-right, top-to-bottom) instead of
    nearest-neighbor. This is O(n) instead of O(n²), allowing fast testing
    of the full pipeline before optimizing the algorithm.
    """

    def __init__(self, divisor: int = 50, skip_paths_longer_than: int = 25):
        """
        Initialize FastTestPlotter.

        Args:
            divisor: Sample every Nth pixel (higher = fewer points, faster processing)
            skip_paths_longer_than: Max distance for continuous line; longer jumps use move command
        """
        self.divisor = divisor
        self.skip_paths_longer_than = skip_paths_longer_than

    def process_image(self, image: Image.Image) -> str:
        """
        Convert a bilevel PIL Image to an SVG string with a continuous line drawing.

        Args:
            image: PIL Image in mode '1' (bilevel) where 1=white, 0=black

        Returns:
            SVG string with single path element
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

        # Generate path using simple scan order (FAST)
        path_points, distances = self._scan_order_path(sampled_points)

        # Create SVG path string
        path_string = self._create_path_string(path_points, distances)

        # Generate final SVG
        return self._create_svg(image.width, image.height, path_string)

    def _scan_order_path(
        self, points: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Connect points in simple scan order (left-to-right, top-to-bottom).

        This is O(n) instead of O(n²) nearest-neighbor.

        Args:
            points: Array of shape (N, 2) with (x, y) coordinates

        Returns:
            Tuple of (ordered_points, distances_between_points)
        """
        if points.shape[0] == 0:
            return np.array([]), np.array([])

        if points.shape[0] == 1:
            return points, np.array([0])

        # Sort points by y (row), then x (column) - scan order
        # This gives us left-to-right, top-to-bottom ordering
        sorted_indices = np.lexsort((points[:, 0], points[:, 1]))
        sorted_points = points[sorted_indices]

        # Calculate distances between consecutive points
        distances = [0]
        for i in range(1, len(sorted_points)):
            dist = np.linalg.norm(sorted_points[i] - sorted_points[i-1])
            distances.append(dist)

        return sorted_points, np.array(distances)

    def _create_path_string(
        self, points: np.ndarray, distances: np.ndarray
    ) -> str:
        """
        Create SVG path d attribute string.

        Args:
            points: Array of (x, y) coordinates
            distances: Array of distances between consecutive points

        Returns:
            SVG path d attribute value (e.g., "M 10 20 L 30 40 ...")
        """
        if points.shape[0] == 0:
            return ""

        # Start with move to first point
        path_parts = [f"M {points[0][0]} {points[0][1]}"]

        # Add subsequent points as lines or moves
        for point, distance in zip(points[1:], distances[1:]):
            if distance > self.skip_paths_longer_than:
                # Gap too large - move without drawing
                path_parts.append(f"M {point[0]} {point[1]}")
            else:
                # Draw line
                path_parts.append(f"L {point[0]} {point[1]}")

        return " ".join(path_parts)

    def _create_svg(self, width: int, height: int, path_string: str) -> str:
        """
        Create complete SVG document string.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            path_string: SVG path d attribute value

        Returns:
            Complete SVG document as string
        """
        if path_string:
            path_element = f'<path d="{path_string}" fill="none" stroke="black" />'
        else:
            path_element = ""

        return (
            f'<svg width="{width}" height="{height}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'{path_element}'
            f'</svg>'
        )
