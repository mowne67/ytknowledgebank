// Configuration for YouTube Summary Generator Extension
const CONFIG = {
  // API Configuration
  API_URLS: {
    local: 'http://127.0.0.1:8000',
    production: 'https://your-render-app-name.onrender.com' // Replace with your actual Render URL
  },
  
  // Feature flags
  FEATURES: {
    overrideNewTab: false, // Set to true if you want to override new tab
    enableDebugLogging: true
  },
  
  // Get the appropriate API URL based on environment
  getApiUrl: function() {
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.protocol === 'chrome-extension:';
    
    return isLocalhost ? this.API_URLS.local : this.API_URLS.production;
  },
  
  // Debug logging
  log: function(message) {
    if (this.FEATURES.enableDebugLogging) {
      console.log(`[YT Summary Extension] ${message}`);
    }
  }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
} 