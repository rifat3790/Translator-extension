// Chat Translator Popup Script (with ChatGPT-Style AI Chat Assistant)

document.addEventListener('DOMContentLoaded', () => {
  // ----------------- TAB SWITCHING -----------------
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

  // ----------------- QUICK TRANSLATOR TAB -----------------
  let selectedTone = 'professional';
  const toneChips = document.querySelectorAll('.tone-chip');
  toneChips.forEach(chip => {
    chip.addEventListener('click', () => {
      toneChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      selectedTone = chip.getAttribute('data-tone');

      const badge = document.getElementById('outputBadge');
      if (selectedTone === 'bangla') {
        badge.innerText = 'বাংলা (Bengali)';
      } else {
        badge.innerText = selectedTone.toUpperCase();
      }
    });
  });

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

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      doPopupTranslate();
    }
  });


  // ----------------- AI CHATBOT TAB (ChatGPT-style) -----------------
  const chatFeed = document.getElementById('chatFeed');
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  const chatResetBtn = document.getElementById('chatResetBtn');
  const welcomeCard = document.getElementById('chatWelcomeCard');

  let chatHistory = [];

  function formatAIMessage(text) {
    // Basic formatting for bold and line breaks
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:1px 4px;border-radius:3px;">$1</code>')
      .replace(/\n/g, '<br>');
  }

  function appendChatBubble(text, role) {
    if (welcomeCard && welcomeCard.style.display !== 'none') {
      welcomeCard.style.display = 'none';
    }

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    if (role === 'ai') {
      bubble.innerHTML = formatAIMessage(text);
      // Double click to copy AI response
      bubble.title = "Click to copy";
      bubble.style.cursor = "pointer";
      bubble.addEventListener('click', () => {
        navigator.clipboard.writeText(text);
        const originalBg = bubble.style.borderColor;
        bubble.style.borderColor = '#10b981';
        setTimeout(() => bubble.style.borderColor = originalBg, 800);
      });
    } else {
      bubble.innerText = text;
    }

    chatFeed.appendChild(bubble);
    chatFeed.scrollTop = chatFeed.scrollHeight;
    return bubble;
  }

  function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'chatTypingIndicator';
    indicator.innerHTML = `
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    `;
    chatFeed.appendChild(indicator);
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  function hideTypingIndicator() {
    const el = document.getElementById('chatTypingIndicator');
    if (el) el.remove();
  }

  function sendChatMessage(userText) {
    const text = (userText || chatInput.value).trim();
    if (!text) return;

    chatInput.value = '';
    appendChatBubble(text, 'user');

    // Add to multi-turn conversation history
    chatHistory.push({
      role: 'user',
      parts: [{ text: text }]
    });

    chatSendBtn.disabled = true;
    showTypingIndicator();

    chrome.runtime.sendMessage({
      action: "ai_chat",
      messages: chatHistory
    }, (response) => {
      hideTypingIndicator();
      chatSendBtn.disabled = false;
      chatInput.focus();

      if (response && response.success) {
        appendChatBubble(response.text, 'ai');
        chatHistory.push({
          role: 'model',
          parts: [{ text: response.text }]
        });
      } else {
        appendChatBubble(`❌ Error: ${response ? response.error : 'Connection failed'}`, 'ai');
      }
    });
  }

  chatSendBtn.addEventListener('click', () => sendChatMessage());

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });

  // Prompt Pill click handlers
  document.querySelectorAll('.prompt-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const promptText = pill.getAttribute('data-prompt');
      sendChatMessage(promptText);
    });
  });

  // Reset / Clear chat
  chatResetBtn.addEventListener('click', () => {
    chatHistory = [];
    chatFeed.innerHTML = '';
    if (welcomeCard) {
      welcomeCard.style.display = 'block';
      chatFeed.appendChild(welcomeCard);
    }
  });


  // ----------------- SETTINGS TAB: API KEY MANAGEMENT -----------------
  const apiKeyInput = document.getElementById('apiKey');
  const toggleKeyBtn = document.getElementById('toggleKeyBtn');
  const saveKeyBtn = document.getElementById('saveKeyBtn');

  chrome.storage.local.get(['geminiApiKey'], (result) => {
    if (result.geminiApiKey) {
      apiKeyInput.value = result.geminiApiKey;
    }
  });

  toggleKeyBtn.addEventListener('click', () => {
    if (apiKeyInput.type === 'password') {
      apiKeyInput.type = 'text';
      toggleKeyBtn.innerText = '🔒';
    } else {
      apiKeyInput.type = 'password';
      toggleKeyBtn.innerText = '👁️';
    }
  });

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
