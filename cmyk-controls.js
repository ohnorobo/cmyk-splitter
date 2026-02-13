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

  // Layer visibility
  showCyan: true,
  showMagenta: true,
  showYellow: true,
  showBlack: true,

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
  exportCyan: function() {
    if (window.cmykData) {
      exportCMYKLayer(window.cmykData.result.cyan_svg, 'cyan.svg', 'cyan');
    }
  },
  exportMagenta: function() {
    if (window.cmykData) {
      exportCMYKLayer(window.cmykData.result.magenta_svg, 'magenta.svg', 'magenta');
    }
  },
  exportYellow: function() {
    if (window.cmykData) {
      exportCMYKLayer(window.cmykData.result.yellow_svg, 'yellow.svg', 'yellow');
    }
  },
  exportBlack: function() {
    if (window.cmykData) {
      exportCMYKLayer(window.cmykData.result.black_svg, 'black.svg', 'black');
    }
  },
  exportCombined: function() {
    if (window.cmykData) {
      exportCombinedCMYK(window.cmykData.result, 'cmyk-combined.svg');
    }
  }
};

/**
 * Set up CMYK-specific dat.GUI controls
 */
function setupCMYKGUI() {
  const gui = new dat.GUI();

  // Upload section
  const uploadFolder = gui.addFolder('Upload');
  uploadFolder.add(cmykParams, 'uploadImage').name('📁 Select Image');
  uploadFolder.open();

  // Processing parameters
  const processFolder = gui.addFolder('Processing Parameters');
  processFolder.add(cmykParams, 'divisor_c', 10, 200, 1).name('Cyan Divisor');
  processFolder.add(cmykParams, 'divisor_m', 10, 200, 1).name('Magenta Divisor');
  processFolder.add(cmykParams, 'divisor_y', 10, 200, 1).name('Yellow Divisor');
  processFolder.add(cmykParams, 'divisor_k', 10, 200, 1).name('Black Divisor');
  processFolder.add(cmykParams, 'skip_paths_longer_than', 5, 100, 1).name('Skip Paths >');
  processFolder.add(cmykParams, 'reprocess').name('🔄 Reprocess');
  processFolder.open();

  // Layer visibility
  const visibilityFolder = gui.addFolder('Layer Visibility');
  visibilityFolder.add(cmykParams, 'showCyan').name('Show Cyan').onChange(() => {
    if (typeof redraw === 'function') redraw();
  });
  visibilityFolder.add(cmykParams, 'showMagenta').name('Show Magenta').onChange(() => {
    if (typeof redraw === 'function') redraw();
  });
  visibilityFolder.add(cmykParams, 'showYellow').name('Show Yellow').onChange(() => {
    if (typeof redraw === 'function') redraw();
  });
  visibilityFolder.add(cmykParams, 'showBlack').name('Show Black').onChange(() => {
    if (typeof redraw === 'function') redraw();
  });
  visibilityFolder.open();

  // Export section
  const exportFolder = gui.addFolder('Export');
  exportFolder.add(cmykParams, 'exportCyan').name('Export Cyan');
  exportFolder.add(cmykParams, 'exportMagenta').name('Export Magenta');
  exportFolder.add(cmykParams, 'exportYellow').name('Export Yellow');
  exportFolder.add(cmykParams, 'exportBlack').name('Export Black');
  exportFolder.add(cmykParams, 'exportCombined').name('Export Combined');
  exportFolder.open();
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
}

/**
 * Check if backend is available
 */
async function checkBackendHealth() {
  try {
    await window.apiClient.healthCheck();
    showStatus('Backend connected ✓', 'success');
    setTimeout(() => showStatus('', ''), 2000);
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

    // Trigger redraw
    if (typeof redraw === 'function') {
      redraw();
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
