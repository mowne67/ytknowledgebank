(async () => {
  const result = await chrome.storage.local.get("lastTabUrl");
  const url = result.lastTabUrl;

  console.log("Previous tab URL:", url);

  if (!url) {
    document.getElementById('spinner').textContent = 'Failed to get previous tab URL.';
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });

    if (!response.ok) throw new Error('API Error: ' + response.status);

    const data = await response.json();
    const markdown = data.markdown;

    console.log("Received markdown:", markdown); // 👈 Debug this

    // Make sure it's stored BEFORE redirecting
    localStorage.setItem('markdown', markdown);
    console.log("Markdown saved to localStorage.");

    // Now redirect
    window.location.href = 'result.html';
  } catch (err) {
    document.getElementById('spinner').textContent = 'Failed: ' + err.message;
    console.error(err);
  }
})();
