// Chat Translator Popup Script

document.addEventListener('DOMContentLoaded', () => {
  // Tab Switching
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab') + 'Tab';
      const targetContent = document.getElementById(tabId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // Tone Chips
  let selectedTone = 'professional';
  const toneChips = document.querySelectorAll('.tone-chip');
  toneChips.forEach(chip => {
    chip.addEventListener('click', () => {
      toneChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      selectedTone = chip.getAttribute('data-tone');

      // Update output badge
      const badge = document.getElementById('outputBadge');
      if (selectedTone === 'bangla') {
        badge.innerText = 'বাংলা (Bengali)';
      } else {
        badge.innerText = selectedTone.toUpperCase();
      }
    });
  });

  // Input & Character Counter
  const inputEl = document.getElementById('inputText');
  const charCountEl = document.getElementById('charCount');
  const clearBtn = document.getElementById('clearBtn');
  const outputEl = document.getElementById('outputText');
  const translateBtn = document.getElementById('popupTranslateBtn');
  const copyBtn = document.getElementById('copyBtn');

  inputEl.addEventListener('input', () => {
    charCountEl.innerText = `${inputEl.value.length} characters`;
  });

  clearBtn.addEventListener('click', () => {
    inputEl.value = '';
    charCountEl.innerText = '0 characters';
    outputEl.innerText = 'Your translated message will appear here...';
    inputEl.focus();
  });

  // Copy button
  copyBtn.addEventListener('click', () => {
    const text = outputEl.innerText;
    if (!text || text === 'Your translated message will appear here...' || text.startsWith('⏳')) return;

    navigator.clipboard.writeText(text).then(() => {
      const originalText = copyBtn.innerText;
      copyBtn.innerText = '✓ Copied!';
      copyBtn.style.color = '#34d399';
      setTimeout(() => {
        copyBtn.innerText = originalText;
        copyBtn.style.color = '';
      }, 1500);
    });
  });

  // Perform Translation inside Popup
  function doPopupTranslate() {
    const text = inputEl.value.trim();
    if (!text) return;

    outputEl.innerHTML = '<span style="color: #94a3b8;">⏳ Translating with Gemini AI...</span>';
    translateBtn.disabled = true;
    translateBtn.style.opacity = '0.7';

    let action = 'translate_outgoing';
    if (selectedTone === 'bangla') {
      action = 'translate_incoming';
    }

    chrome.runtime.sendMessage({
      action: action,
      text: text,
      tone: selectedTone
    }, (response) => {
      translateBtn.disabled = false;
      translateBtn.style.opacity = '1';

      if (response && response.success) {
        outputEl.innerText = response.text;
      } else {
        outputEl.innerHTML = `<span style="color: #f87171;">❌ ${response ? response.error : 'Translation failed'}</span>`;
      }
    });
  }

  translateBtn.addEventListener('click', doPopupTranslate);

  // Keyboard shortcut: Ctrl + Enter in textarea
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      doPopupTranslate();
    }
  });

  // Settings Tab: API Key Management
  const apiKeyInput = document.getElementById('apiKey');
  const toggleKeyBtn = document.getElementById('toggleKeyBtn');
  const saveKeyBtn = document.getElementById('saveKeyBtn');

  // Load existing key or mask
  chrome.storage.local.get(['geminiApiKey'], (result) => {
    if (result.geminiApiKey) {
      apiKeyInput.value = result.geminiApiKey;
    }
  });

  // Toggle Visibility
  toggleKeyBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleKeyBtn.innerText = '🔒';
    } else {
      apiKeyInput.type = 'password';
      toggleKeyBtn.innerText = '👁️';
    }
  });

  // Save Key
  saveKeyBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    chrome.storage.local.set({ geminiApiKey: key }, () => {
      saveKeyBtn.innerText = '✓ Key Saved!';
      saveKeyBtn.style.background = '#059669';
      setTimeout(() => {
        saveKeyBtn.innerText = 'Save API Key';
        saveKeyBtn.style.background = '';
      }, 1800);
    });
  });
});
