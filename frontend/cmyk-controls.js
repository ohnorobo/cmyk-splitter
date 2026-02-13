/**
 * CMYK Controls - dat.GUI interface for CMYK Splitter
 */

// Global state for CMYK data
window.cmykData = null;
window.apiClient = null;

// CMYK parameters
window.cmykParams = {
  // Processing parameters
  divisor_c: 50,
  divisor_m: 50,
  divisor_y: 50,
  divisor_k: 25,
  skip_paths_longer_than: 25,

  // Actions
  uploadImage: function() {
    document.getElementById('image-upload').click();
  },
  reprocess: function() {
    if (window.currentImageFile) {
      processImage(window.currentImageFile);
    } else {
      showStatus('Please upload an image first', 'error');
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
  gui.add(cmykParams, 'divisor_c', 10, 200, 1).name('Cyan Divisor');
  gui.add(cmykParams, 'divisor_m', 10, 200, 1).name('Magenta Divisor');
  gui.add(cmykParams, 'divisor_y', 10, 200, 1).name('Yellow Divisor');
  gui.add(cmykParams, 'divisor_k', 10, 200, 1).name('Black Divisor');
  gui.add(cmykParams, 'skip_paths_longer_than', 5, 100, 1).name('Skip Paths >');
  gui.add(cmykParams, 'reprocess').name('🔄 Reprocess');
  gui.add(cmykParams, 'export').name('💾 Export SVG');
}

/**
 * Initialize API client and file upload handler
 */
function initializeCMYKControls() {
  // Create API client
  window.apiClient = new CMYKAPIClient('http://localhost:8000');

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
    const response = await fetch('static/urn.png');
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

    // Process the default image
    await processImage(file);
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
      divisor_c: cmykParams.divisor_c,
      divisor_m: cmykParams.divisor_m,
      divisor_y: cmykParams.divisor_y,
      divisor_k: cmykParams.divisor_k,
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
