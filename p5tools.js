function exportCurrentSVG(filename = 'drawing.svg') {
  let origSvgElement = document.querySelector('svg');

  svgElement = clipSVGPaths(origSvgElement); 

  if (svgElement) {
      let serializer = new XMLSerializer();
      let source = serializer.serializeToString(svgElement);
      let blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
      let url = URL.createObjectURL(blob);
      let link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
  } else {
      console.error('No SVG element found for export.');
  }
}

// Adapted from https://gist.github.com/akre54/4d9ace17fb27d0507a6c790be5047e3d
function clipSVGPaths(origSvgElement) {
  // Create a deep clone of the SVG element to avoid modifying the original.
  const svgElement = origSvgElement.cloneNode(true);

  // Paper.js works on a canvas, so we create a hidden one.
  const paperCanvas = document.createElement('canvas');
  paperCanvas.style.display = 'none';
  paper.setup(paperCanvas);

  // Find all elements that have a clip-path or mask applied.
  const clipPathElements = svgElement.querySelectorAll('[clip-path], [mask]');
  // A map to cache the geometry of each clip path so we don't re-process it.
  const elementMap = new Map();

  // First pass: Go through all clipped elements to find their associated
  // <clipPath> definitions, convert them to Paper.js paths, and cache them.
  clipPathElements.forEach(element => {
    const clipPathAttr = element.getAttribute('clip-path') || element.getAttribute('mask');

    // Extract the ID from the "url(#elementId)" string.
    const elementId = clipPathAttr.match(/\#(.+?)\)/)[1];
    const clipPathElement = document.getElementById(elementId);

    // If we haven't processed this clip path definition yet...
    if (!elementMap.has(elementId)) {
      // Find all <path>s inside the <clipPath> definition.
      const pathElements = clipPathElement.querySelectorAll('path');

      // Combine all path 'd' attributes into a single string for Paper.js.
      const path = new paper.Path(
        [].map.call(pathElements, p => p.getAttribute('d')).join(' ')
      );

      // Cache the resulting path data, keyed by the clip path ID.
      elementMap.set(elementId, path.pathData);
    }
  });

  // Second pass: Apply the cached clip paths to the actual elements.
  clipPathElements.forEach(element => {
    // Get the clip path ID and its corresponding cached path data.
    const clipPathAttr = element.getAttribute('clip-path') || element.getAttribute('mask');
    const elementId = clipPathAttr.match(/\#(.+?)\)/)[1];
    const clipPathData = elementMap.get(elementId);

    // Remove the original clip-path/mask attributes as we're replacing them.
    element.removeAttribute('clip-path');
    element.removeAttribute('mask');

    // Find all paths within the element that needs to be clipped.
    const pathElements = element.querySelectorAll('path');

    // Combine the element's paths into a single Paper.js path.
    const path = new paper.Path(
      [].map.call(pathElements, p => p.getAttribute('d')).join(' ')
    );

    // Create the clipping path and the content path in Paper.js.
    const clipPath = new paper.Path(clipPathData);
    // Calculate the geometric intersection. This is the "clipping" operation.
    const intersection = path.intersect(clipPath, { trace: false });

    // Get style attributes from the first original path to apply to the new one.
    const originalStyleSource = pathElements.length > 0 ? pathElements[0] : element;

    // Create a new <path> element to hold the result of the intersection.
    const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pathElement.setAttribute('d', intersection.pathData);
    pathElement.setAttribute('fill', originalStyleSource.getAttribute('fill') || 'none');
    pathElement.setAttribute('stroke', originalStyleSource.getAttribute('stroke') || 'black');
    pathElement.setAttribute('stroke-width', originalStyleSource.getAttribute('stroke-width') || '1');
    pathElement.setAttribute('data-clipped', true);

    element.appendChild(pathElement);
  });

  // --- Cleanup ---
  // Remove the <defs> section which contained the original <clipPath> definitions.
  // Also remove the original paths that have now been replaced.
  clipPathElements.forEach(element => element.querySelectorAll('path:not([data-clipped])').forEach(p => p.remove()));

  const defs = svgElement.querySelector('defs');
  if (defs) {
    defs.remove();
  }

  // Remove any paths that were likely used for masking or background fills.
  svgElement.querySelectorAll('path[fill="#FFF"]').forEach(n => n.remove())

  return svgElement;
}

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