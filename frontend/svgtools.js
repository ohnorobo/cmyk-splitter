/**
 * Export all CMYK layers combined into one SVG
 * @param {Object} result - Result object from API with combined_svg
 * @param {string} filename - Output filename
 */
function exportCombinedCMYK(result, filename) {
  if (!window.cmykData || !window.cmykData.result) {
    console.error('No CMYK data to export');
    return;
  }

  // Start from the original combined_svg string to preserve Inkscape
  // namespace attributes (inkscape:groupmode, inkscape:label) that get
  // stripped when the browser DOM round-trips the SVG.
  let source = window.cmykData.result.combined_svg;

  // Apply current stroke widths from the UI by replacing stroke-width
  // values in the raw SVG string for each layer
  const widthMap = {
    'cyan-layer': window.cmykParams.width_c,
    'magenta-layer': window.cmykParams.width_m,
    'yellow-layer': window.cmykParams.width_y,
    'black-layer': window.cmykParams.width_k
  };

  for (const [layerId, width] of Object.entries(widthMap)) {
    // Find the layer's section and update stroke-width in its paths
    const layerRegex = new RegExp(
      `(id="${layerId}"[^>]*>)([\\s\\S]*?)(<\\/g>)`,
    );
    source = source.replace(layerRegex, (match, open, content, close) => {
      const updatedContent = content.replace(
        /stroke-width="[^"]*"/g,
        `stroke-width="${width}"`
      );
      return open + updatedContent + close;
    });
  }

  // Update dimensions to physical units
  const metadata = window.cmykData.result.metadata;
  const processingDims = metadata.processing_dimensions || metadata.original_dimensions;
  let widthAttr, heightAttr;
  if (metadata.physical_dimensions_mm) {
    widthAttr = metadata.physical_dimensions_mm[0] + 'mm';
    heightAttr = metadata.physical_dimensions_mm[1] + 'mm';
  } else {
    const scale = Math.min(210 / processingDims[0], 297 / processingDims[1]);
    widthAttr = Math.round(processingDims[0] * scale * 100) / 100 + 'mm';
    heightAttr = Math.round(processingDims[1] * scale * 100) / 100 + 'mm';
  }
  source = source.replace(/width="[^"]*"/, `width="${widthAttr}"`);
  source = source.replace(/height="[^"]*"/, `height="${heightAttr}"`);

  // Ensure viewBox matches processing coordinate space
  const vbAttr = `0 0 ${processingDims[0]} ${processingDims[1]}`;
  source = source.replace(/viewBox="[^"]*"/, `viewBox="${vbAttr}"`);

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