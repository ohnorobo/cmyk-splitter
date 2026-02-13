const width = 700;
const height = 700;

// Simple spiral drawing example
function drawSpiral() {
  beginShape();
  let angleStep = 0.1;
  for (let a = 0; a < params.turns * TWO_PI; a += angleStep) {
    let r = params.spacing * a;
    let x = r * cos(a);
    let y = r * sin(a);
    vertex(x, y);
  }
  endShape();
}

function setup() {
  const canvas = createCanvas(width, height, SVG);
  canvas.parent(select('div[p5]'));

  noFill();
  stroke(0);

  setupCMYKGUI();
}

function draw() {
  clear(); // clear canvas for SVG redraw

  // If we have CMYK data, render it
  if (window.cmykData) {
    drawCMYKLayers();
  } else {
    // Otherwise show the spiral demo
    strokeWeight(params.lineWeight);
    drawShapeInsideBorder(drawSpiral);
    if (params.drawRegistrationMark) {
      drawRegistrationMark();
    }
  }
}

function drawShapeInsideBorder(shapeDrawingFunction) {
  // clip the shape inside the SVG border
  push();
  function mask() {
    rect(params.border,
      params.border,
      width - params.border*2,
      height - params.border*2)
  }
  clip(mask);

  // move to center
  translate(width/2, height/2);

  shapeDrawingFunction();

  pop();
}

function drawRegistrationMark() {
  translate(0, 0)

  const circleSize = 30;
  const crosshairSize = 50;
  const center = crosshairSize / 2;

  ellipse(center, center, circleSize, circleSize);
 
  line(center - crosshairSize / 2, center, center + crosshairSize / 2, center); // Horizontal
  line(center, center - crosshairSize / 2, center, center + crosshairSize / 2); // Vertical
}

let params = {
  turns: 5,
  spacing: 10,
  lineWeight: 2,
  border: 50,
  drawRegistrationMark: true,
  exportSVG: function() { exportCurrentSVG('spiral.svg'); }
};

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
 * Parse and draw an SVG path string
 */
function drawSVGPath(svgString) {
  // Extract path d attribute
  const pathMatch = svgString.match(/d="([^"]*)"/);
  if (!pathMatch) return;

  const pathData = pathMatch[1];

  // Parse path commands (M x y, L x y)
  const commands = pathData.match(/[ML]\s*[\d.]+\s+[\d.]+/g);
  if (!commands) return;

  beginShape();
  for (const cmd of commands) {
    const parts = cmd.trim().split(/\s+/);
    const command = parts[0];
    const x = parseFloat(parts[1]);
    const y = parseFloat(parts[2]);

    if (command === 'M') {
      // Move without drawing - end current shape and start new one
      endShape();
      beginShape();
      vertex(x, y);
    } else if (command === 'L') {
      // Line to
      vertex(x, y);
    }
  }
  endShape();
}

function setupGUI() {
  const gui = new dat.GUI();
  gui.add(params, 'turns', 1, 20, 1).name('Turns').onChange(redraw);
  gui.add(params, 'spacing', 1, 20, 1).name('Spacing').onChange(redraw);
  gui.add(params, 'lineWeight', 1, 10, 1).name('Line Weight').onChange(redraw);
  gui.add(params, 'border', 0, 100, 1).name('Border').onChange(redraw);
  gui.add(params, 'drawRegistrationMark').name('Registration').onChange(redraw);
  gui.add(params, 'exportSVG').name('Export SVG');
  noLoop(); // only redraw when parameters change
}
