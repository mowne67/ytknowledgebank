# YouTube Knowledge Bank - Deployment Guide

## Issues Fixed

### 1. Extension New Tab Override Issue
- **Problem**: Extension was overriding the new tab page with loading.html
- **Solution**: Removed `chrome_url_overrides` from manifest.json
- **Result**: New tab page is no longer affected by the extension

### 2. Render Sign-in Error
- **Problem**: yt-dlp authentication issues on Render deployment
- **Solution**: Added better error handling and retry mechanisms
- **Changes Made**:
  - Enhanced subtitle extraction with retry logic
  - Added user agent headers to avoid blocking
  - Improved error handling in API endpoints
  - Added health check endpoint

## Deployment Steps

### 1. Update Extension Configuration
1. Open `extension_1/config.js`
2. Replace `'https://your-render-app-name.onrender.com'` with your actual Render URL
3. Reload the extension in Chrome

### 2. Render Deployment
1. Ensure your Render app has the following environment variables:
   ```
   PYTHON_VERSION=3.9
   ```
2. The app should automatically install dependencies from `requirements.txt`
3. Render will use the `main.py` file as the entry point

### 3. Testing the Fixes
1. **Local Testing**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
2. **Extension Testing**:
   - Load the extension in Chrome
   - Navigate to a YouTube video
   - Click the extension icon
   - Verify it works with both local and production URLs

### 4. Troubleshooting Render Issues

If you still get sign-in errors on Render:

1. **Check Logs**: Monitor the Render logs for specific error messages
2. **Video Restrictions**: Some videos may require authentication
3. **Rate Limiting**: YouTube may block requests from Render IPs
4. **Alternative Solutions**:
   - Use a different subtitle extraction method
   - Implement cookie-based authentication
   - Use YouTube Data API instead of yt-dlp

### 5. Extension Features

- **New Tab Override**: Disabled by default (can be enabled in config.js)
- **Environment Detection**: Automatically switches between local and production URLs
- **Error Handling**: Better error messages and logging
- **Debug Mode**: Enable/disable debug logging in config.js

## Configuration Options

### Extension Configuration (`extension_1/config.js`)
```javascript
FEATURES: {
  overrideNewTab: false, // Set to true to override new tab
  enableDebugLogging: true // Enable/disable debug logs
}
```

### API Endpoints
- `GET /` - Welcome message
- `POST /summarize` - Main summarization endpoint
- `GET /health` - Health check for monitoring

## Common Issues and Solutions

1. **"Authentication required" error**: Video is restricted, try a different video
2. **"Video not found" error**: Check if the video URL is valid
3. **Extension not working**: Check the API URL in config.js
4. **New tab still affected**: Make sure you reloaded the extension after changes 