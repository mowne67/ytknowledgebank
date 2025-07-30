const contentDiv = document.getElementById('content');
const markdown = localStorage.getItem('markdown');

console.log('Loaded markdown:', markdown);

if (markdown) {
  try {
    const html = marked.parse(markdown);
    contentDiv.innerHTML = html;
  } catch (e) {
    contentDiv.textContent = 'Error parsing markdown: ' + e.message;
    console.error(e);
  }
} else {
  contentDiv.textContent = 'No summary found. Make sure loading.js stored the markdown.';
}
