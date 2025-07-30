chrome.action.onClicked.addListener(async (tab) => {
  const url = tab.url;
  await chrome.storage.local.set({ lastTabUrl: url });
  chrome.tabs.create({ url: "loading.html" });
});
