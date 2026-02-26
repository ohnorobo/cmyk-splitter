"""SVG Combiner service for merging CMYK channel SVGs into a single layered SVG."""

from xml.etree import ElementTree as ET


# Register Inkscape/Sodipodi namespaces so they appear in output
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')

INKSCAPE_NS = 'http://www.inkscape.org/namespaces/inkscape'


class SVGCombiner:
    """Combines multiple channel SVGs into a single layered SVG with proper colors and groups."""

    # Color mapping for CMYK channels
    CHANNEL_COLORS = {
        "cyan": "rgb(0, 255, 255)",
        "magenta": "rgb(255, 0, 255)",
        "yellow": "rgb(255, 255, 0)",
        "black": "rgb(0, 0, 0)",
    }

    # Layer labels matching the working file convention (number + letter)
    CHANNEL_LABELS = {
        "cyan": "1 C",
        "magenta": "2 M",
        "yellow": "3 Y",
        "black": "4 K",
    }

    @staticmethod
    def combine_cmyk_layers(
        cyan_svg: str,
        magenta_svg: str,
        yellow_svg: str,
        black_svg: str,
        width: int,
        height: int,
        physical_width_mm: float = None,
        physical_height_mm: float = None
    ) -> str:
        """
        Combine 4 channel SVGs into a single SVG with Inkscape-compatible layers.

        Args:
            cyan_svg: SVG string for cyan channel
            magenta_svg: SVG string for magenta channel
            yellow_svg: SVG string for yellow channel
            black_svg: SVG string for black channel
            width: Width of the output SVG in pixels (used for viewBox)
            height: Height of the output SVG in pixels (used for viewBox)
            physical_width_mm: Physical width in mm (used for width attribute)
            physical_height_mm: Physical height in mm (used for height attribute)

        Returns:
            Combined SVG string with Inkscape-compatible layer structure
        """
        # Create root SVG element
        svg_root = ET.Element('svg')
        svg_root.set('xmlns', 'http://www.w3.org/2000/svg')

        if physical_width_mm is not None and physical_height_mm is not None:
            svg_root.set('width', f'{physical_width_mm}mm')
            svg_root.set('height', f'{physical_height_mm}mm')
        else:
            svg_root.set('width', str(width))
            svg_root.set('height', str(height))

        svg_root.set('viewBox', f'0 0 {width} {height}')

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

            # Create Inkscape-compatible layer group
            group = ET.SubElement(svg_root, 'g')
            group.set('id', f'{channel_name}-layer')
            group.set(f'{{{INKSCAPE_NS}}}groupmode', 'layer')
            group.set(f'{{{INKSCAPE_NS}}}label', SVGCombiner.CHANNEL_LABELS[channel_name])
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
