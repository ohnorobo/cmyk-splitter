let canvasWidth = 800;
let canvasHeight = 800;
let scaleFactor = 1;
let imageWidth = 800;
let imageHeight = 800;

function setup() {
  // Use default canvas renderer (supports blend modes) instead of SVG
  // SVG export works directly from API data, doesn't need SVG canvas
  const canvas = createCanvas(canvasWidth, canvasHeight);
  canvas.parent(select('div[p5]'));

  background(255); // White background

  noFill();
  stroke(0);

  setupCMYKGUI();
}

function draw() {
  background(255); // White background

  // Render CMYK layers if available
  if (window.cmykData) {
    updateCanvasSize();
    drawCMYKLayers();
  }
}

function updateCanvasSize() {
  // Get original image dimensions from API response
  const metadata = window.cmykData.result.metadata;
  imageWidth = metadata.original_dimensions[0];
  imageHeight = metadata.original_dimensions[1];

  // Calculate scale to fit in max 800px while maintaining aspect ratio
  const maxSize = 800;
  const scale = Math.min(maxSize / imageWidth, maxSize / imageHeight);

  scaleFactor = scale;
  canvasWidth = imageWidth * scale;
  canvasHeight = imageHeight * scale;

  // Resize canvas if dimensions changed
  if (width !== canvasWidth || height !== canvasHeight) {
    resizeCanvas(canvasWidth, canvasHeight);
  }
}

/**
 * Draw CMYK layers from API response
 */
function drawCMYKLayers() {
  if (!window.cmykData || !window.cmykData.result) return;

  const result = window.cmykData.result;
  const layers = [
    { svg: result.cyan_svg, color: [0, 255, 255], visible: cmykParams.showCyan },
    { svg: result.magenta_svg, color: [255, 0, 255], visible: cmykParams.showMagenta },
    { svg: result.yellow_svg, color: [255, 255, 0], visible: cmykParams.showYellow },
    { svg: result.black_svg, color: [0, 0, 0], visible: cmykParams.showBlack }
  ];

  // Apply scaling to fit canvas
  push();
  scale(scaleFactor);

  // Use multiply blend mode for authentic CMYK appearance
  blendMode(MULTIPLY);

  strokeWeight(1);
  noStroke();

  // Draw each visible layer
  for (const layer of layers) {
    if (layer.visible) {
      fill(...layer.color);
      drawSVGPath(layer.svg);
    }
  }

  // Reset blend mode
  blendMode(BLEND);

  pop();
}

/**
 * Parse and draw an SVG string (handles both paths and circles)
 */
function drawSVGPath(svgString) {
  // Handle path elements (for StringyPlotter)
  const pathMatch = svgString.match(/d="([^"]*)"/);
  if (pathMatch) {
    const pathData = pathMatch[1];
    const commands = pathData.match(/[ML]\s*[\d.]+\s+[\d.]+/g);
    if (commands) {
      beginShape();
      for (const cmd of commands) {
        const parts = cmd.trim().split(/\s+/);
        const command = parts[0];
        const x = parseFloat(parts[1]);
        const y = parseFloat(parts[2]);

        if (command === 'M') {
          endShape();
          beginShape();
          vertex(x, y);
        } else if (command === 'L') {
          vertex(x, y);
        }
      }
      endShape();
    }
  }

  // Handle circle elements (for HalftoneDotPlotter) - filled circles
  const circleMatches = svgString.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g);
  for (const match of circleMatches) {
    const cx = parseFloat(match[1]);
    const cy = parseFloat(match[2]);
    const r = parseFloat(match[3]);
    ellipse(cx, cy, r * 2, r * 2);  // Filled circles (noStroke/fill set by caller)
  }
}
