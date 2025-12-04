let currentTab = 'passwords';
let currentCategory = 'pending';

document.addEventListener('DOMContentLoaded', async () => {
  await loadAllData();
  
  // Main tab switching
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      currentTab = tab.dataset.tab;
      updateActiveTab();
      showCurrentContent();
    });
  });
  
  // Category tab switching (Pending/Saved)
  document.querySelectorAll('.category-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentCategory = tab.dataset.category;
      showCurrentContent();
    });
  });
  
  updateActiveTab();
  showCurrentContent();
});

function updateActiveTab() {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${currentTab}"]`).classList.add('active');
}

function showCurrentContent() {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById(`${currentTab}-${currentCategory}`).classList.add('active');
}

async function loadAllData() {
  const result = await chrome.storage.local.get([
    'pendingPasswords', 'passwords',
    'pendingPayments', 'payments',
    'pendingIdentities', 'identities',
    'pendingLicenses', 'licenses'
  ]);
  
  const pendingPasswords = result.pendingPasswords || [];
  const passwords = result.passwords || [];
  const pendingPayments = result.pendingPayments || [];
  const payments = result.payments || [];
  const pendingIdentities = result.pendingIdentities || [];
  const identities = result.identities || [];
  const pendingLicenses = result.pendingLicenses || [];
  const licenses = result.licenses || [];
  
  // Update badges
  updateBadge('passwordCount', pendingPasswords.length);
  updateBadge('paymentCount', pendingPayments.length);
  updateBadge('identityCount', pendingIdentities.length);
  updateBadge('licenseCount', pendingLicenses.length);
  
  // Render all sections
  renderPasswords('passwords-pending', pendingPasswords, true);
  renderPasswords('passwords-saved', passwords, false);
  renderPayments('payments-pending', pendingPayments, true);
  renderPayments('payments-saved', payments, false);
  renderIdentities('identities-pending', pendingIdentities, true);
  renderIdentities('identities-saved', identities, false);
  renderLicenses('licenses-pending', pendingLicenses, true);
  renderLicenses('licenses-saved', licenses, false);
}

function updateBadge(id, count) {
  const badge = document.getElementById(id);
  if (badge) {
    badge.textContent = count > 0 ? count : '';
  }
}

function renderPendingPasswords(pendingPasswords) {
  const container = document.getElementById('pending-content');
  
  if (pendingPasswords.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        <h3>No pending passwords</h3>
        <p>Detected passwords will appear here</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = pendingPasswords.map((pwd, index) => `
    <div class="password-item pending">
      <div class="password-url">
        ${pwd.url}
        <span class="pending-badge">PENDING</span>
      </div>
      <div class="password-username">${pwd.username || 'No username'}</div>
      <div class="password-field">
        <div class="password-text hidden" data-password="${escapeHtml(pwd.password)}" data-index="${index}">••••••••</div>
        <button class="btn-icon btn-toggle-password" data-index="${index}" title="Show password">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
        </button>
        <button class="btn-icon btn-copy-password" data-password="${escapeHtml(pwd.password)}" title="Copy password">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
      <div class="password-time">${formatTime(pwd.timestamp)}</div>
      <div class="password-actions">
        <button class="btn btn-success" data-action="approve" data-index="${index}">✓ Save</button>
        <button class="btn btn-secondary" data-action="reject" data-index="${index}">✗ Reject</button>
        <button class="btn btn-danger" data-action="never" data-index="${index}">Never for site</button>
      </div>
    </div>
  `).join('');
  
  // Add event listeners
  container.querySelectorAll('button').forEach(btn => {
    if (btn.classList.contains('btn-toggle-password')) {
      btn.addEventListener('click', togglePassword);
    } else if (btn.classList.contains('btn-copy-password')) {
      btn.addEventListener('click', copyPassword);
    } else {
      btn.addEventListener('click', handlePendingAction);
    }
  });
}

function renderSavedPasswords(passwords) {
  const container = document.getElementById('saved-content');
  
  if (passwords.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
        <h3>No saved passwords</h3>
        <p>Approved passwords will appear here</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = passwords.map((pwd, index) => `
    <div class="password-item">
      <div class="password-url">${pwd.url}</div>
      <div class="password-username">${pwd.username || 'No username'}</div>
      <div class="password-field">
        <div class="password-text hidden" data-password="${escapeHtml(pwd.password)}" data-index="${index}">••••••••</div>
        <button class="btn-icon btn-toggle-password" data-index="${index}" title="Show password">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
        </button>
        <button class="btn-icon btn-copy-password" data-password="${escapeHtml(pwd.password)}" title="Copy password">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        </button>
      </div>
      <div class="password-time">${formatTime(pwd.timestamp)}</div>
      <div class="password-actions">
        <button class="btn btn-danger" data-action="delete" data-index="${index}">Delete</button>
      </div>
    </div>
  `).join('');
  
  // Add event listeners
  container.querySelectorAll('button').forEach(btn => {
    if (btn.classList.contains('btn-toggle-password')) {
      btn.addEventListener('click', togglePassword);
    } else if (btn.classList.contains('btn-copy-password')) {
      btn.addEventListener('click', copyPassword);
    } else {
      btn.addEventListener('click', handleSavedAction);
    }
  });
}

async function handlePendingAction(e) {
  const action = e.target.dataset.action;
  const index = parseInt(e.target.dataset.index);
  
  const result = await chrome.storage.local.get(['pendingPasswords', 'passwords', 'neverSaveList']);
  const pendingPasswords = result.pendingPasswords || [];
  const passwords = result.passwords || [];
  const neverSaveList = result.neverSaveList || [];
  
  const pwd = pendingPasswords[index];
  
  if (action === 'approve') {
    // Move to saved passwords
    delete pwd.pending;
    
    const existingIndex = passwords.findIndex(p => 
      p.url === pwd.url && p.username === pwd.username
    );
    
    if (existingIndex >= 0) {
      passwords[existingIndex] = pwd;
    } else {
      passwords.push(pwd);
    }
    
    pendingPasswords.splice(index, 1);
    await chrome.storage.local.set({ passwords, pendingPasswords });
    
  } else if (action === 'reject') {
    // Just remove from pending
    pendingPasswords.splice(index, 1);
    await chrome.storage.local.set({ pendingPasswords });
    
  } else if (action === 'never') {
    // Add to never save list and remove from pending
    if (!neverSaveList.includes(pwd.url)) {
      neverSaveList.push(pwd.url);
    }
    pendingPasswords.splice(index, 1);
    await chrome.storage.local.set({ pendingPasswords, neverSaveList });
  }
  
  // Reload
  location.reload();
}

async function handleSavedAction(e) {
  const action = e.target.dataset.action;
  const index = parseInt(e.target.dataset.index);
  
  if (action === 'delete') {
    const result = await chrome.storage.local.get(['passwords']);
    const passwords = result.passwords || [];
    passwords.splice(index, 1);
    await chrome.storage.local.set({ passwords });
    location.reload();
  }
}

function formatTime(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  
  return new Date(timestamp).toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function togglePassword(e) {
  const button = e.currentTarget;
  const passwordText = button.parentElement.querySelector('.password-text');
  const isHidden = passwordText.classList.contains('hidden');
  
  if (isHidden) {
    // Show password
    passwordText.textContent = passwordText.dataset.password;
    passwordText.classList.remove('hidden');
    button.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
        <line x1="1" y1="1" x2="23" y2="23"></line>
      </svg>
    `;
    button.title = 'Hide password';
  } else {
    // Hide password
    passwordText.textContent = '••••••••';
    passwordText.classList.add('hidden');
    button.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
    `;
    button.title = 'Show password';
  }
}

async function copyPassword(e) {
  const button = e.currentTarget;
  const password = button.dataset.password;
  
  try {
    await navigator.clipboard.writeText(password);
    
    // Visual feedback
    const originalHTML = button.innerHTML;
    button.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    `;
    button.style.background = '#10b981';
    button.style.color = 'white';
    
    setTimeout(() => {
      button.innerHTML = originalHTML;
      button.style.background = '';
      button.style.color = '';
    }, 1500);
  } catch (err) {
    console.error('Failed to copy password:', err);
  }
}