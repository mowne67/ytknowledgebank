(async () => {
  const result = await chrome.storage.local.get("lastTabUrl");
  const url = result.lastTabUrl;

  CONFIG.log("Previous tab URL: " + url);

  if (!url) {
    document.getElementById('spinner').textContent = 'Failed to get previous tab URL.';
    return;
  }

  // Use configuration for API URL
  const apiBaseUrl = CONFIG.getApiUrl();
  CONFIG.log("Using API URL: " + apiBaseUrl);
  
  try {
    const response = await fetch(`${apiBaseUrl}/summarize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const markdown = data.markdown;

    CONFIG.log("Received markdown: " + markdown.substring(0, 100) + "...");

    // Make sure it's stored BEFORE redirecting
    localStorage.setItem('markdown', markdown);
    CONFIG.log("Markdown saved to localStorage.");

    // Now redirect
    window.location.href = 'result.html';
  } catch (err) {
    document.getElementById('spinner').textContent = 'Failed: ' + err.message;
    CONFIG.log("Error: " + err.message);
    console.error(err);
  }
})();
