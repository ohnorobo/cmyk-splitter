/**
 * Export a single CMYK layer as SVG
 * @param {string} svgString - SVG string from API response
 * @param {string} filename - Output filename
 * @param {string} channel - Channel name: 'cyan', 'magenta', 'yellow', or 'black'
 */
function exportCMYKLayer(svgString, filename, channel) {
  // Parse SVG string to extract path
  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(svgString, 'image/svg+xml');
  const svgElement = svgDoc.documentElement;

  // Set stroke color based on channel
  const colorMap = {
    'cyan': '#00FFFF',
    'magenta': '#FF00FF',
    'yellow': '#FFFF00',
    'black': '#000000'
  };

  const pathElement = svgElement.querySelector('path');
  if (pathElement) {
    pathElement.setAttribute('stroke', colorMap[channel] || '#000000');
    pathElement.setAttribute('stroke-width', '1');
  }

  // Serialize and download
  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(svgElement);
  downloadSVG(source, filename);
}

/**
 * Export all CMYK layers combined into one SVG
 * @param {Object} result - Result object from API with cyan_svg, magenta_svg, yellow_svg, black_svg
 * @param {string} filename - Output filename
 */
function exportCombinedCMYK(result, filename) {
  // Parse the first SVG to get dimensions
  const parser = new DOMParser();
  const firstDoc = parser.parseFromString(result.cyan_svg, 'image/svg+xml');
  const width = firstDoc.documentElement.getAttribute('width');
  const height = firstDoc.documentElement.getAttribute('height');

  // Create new SVG with all layers
  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('width', width);
  svg.setAttribute('height', height);
  svg.setAttribute('xmlns', svgNS);

  // Layer configurations
  const layers = [
    { svgString: result.cyan_svg, color: '#00FFFF', name: 'cyan' },
    { svgString: result.magenta_svg, color: '#FF00FF', name: 'magenta' },
    { svgString: result.yellow_svg, color: '#FFFF00', name: 'yellow' },
    { svgString: result.black_svg, color: '#000000', name: 'black' }
  ];

  // Add each layer as a group
  layers.forEach(layer => {
    const layerDoc = parser.parseFromString(layer.svgString, 'image/svg+xml');
    const pathElement = layerDoc.querySelector('path');

    if (pathElement) {
      // Create group for this layer
      const group = document.createElementNS(svgNS, 'g');
      group.setAttribute('id', `${layer.name}-layer`);

      // Clone and style the path
      const path = document.createElementNS(svgNS, 'path');
      path.setAttribute('d', pathElement.getAttribute('d'));
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', layer.color);
      path.setAttribute('stroke-width', '1');

      group.appendChild(path);
      svg.appendChild(group);
    }
  });

  // Serialize and download
  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(svg);
  downloadSVG(source, filename);
}

/**
 * Helper function to download SVG content
 * @param {string} source - SVG content as string
 * @param {string} filename - Output filename
 */
function downloadSVG(source, filename) {
  const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}