const width = 700;
const height = 700;

function setup() {
  const canvas = createCanvas(width, height, SVG);
  canvas.parent(select('div[p5]'));

  noFill();
  stroke(0);

  setupCMYKGUI();
}

function draw() {
  clear(); // clear canvas for SVG redraw

  // Render CMYK layers if available
  if (window.cmykData) {
    drawCMYKLayers();
  }
}

/**
 * Draw CMYK layers from API response
 */
function drawCMYKLayers() {
  if (!window.cmykData || !window.cmykData.result) return;

  const result = window.cmykData.result;
  const layers = [
    { svg: result.cyan_svg, color: [0, 255, 255, 180], visible: cmykParams.showCyan },
    { svg: result.magenta_svg, color: [255, 0, 255, 180], visible: cmykParams.showMagenta },
    { svg: result.yellow_svg, color: [255, 255, 0, 180], visible: cmykParams.showYellow },
    { svg: result.black_svg, color: [0, 0, 0, 255], visible: cmykParams.showBlack }
  ];

  strokeWeight(1);
  noFill();

  // Draw each visible layer
  for (const layer of layers) {
    if (layer.visible) {
      stroke(...layer.color);
      drawSVGPath(layer.svg);
    }
  }
}

/**
 * Parse and draw an SVG string (handles both paths and circles)
 */
function drawSVGPath(svgString) {
  // Try to extract path d attribute
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

  // Also handle circle elements (for halftone dots)
  const circleMatches = svgString.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/g);
  for (const match of circleMatches) {
    const cx = parseFloat(match[1]);
    const cy = parseFloat(match[2]);
    const r = parseFloat(match[3]);
    ellipse(cx, cy, r * 2, r * 2);
  }
}
