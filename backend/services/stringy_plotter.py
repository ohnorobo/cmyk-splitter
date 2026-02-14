"""StringyPlotter service - converts bilevel images to continuous line SVG drawings."""

import numpy as np
from scipy.spatial import KDTree
from PIL import Image
from typing import Tuple


class StringyPlotter:
    """
    Converts a bilevel (black and white) image into a single continuous line SVG.

    The algorithm:
    1. Extracts white pixels (ink areas) from the image
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

        # Find coordinates of white pixels (value = 1 in mode '1')
        # White pixels represent areas with ink/color
        white_pixel_coords = np.where(img_array != 0)

        # Stack coordinates and swap to (x, y) format
        # np.where returns (rows, cols) which is (y, x), so reverse it
        points = np.column_stack(list(reversed(white_pixel_coords)))

        # Check if there are any white pixels
        if points.shape[0] == 0:
            # No white pixels - return empty SVG
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
        Connect points using nearest neighbor algorithm with KD-Tree optimization.

        Uses adaptive k-NN queries: starts with k=50 and expands only when needed.
        Leverages spatial locality - next unvisited point is usually very close.
        O(N log N) amortized complexity vs O(N²) brute force.

        Args:
            points: Array of shape (N, 2) with (x, y) coordinates

        Returns:
            Tuple of (ordered_points, distances_between_points)
        """
        if points.shape[0] == 0:
            return np.array([]), np.array([])

        if points.shape[0] == 1:
            return points, np.array([0])

        # Build KD-Tree for fast nearest-neighbor queries
        tree = KDTree(points, compact_nodes=True, balanced_tree=True)

        # Track visited points
        visited = np.zeros(points.shape[0], dtype=bool)

        # Start with first point
        current_idx = 0
        visited[current_idx] = True
        point_collection = [points[current_idx]]
        distance_collection = [0]

        # Initial k for nearest neighbor queries (balance between speed and success rate)
        k_initial = min(50, points.shape[0])

        # Greedily connect nearest neighbors using adaptive k-NN
        for _ in range(points.shape[0] - 1):
            k = k_initial
            found = False

            # Adaptive search: start with small k, expand if all neighbors visited
            while not found and k <= points.shape[0]:
                # Query k nearest neighbors
                distances, indices = tree.query(points[current_idx], k=k)

                # Vectorized check for unvisited neighbors
                unvisited_mask = ~visited[indices]

                if np.any(unvisited_mask):
                    # Find first unvisited neighbor (smallest distance)
                    first_unvisited_pos = np.argmax(unvisited_mask)
                    nearest_idx = indices[first_unvisited_pos]
                    nearest_distance = distances[first_unvisited_pos]

                    # Mark as visited and add to path
                    visited[nearest_idx] = True
                    point_collection.append(points[nearest_idx])
                    distance_collection.append(nearest_distance)
                    current_idx = nearest_idx
                    found = True
                else:
                    # All k neighbors visited - expand search
                    k = min(k * 2, points.shape[0])

            if not found:
                # Shouldn't happen, but handle gracefully
                break

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
