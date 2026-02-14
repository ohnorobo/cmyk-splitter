/**
 * Simple CMYK visualization without p5.js
 * Just inserts SVG directly into the DOM
 */

let currentImageWidth = 0;
let currentImageHeight = 0;

/**
 * Initialize the visualization
 */
function setup() {
  setupCMYKGUI();
}

/**
 * Render CMYK layers by inserting SVG into DOM
 */
function renderCMYKLayers() {
  if (!window.cmykData || !window.cmykData.result) return;

  const container = document.getElementById('cmyk-container');
  const result = window.cmykData.result;
  const metadata = result.metadata;

  // Get original image dimensions
  currentImageWidth = metadata.original_dimensions[0];
  currentImageHeight = metadata.original_dimensions[1];

  // Calculate scale to fit in max 800px
  const maxSize = 800;
  const scale = Math.min(maxSize / currentImageWidth, maxSize / currentImageHeight);
  const displayWidth = currentImageWidth * scale;
  const displayHeight = currentImageHeight * scale;

  // Parse the combined SVG
  const parser = new DOMParser();
  const svgDoc = parser.parseFromString(result.combined_svg, 'image/svg+xml');
  const svgElement = svgDoc.documentElement;

  // Set display dimensions with viewBox for proper scaling
  svgElement.setAttribute('width', displayWidth);
  svgElement.setAttribute('height', displayHeight);
  svgElement.setAttribute('viewBox', `0 0 ${currentImageWidth} ${currentImageHeight}`);
  svgElement.style.backgroundColor = 'white';

  // Clear container and add SVG
  container.innerHTML = '';
  container.appendChild(svgElement);

  // Apply stroke widths from current parameters
  updateStrokeWidths();
}

/**
 * Update stroke widths for all CMYK layers
 */
function updateStrokeWidths() {
  const svg = document.querySelector('#cmyk-container svg');
  if (!svg) return;

  // Update each layer with its corresponding width
  const widthMap = {
    'cyan-layer': window.cmykParams.width_c,
    'magenta-layer': window.cmykParams.width_m,
    'yellow-layer': window.cmykParams.width_y,
    'black-layer': window.cmykParams.width_k
  };

  for (const [layerId, width] of Object.entries(widthMap)) {
    const layer = svg.querySelector(`#${layerId}`);
    if (layer) {
      const paths = layer.querySelectorAll('path');
      paths.forEach(path => {
        path.setAttribute('stroke-width', width);
      });
    }
  }
}

/**
 * Redraw function (called when visibility toggles change)
 */
function redraw() {
  renderCMYKLayers();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setup);
} else {
  setup();
}

// Export for use by control handlers
window.updateStrokeWidths = updateStrokeWidths;
