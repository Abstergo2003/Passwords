(function() {
  let detectedCredentials = null;
  let promptTimeout = null;

  // Monitor form submissions - DON'T BLOCK THEM
  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (form.tagName !== 'FORM') return;

    // Check if site is in never save list first
    const result = await chrome.storage.local.get(['neverSaveList']);
    const neverSaveList = result.neverSaveList || [];
    if (neverSaveList.includes(window.location.origin)) {
      return;
    }

    // Detect what type of data we have
    const detectedData = detectFormData(form);
    
    if (!detectedData) return; // No sensitive data detected

    detectedCredentials = {
      ...detectedData,
      url: window.location.origin,
      timestamp: Date.now(),
      pending: true
    };

    // Save to appropriate pending list
    saveToPending(detectedCredentials);

    // Show prompt for immediate action
    showSavePrompt(detectedCredentials.type);
  }, true);

  function detectFormData(form) {
    // 1. Check for passwords (highest priority)
    const passwordField = form.querySelector('input[type="password"]');
    if (passwordField && passwordField.value) {
      const usernameField = form.querySelector(
        'input[type="email"], input[type="text"], input[name*="user"], input[name*="email"], input[id*="user"], input[id*="email"]'
      );
      
      return {
        type: 'password',
        username: usernameField ? usernameField.value : '',
        password: passwordField.value
      };
    }

    // 2. Check for credit card information
    const cardNumber = form.querySelector(
      'input[name*="card"], input[name*="cardnumber"], input[id*="card"], input[autocomplete="cc-number"], input[placeholder*="card number"]'
    );
    
    if (cardNumber && cardNumber.value) {
      const cardName = form.querySelector(
        'input[name*="cardholder"], input[name*="card-name"], input[autocomplete="cc-name"], input[placeholder*="name on card"]'
      );
      const cardExpiry = form.querySelector(
        'input[name*="expir"], input[name*="exp"], input[autocomplete="cc-exp"], input[placeholder*="expir"]'
      );
      const cardCVV = form.querySelector(
        'input[name*="cvv"], input[name*="cvc"], input[name*="security"], input[autocomplete="cc-csc"]'
      );
      
      const cleanCardNumber = cardNumber.value.replace(/\s|-/g, '');
      if (cleanCardNumber.length >= 13 && /^\d+$/.test(cleanCardNumber)) {
        return {
          type: 'payment',
          cardNumber: maskCardNumber(cleanCardNumber),
          cardName: cardName ? cardName.value : '',
          expiry: cardExpiry ? cardExpiry.value : '',
          cvv: cardCVV ? '***' : '' // Never save actual CVV
        };
      }
    }

    // 3. Check for identity information (passport, ID, driver's license)
    const identityFields = form.querySelectorAll(
      'input[name*="passport"], input[name*="id-number"], input[name*="identity"], input[name*="license"], input[name*="ssn"], input[name*="pesel"], input[id*="passport"], input[id*="identity"], input[id*="license"]'
    );
    
    for (const field of identityFields) {
      if (field.value && field.value.length >= 5) {
        const firstName = form.querySelector(
          'input[name*="first"], input[name*="fname"], input[id*="first"]'
        );
        const lastName = form.querySelector(
          'input[name*="last"], input[name*="lname"], input[id*="last"]'
        );
        const dob = form.querySelector(
          'input[name*="birth"], input[name*="dob"], input[type="date"]'
        );
        
        return {
          type: 'identity',
          documentType: getDocumentType(field),
          documentNumber: field.value,
          firstName: firstName ? firstName.value : '',
          lastName: lastName ? lastName.value : '',
          dateOfBirth: dob ? dob.value : ''
        };
      }
    }

    // 4. Check for license keys/serial numbers
    const licenseFields = form.querySelectorAll(
      'input[name*="license-key"], input[name*="serial"], input[name*="activation"], input[name*="product-key"], input[id*="license"], input[id*="serial"], input[placeholder*="license"], input[placeholder*="serial"]'
    );
    
    for (const field of licenseFields) {
      if (field.value && field.value.length >= 10) {
        const productName = form.querySelector(
          'input[name*="product"], input[name*="software"], select[name*="product"]'
        );
        
        return {
          type: 'license',
          licenseKey: field.value,
          productName: productName ? (productName.value || productName.options[productName.selectedIndex]?.text) : ''
        };
      }
    }

    return null;
  }

  function getDocumentType(field) {
    const name = (field.name + field.id).toLowerCase();
    if (name.includes('passport')) return 'Passport';
    if (name.includes('license') || name.includes('driving')) return 'Driver License';
    if (name.includes('ssn')) return 'SSN';
    if (name.includes('pesel')) return 'PESEL';
    if (name.includes('id') || name.includes('identity')) return 'ID Card';
    return 'Document';
  }

  function maskCardNumber(cardNumber) {
    // Show only last 4 digits
    return '•••• •••• •••• ' + cardNumber.slice(-4);
  }

  async function saveToPending(credentials) {
    try {
      const storageKey = `pending${credentials.type.charAt(0).toUpperCase() + credentials.type.slice(1)}s`;
      const result = await chrome.storage.local.get([storageKey]);
      const pendingItems = result[storageKey] || [];
      
      // Check if already exists
      const existingIndex = pendingItems.findIndex(p => {
        if (credentials.type === 'password') {
          return p.url === credentials.url && p.username === credentials.username;
        } else if (credentials.type === 'payment') {
          return p.url === credentials.url && p.cardNumber === credentials.cardNumber;
        } else if (credentials.type === 'identity') {
          return p.url === credentials.url && p.documentNumber === credentials.documentNumber;
        } else if (credentials.type === 'license') {
          return p.url === credentials.url && p.licenseKey === credentials.licenseKey;
        }
        return false;
      });

      if (existingIndex >= 0) {
        pendingItems[existingIndex] = credentials;
      } else {
        pendingItems.push(credentials);
      }

      await chrome.storage.local.set({ [storageKey]: pendingItems });
    } catch (error) {
      console.error('Error saving pending data:', error);
    }
  }

  function showSavePrompt(dataType) {
    // Remove existing prompt if any
    const existing = document.getElementById('securepass-prompt');
    if (existing) existing.remove();

    const titles = {
      password: 'Password Detected',
      payment: 'Payment Card Detected',
      identity: 'Identity Document Detected',
      license: 'License Key Detected'
    };

    const icons = {
      password: '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path>',
      payment: '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
      identity: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
      license: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line>'
    };

    const descriptions = getDataDescription(detectedCredentials);

    const prompt = document.createElement('div');
    prompt.id = 'securepass-prompt';
    prompt.className = 'securepass-save-prompt';
    prompt.innerHTML = `
      <div class="securepass-prompt-content">
        <div class="securepass-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${icons[dataType]}
          </svg>
          <span>${titles[dataType]}</span>
        </div>
        <div class="securepass-body">
          <p><strong>${detectedCredentials.url}</strong></p>
          ${descriptions}
        </div>
        <div class="securepass-actions">
          <button id="securepass-save" class="securepass-btn securepass-btn-primary">Save Now</button>
          <button id="securepass-never" class="securepass-btn securepass-btn-danger">Never for this site</button>
          <button id="securepass-later" class="securepass-btn securepass-btn-secondary">Decide Later</button>
        </div>
        <div class="securepass-footer">
          Auto-saved to pending list
        </div>
      </div>
    `;

    document.body.appendChild(prompt);

    // Animate in
    setTimeout(() => prompt.classList.add('show'), 10);

    // Auto-hide after 8 seconds
    promptTimeout = setTimeout(() => {
      closePrompt();
    }, 8000);

    // Button handlers
    document.getElementById('securepass-save').addEventListener('click', async () => {
      await saveDataNow();
      closePrompt();
    });

    document.getElementById('securepass-never').addEventListener('click', async () => {
      await neverSaveForSite();
      closePrompt();
    });

    document.getElementById('securepass-later').addEventListener('click', () => {
      showNotification('Saved to pending list', 'info');
      closePrompt();
    });
  }

  function getDataDescription(data) {
    switch(data.type) {
      case 'password':
        return `<p>Save login credentials?</p>${data.username ? `<p class="securepass-username">Username: ${data.username}</p>` : ''}`;
      case 'payment':
        return `<p>Save payment card?</p><p class="securepass-username">Card: ${data.cardNumber}</p>${data.cardName ? `<p class="securepass-username">Name: ${data.cardName}</p>` : ''}`;
      case 'identity':
        return `<p>Save identity document?</p><p class="securepass-username">Type: ${data.documentType}</p>${data.firstName || data.lastName ? `<p class="securepass-username">Name: ${data.firstName} ${data.lastName}</p>` : ''}`;
      case 'license':
        return `<p>Save license key?</p>${data.productName ? `<p class="securepass-username">Product: ${data.productName}</p>` : ''}`;
      default:
        return '';
    }
  }

  async function saveDataNow() {
    try {
      const dataType = detectedCredentials.type;
      const storageKey = dataType === 'password' ? 'passwords' : 
                        dataType === 'payment' ? 'payments' :
                        dataType === 'identity' ? 'identities' : 'licenses';
      const pendingKey = `pending${storageKey.charAt(0).toUpperCase() + storageKey.slice(1)}`;
      
      const result = await chrome.storage.local.get([storageKey, pendingKey]);
      const savedItems = result[storageKey] || [];
      const pendingItems = result[pendingKey] || [];
      
      // Remove pending flag
      const savedData = { ...detectedCredentials };
      delete savedData.pending;
      
      // Check if already exists
      const existingIndex = savedItems.findIndex(p => {
        if (dataType === 'password') {
          return p.url === savedData.url && p.username === savedData.username;
        } else if (dataType === 'payment') {
          return p.url === savedData.url && p.cardNumber === savedData.cardNumber;
        } else if (dataType === 'identity') {
          return p.url === savedData.url && p.documentNumber === savedData.documentNumber;
        } else if (dataType === 'license') {
          return p.url === savedData.url && p.licenseKey === savedData.licenseKey;
        }
        return false;
      });

      if (existingIndex >= 0) {
        savedItems[existingIndex] = savedData;
      } else {
        savedItems.push(savedData);
      }

      // Remove from pending
      const pendingIndex = pendingItems.findIndex(p => JSON.stringify(p) === JSON.stringify(detectedCredentials));
      if (pendingIndex >= 0) {
        pendingItems.splice(pendingIndex, 1);
      }

      await chrome.storage.local.set({ [storageKey]: savedItems, [pendingKey]: pendingItems });
      showNotification(`${dataType.charAt(0).toUpperCase() + dataType.slice(1)} saved securely!`, 'success');
    } catch (error) {
      showNotification('Error saving data', 'error');
    }
  }

  async function neverSaveForSite() {
    try {
      const result = await chrome.storage.local.get(['neverSaveList', 'pendingPasswords', 'pendingPayments', 'pendingIdentities', 'pendingLicenses']);
      const neverSaveList = result.neverSaveList || [];
      
      if (!neverSaveList.includes(detectedCredentials.url)) {
        neverSaveList.push(detectedCredentials.url);
      }

      // Remove from appropriate pending list
      const dataType = detectedCredentials.type;
      const pendingKey = `pending${dataType.charAt(0).toUpperCase() + dataType.slice(1)}s`;
      const pendingItems = result[pendingKey] || [];
      
      const pendingIndex = pendingItems.findIndex(p => JSON.stringify(p) === JSON.stringify(detectedCredentials));
      if (pendingIndex >= 0) {
        pendingItems.splice(pendingIndex, 1);
      }
      
      await chrome.storage.local.set({ neverSaveList, [pendingKey]: pendingItems });
      showNotification('Site added to never save list', 'info');
    } catch (error) {
      showNotification('Error updating settings', 'error');
    }
  }

  function closePrompt() {
    if (promptTimeout) {
      clearTimeout(promptTimeout);
      promptTimeout = null;
    }
    
    const prompt = document.getElementById('securepass-prompt');
    if (prompt) {
      prompt.classList.remove('show');
      setTimeout(() => prompt.remove(), 300);
    }
  }

  function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `securepass-notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2500);
  }

  // Initialize on page load
  chrome.storage.local.get(['neverSaveList'], (result) => {
    const neverSaveList = result.neverSaveList || [];
    // Just store the list, don't prevent anything
  });
})();