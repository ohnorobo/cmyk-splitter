/**
 * CMYK Controls - dat.GUI interface for CMYK Splitter
 */

// Global state for CMYK data
window.cmykData = null;
window.apiClient = null;

// CMYK parameters
window.cmykParams = {
  // Threshold parameters (0-255, higher = more ink)
  threshold_c: 128,
  threshold_m: 128,
  threshold_y: 90,
  threshold_k: 128,

  // Density parameters (10-200, higher = more dense)
  density_c: 160,
  density_m: 160,
  density_y: 160,
  density_k: 185,
  skip_paths_longer_than: 25,

  // Stroke width parameters
  width_c: 15,
  width_m: 15,
  width_y: 15,
  width_k: 3,

  // Actions
  uploadImage: function() {
    document.getElementById('image-upload').click();
  },
  reprocess: function() {
    if (!window.currentImageFile) {
      showStatus('Please upload an image first', 'error');
      return;
    }

    // Check if this is urn.png with default parameters
    const isUrnPng = window.currentImageFile.name === 'urn.png';
    const hasDefaultParams = (
      cmykParams.threshold_c === 128 &&
      cmykParams.threshold_m === 128 &&
      cmykParams.threshold_y === 90 &&
      cmykParams.threshold_k === 128 &&
      cmykParams.density_c === 160 &&
      cmykParams.density_m === 160 &&
      cmykParams.density_y === 160 &&
      cmykParams.density_k === 185 &&
      cmykParams.skip_paths_longer_than === 25
    );

    if (isUrnPng && hasDefaultParams) {
      // Use fast cached endpoint
      loadDefaultImage();
    } else {
      // Use regular processing
      processImage(window.currentImageFile);
    }
  },
  export: function() {
    if (window.cmykData) {
      exportCombinedCMYK(window.cmykData.result, 'cmyk-combined.svg');
    } else {
      showStatus('Please upload an image first', 'error');
    }
  }
};

/**
 * Set up CMYK-specific dat.GUI controls
 */
function setupCMYKGUI() {
  const gui = new dat.GUI();

  // All controls at top level
  gui.add(cmykParams, 'uploadImage').name('📁 Select Image');
  gui.add(cmykParams, 'threshold_c', 0, 255, 1).name('C Threshold');
  gui.add(cmykParams, 'threshold_m', 0, 255, 1).name('M Threshold');
  gui.add(cmykParams, 'threshold_y', 0, 255, 1).name('Y Threshold');
  gui.add(cmykParams, 'threshold_k', 0, 255, 1).name('K Threshold');
  gui.add(cmykParams, 'density_c', 10, 200, 1).name('C Density');
  gui.add(cmykParams, 'density_m', 10, 200, 1).name('M Density');
  gui.add(cmykParams, 'density_y', 10, 200, 1).name('Y Density');
  gui.add(cmykParams, 'density_k', 10, 200, 1).name('K Density');
  gui.add(cmykParams, 'skip_paths_longer_than', 5, 100, 1).name('Skip Paths >');
  gui.add(cmykParams, 'reprocess').name('🔄 Reprocess');
  gui.add(cmykParams, 'width_c', 0.1, 50, 0.5).name('C Width')
    .onChange(() => {
      if (typeof updateStrokeWidths === 'function') {
        updateStrokeWidths();
      }
    });
  gui.add(cmykParams, 'width_m', 0.1, 50, 0.5).name('M Width')
    .onChange(() => {
      if (typeof updateStrokeWidths === 'function') {
        updateStrokeWidths();
      }
    });
  gui.add(cmykParams, 'width_y', 0.1, 50, 0.5).name('Y Width')
    .onChange(() => {
      if (typeof updateStrokeWidths === 'function') {
        updateStrokeWidths();
      }
    });
  gui.add(cmykParams, 'width_k', 0.1, 50, 0.5).name('K Width')
    .onChange(() => {
      if (typeof updateStrokeWidths === 'function') {
        updateStrokeWidths();
      }
    });
  gui.add(cmykParams, 'export').name('💾 Export SVG');
}

/**
 * Initialize API client and file upload handler
 */
function initializeCMYKControls() {
  // Create API client (auto-detects environment)
  window.apiClient = new CMYKAPIClient();

  // Set up file upload handler
  const fileInput = document.getElementById('image-upload');
  fileInput.addEventListener('change', handleFileUpload);

  // Check backend health
  checkBackendHealth();

  // Load default image
  loadDefaultImage();
}

/**
 * Load and process default image on startup
 */
async function loadDefaultImage() {
  try {
    const response = await fetch('frontend/static/urn.png');
    const blob = await response.blob();
    const file = new File([blob], 'urn.png', { type: 'image/png' });

    // Store for reprocessing
    window.currentImageFile = file;

    // Show preview
    const previewContainer = document.getElementById('preview-container');
    const reader = new FileReader();
    reader.onload = function(e) {
      previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;">`;
    };
    reader.readAsDataURL(file);

    // Use fast cached endpoint for default urn.png
    showStatus('Loading default image...', 'processing');

    try {
      const result = await window.apiClient.getCachedUrnResponse();
      window.cmykData = result;

      showStatus('Default image loaded ✓', 'success');
      setTimeout(() => showStatus('', ''), 2000);

      // Render the CMYK layers
      if (typeof renderCMYKLayers === 'function') {
        renderCMYKLayers();
      }
    } catch (error) {
      // Fallback to regular processing if cache fails
      console.warn('Cached response failed, falling back to regular processing:', error);
      await processImage(file);
    }
  } catch (error) {
    console.error('Failed to load default image:', error);
    // Silently fail - user can upload their own image
  }
}

/**
 * Check if backend is available
 */
async function checkBackendHealth() {
  try {
    await window.apiClient.healthCheck();
    // Silently succeed - only show error if backend fails
  } catch (error) {
    showStatus('Backend not available. Start server with: uvicorn backend.main:app --reload --port 8000', 'error');
  }
}

/**
 * Handle file upload
 */
async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Store for reprocessing
  window.currentImageFile = file;

  // Show preview
  const reader = new FileReader();
  reader.onload = function(e) {
    const previewContainer = document.getElementById('preview-container');
    previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;">`;
  };
  reader.readAsDataURL(file);

  // Process image
  await processImage(file);
}

/**
 * Process image through API
 */
async function processImage(file) {
  showStatus('Processing image...', 'processing');

  try {
    const params = {
      threshold_c: cmykParams.threshold_c,
      threshold_m: cmykParams.threshold_m,
      threshold_y: cmykParams.threshold_y,
      threshold_k: cmykParams.threshold_k,
      // Convert density to divisor (invert: higher density = lower divisor)
      divisor_c: 210 - cmykParams.density_c,
      divisor_m: 210 - cmykParams.density_m,
      divisor_y: 210 - cmykParams.density_y,
      divisor_k: 210 - cmykParams.density_k,
      skip_paths_longer_than: cmykParams.skip_paths_longer_than
    };

    const result = await window.apiClient.processImage(file, params);
    window.cmykData = result;

    showStatus('Processing complete ✓', 'success');
    setTimeout(() => showStatus('', ''), 2000);

    // Render the CMYK layers
    if (typeof renderCMYKLayers === 'function') {
      renderCMYKLayers();
    }
  } catch (error) {
    showStatus(`Error: ${error.message}`, 'error');
    console.error('Processing error:', error);
  }
}

/**
 * Show status message
 */
function showStatus(message, type = '') {
  const statusDiv = document.getElementById('status-message');
  statusDiv.textContent = message;
  statusDiv.className = type;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeCMYKControls);
} else {
  initializeCMYKControls();
}
