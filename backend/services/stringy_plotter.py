"""StringyPlotter service - converts bilevel images to continuous line SVG drawings."""

import numpy as np
from scipy.spatial.distance import cdist
from PIL import Image
from typing import Tuple


class StringyPlotter:
    """
    Converts a bilevel (black and white) image into a single continuous line SVG.

    The algorithm:
    1. Extracts black pixels from the image
    2. Randomly samples pixels based on divisor
    3. Connects pixels using nearest-neighbor traversal
    4. Generates SVG path with moves for gaps longer than threshold
    """

    def __init__(self, divisor: int = 50, skip_paths_longer_than: int = 25):
        """
        Initialize StringyPlotter.

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
        # PIL mode '1': 0=black, 1=white
        black_pixel_coords = np.where(img_array == 0)

        # Stack coordinates and swap to (x, y) format
        # np.where returns (rows, cols) which is (y, x), so reverse it
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

        # Generate continuous path using nearest neighbor
        path_points, distances = self._nearest_neighbor_path(sampled_points)

        # Create SVG path string
        path_string = self._create_path_string(path_points, distances)

        # Generate final SVG
        return self._create_svg(image.width, image.height, path_string)

    def _nearest_neighbor_path(
        self, points: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Connect points using nearest neighbor algorithm.

        Args:
            points: Array of shape (N, 2) with (x, y) coordinates

        Returns:
            Tuple of (ordered_points, distances_between_points)
        """
        if points.shape[0] == 0:
            return np.array([]), np.array([])

        if points.shape[0] == 1:
            return points, np.array([0])

        # Start with first point
        current_point = points[0]
        remaining_points = points[1:]
        point_collection = [current_point]
        distance_collection = [0]

        # Greedily connect nearest neighbors
        for _ in range(points.shape[0] - 1):
            # Calculate distances from current point to all remaining points
            distances = cdist(remaining_points, [current_point])
            nearest_distance = np.min(distances)
            nearest_index = np.where(distances == nearest_distance)[0][0]
            nearest_point = remaining_points[nearest_index]

            # Add to collections
            point_collection.append(nearest_point)
            distance_collection.append(nearest_distance)

            # Remove the point we just added and continue
            mask = np.ones(remaining_points.shape[0], dtype=bool)
            mask[nearest_index] = False
            remaining_points = remaining_points[mask]
            current_point = nearest_point

        return np.array(point_collection), np.array(distance_collection)

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
