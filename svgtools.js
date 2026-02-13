/**
 * Export all CMYK layers combined into one SVG
 * @param {Object} result - Result object from API with combined_svg
 * @param {string} filename - Output filename
 */
function exportCombinedCMYK(result, filename) {
  // Get the SVG that's already displayed
  const svgElement = document.querySelector('#cmyk-container svg');

  if (!svgElement) {
    console.error('No SVG found to export');
    return;
  }

  // Clone it to reset any display-specific attributes
  const exportSvg = svgElement.cloneNode(true);

  // Reset to original dimensions (from metadata)
  const metadata = window.cmykData.result.metadata;
  exportSvg.setAttribute('width', metadata.original_dimensions[0]);
  exportSvg.setAttribute('height', metadata.original_dimensions[1]);

  // Serialize and download
  const serializer = new XMLSerializer();
  const source = serializer.serializeToString(exportSvg);
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