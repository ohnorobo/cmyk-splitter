/**
 * API client for communicating with the CMYK Splitter backend
 */

class CMYKAPIClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  /**
   * Process an image through the CMYK splitter
   *
   * @param {File} imageFile - The image file to process
   * @param {Object} params - Processing parameters
   * @param {number} params.divisor_c - Cyan channel divisor (default: 50)
   * @param {number} params.divisor_m - Magenta channel divisor (default: 50)
   * @param {number} params.divisor_y - Yellow channel divisor (default: 50)
   * @param {number} params.divisor_k - Black channel divisor (default: 25)
   * @param {number} params.skip_paths_longer_than - Max continuous line distance (default: 25)
   * @returns {Promise<Object>} Response with cyan_svg, magenta_svg, yellow_svg, black_svg
   */
  async processImage(imageFile, params = {}) {
    // Build FormData with file and parameters
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('divisor_c', params.divisor_c || 50);
    formData.append('divisor_m', params.divisor_m || 50);
    formData.append('divisor_y', params.divisor_y || 50);
    formData.append('divisor_k', params.divisor_k || 25);
    formData.append('skip_paths_longer_than', params.skip_paths_longer_than || 25);

    try {
      const response = await fetch(`${this.baseURL}/api/process-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API error:', error);
      throw error;
    }
  }

  /**
   * Check backend health status
   *
   * @returns {Promise<Object>} Health status response
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

// Export for use in other modules
window.CMYKAPIClient = CMYKAPIClient;
