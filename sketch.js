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

  // Create wrapper SVG with all layers
  const svgWrapper = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svgWrapper.setAttribute('width', displayWidth);
  svgWrapper.setAttribute('height', displayHeight);
  svgWrapper.setAttribute('viewBox', `0 0 ${currentImageWidth} ${currentImageHeight}`);
  svgWrapper.style.backgroundColor = 'white';

  // Define layers with colors and visibility
  const layers = [
    {
      name: 'cyan',
      svg: result.cyan_svg,
      color: 'rgb(0, 255, 255)',
      visible: window.cmykParams.showCyan
    },
    {
      name: 'magenta',
      svg: result.magenta_svg,
      color: 'rgb(255, 0, 255)',
      visible: window.cmykParams.showMagenta
    },
    {
      name: 'yellow',
      svg: result.yellow_svg,
      color: 'rgb(255, 255, 0)',
      visible: window.cmykParams.showYellow
    },
    {
      name: 'black',
      svg: result.black_svg,
      color: 'rgb(0, 0, 0)',
      visible: window.cmykParams.showBlack
    }
  ];

  // Add each layer as a group
  layers.forEach(layer => {
    if (!layer.visible) return;

    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('class', `cmyk-layer ${layer.name}-layer`);
    group.style.mixBlendMode = 'multiply';

    // Parse the SVG string and extract circles
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(layer.svg, 'image/svg+xml');
    const circles = svgDoc.querySelectorAll('circle');

    // Copy circles to the group with appropriate color
    circles.forEach(circle => {
      const newCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      newCircle.setAttribute('cx', circle.getAttribute('cx'));
      newCircle.setAttribute('cy', circle.getAttribute('cy'));
      newCircle.setAttribute('r', circle.getAttribute('r'));
      newCircle.setAttribute('fill', layer.color);
      group.appendChild(newCircle);
    });

    svgWrapper.appendChild(group);
  });

  // Clear container and add new SVG
  container.innerHTML = '';
  container.appendChild(svgWrapper);
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
