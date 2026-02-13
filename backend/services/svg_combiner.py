"""SVG Combiner service for merging CMYK channel SVGs into a single layered SVG."""

from xml.etree import ElementTree as ET


class SVGCombiner:
    """Combines multiple channel SVGs into a single layered SVG with proper colors and groups."""

    # Color mapping for CMYK channels
    CHANNEL_COLORS = {
        "cyan": "rgb(0, 255, 255)",
        "magenta": "rgb(255, 0, 255)",
        "yellow": "rgb(255, 255, 0)",
        "black": "rgb(0, 0, 0)",
    }

    @staticmethod
    def combine_cmyk_layers(
        cyan_svg: str,
        magenta_svg: str,
        yellow_svg: str,
        black_svg: str,
        width: int,
        height: int
    ) -> str:
        """
        Combine 4 channel SVGs into a single SVG with named groups.

        Args:
            cyan_svg: SVG string for cyan channel
            magenta_svg: SVG string for magenta channel
            yellow_svg: SVG string for yellow channel
            black_svg: SVG string for black channel
            width: Width of the output SVG
            height: Height of the output SVG

        Returns:
            Combined SVG string with structure:
            <svg width="..." height="..." xmlns="...">
              <g id="cyan-layer" style="mix-blend-mode: multiply;">
                <circle... fill="rgb(0, 255, 255)" />
                ...
              </g>
              <g id="magenta-layer" style="mix-blend-mode: multiply;">
                <circle... fill="rgb(255, 0, 255)" />
                ...
              </g>
              <g id="yellow-layer" style="mix-blend-mode: multiply;">
                <circle... fill="rgb(255, 255, 0)" />
                ...
              </g>
              <g id="black-layer" style="mix-blend-mode: multiply;">
                <circle... fill="rgb(0, 0, 0)" />
                ...
              </g>
            </svg>
        """
        # Create root SVG element
        svg_root = ET.Element('svg')
        svg_root.set('width', str(width))
        svg_root.set('height', str(height))
        svg_root.set('xmlns', 'http://www.w3.org/2000/svg')

        # Process each channel
        channels = [
            ("cyan", cyan_svg),
            ("magenta", magenta_svg),
            ("yellow", yellow_svg),
            ("black", black_svg),
        ]

        for channel_name, svg_string in channels:
            # Parse the channel SVG
            try:
                channel_root = ET.fromstring(svg_string)
            except ET.ParseError as e:
                print(f"Error parsing {channel_name} SVG: {e}")
                continue

            # Create group for this channel
            group = ET.SubElement(svg_root, 'g')
            group.set('id', f'{channel_name}-layer')
            group.set('style', 'mix-blend-mode: multiply;')

            # Extract all circles from the channel SVG (HalftoneDotPlotter)
            circles = channel_root.findall('.//{http://www.w3.org/2000/svg}circle')
            if not circles:
                # Try without namespace
                circles = channel_root.findall('.//circle')

            # Extract all paths from the channel SVG (StringyPlotter)
            paths = channel_root.findall('.//{http://www.w3.org/2000/svg}path')
            if not paths:
                # Try without namespace
                paths = channel_root.findall('.//path')

            channel_color = SVGCombiner.CHANNEL_COLORS[channel_name]

            # Add circles to the group with proper color
            for circle in circles:
                new_circle = ET.SubElement(group, 'circle')
                new_circle.set('cx', circle.get('cx', '0'))
                new_circle.set('cy', circle.get('cy', '0'))
                new_circle.set('r', circle.get('r', '1'))
                new_circle.set('fill', channel_color)

            # Add paths to the group with proper color
            for path in paths:
                new_path = ET.SubElement(group, 'path')
                new_path.set('d', path.get('d', ''))
                new_path.set('fill', 'none')
                new_path.set('stroke', channel_color)
                new_path.set('stroke-width', path.get('stroke-width', '1'))

        # Convert to string
        svg_string = ET.tostring(svg_root, encoding='unicode', method='xml')
        return svg_string
