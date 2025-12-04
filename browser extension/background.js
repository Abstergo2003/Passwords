chrome.runtime.onInstalled.addListener(() => {
  console.log('SecurePass Manager installed');
  
  // Initialize storage
  chrome.storage.local.get(['passwords', 'pendingPasswords'], (result) => {
    if (!result.passwords) {
      chrome.storage.local.set({ passwords: [] });
    }
    if (!result.pendingPasswords) {
      chrome.storage.local.set({ pendingPasswords: [] });
    }
  });
});

// Show badge with pending count
async function updateBadge() {
  const result = await chrome.storage.local.get(['pendingPasswords']);
  const pendingPasswords = result.pendingPasswords || [];
  
  if (pendingPasswords.length > 0) {
    chrome.action.setBadgeText({ text: pendingPasswords.length.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#f59e0b' });
  } else {
    chrome.action.setBadgeText({ text: '' });
  }
}

// Update badge on storage change
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.pendingPasswords) {
    updateBadge();
  }
});

// Initialize badge
updateBadge();