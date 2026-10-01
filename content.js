// Chat Translator Content Script (Universal WhatsApp & Telegram Web Support)

console.log("[Chat Translator] Initializing on:", window.location.hostname);

// ----------------- TOAST NOTIFICATION FOR USER FEEDBACK -----------------
let toastEl = null;

function showToast(message, type = 'info', duration = 2500) {
  if (!toastEl) {
    toastEl = document.createElement('div');
    toastEl.id = 'chat-translator-toast';
    toastEl.style.cssText = `
      position: fixed;
      bottom: 85px;
      right: 25px;
      z-index: 9999999;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      box-shadow: 0 4px 14px rgba(0,0,0,0.18);
      pointer-events: none;
      transition: opacity 0.25s ease, transform 0.25s ease;
      opacity: 0;
      transform: translateY(10px);
    `;
    document.body.appendChild(toastEl);
  }

  if (type === 'loading') {
    toastEl.style.background = '#0284c7';
    toastEl.style.color = '#ffffff';
  } else if (type === 'success') {
    toastEl.style.background = '#16a34a';
    toastEl.style.color = '#ffffff';
  } else if (type === 'error') {
    toastEl.style.background = '#dc2626';
    toastEl.style.color = '#ffffff';
  } else {
    toastEl.style.background = '#334155';
    toastEl.style.color = '#ffffff';
  }

  toastEl.innerText = message;
  toastEl.style.opacity = '1';
  toastEl.style.transform = 'translateY(0)';

  if (type !== 'loading' && duration > 0) {
    clearTimeout(toastEl._timer);
    toastEl._timer = setTimeout(() => {
      if (toastEl) {
        toastEl.style.opacity = '0';
        toastEl.style.transform = 'translateY(10px)';
      }
    }, duration);
  }
}

function hideToast() {
  if (toastEl) {
    toastEl.style.opacity = '0';
    toastEl.style.transform = 'translateY(10px)';
  }
}


// ----------------- INCOMING MESSAGES (Translate to Bengali) -----------------

// Helper to extract clean message text
function cleanMessageText(text) {
  if (!text) return "";
  return text
    // Remove timestamps like 7:23 pm, 10:13, etc. (even if attached without space)
    .replace(/\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?/gi, '')
    .replace(/🌐\s*অনুবাদ/g, '')
    .replace(/বাংলা:\s*.*$/gs, '')
    .replace(/[\u2713\u2714\u2705\u202F\u00A0\u200B-\u200D\uFEFF]/g, ' ')
    .trim();
}

function extractTextFromContainer(container) {
  // If container has specific text span without timestamp (e.g. WhatsApp span[dir="ltr"])
  const textSpan = container.querySelector('.copyable-text span, span.selectable-text, .text-content, .message-text, span[dir="ltr"]');
  if (textSpan) {
    const cleaned = cleanMessageText(textSpan.innerText);
    if (cleaned.length >= 2) return cleaned;
  }

  const clone = container.cloneNode(true);
  clone.querySelectorAll('.translate-btn, .translate-btn-wrapper, .translated-box, time, .time, [data-testid="msg-meta"], svg').forEach(el => el.remove());
  return cleanMessageText(clone.innerText);
}

// Function to translate and display Bengali translation
function translateElement(messageContainer, textHolder) {
  const box = messageContainer.querySelector('.translated-box');
  if (messageContainer.dataset.translated === "true") {
    if (box) box.style.display = box.style.display === 'none' ? 'block' : 'none';
    return;
  }
  if (messageContainer.dataset.translating === "true") return;

  const textToTranslate = extractTextFromContainer(textHolder || messageContainer);
  if (!textToTranslate || textToTranslate.length < 2) return;

  messageContainer.dataset.translating = "true";

  let resultBox = box;
  if (!resultBox) {
    resultBox = document.createElement('div');
    resultBox.className = 'translated-box';
    resultBox.style.cssText = `
      margin-top: 6px;
      margin-bottom: 2px;
      padding: 6px 10px;
      background: #e8f5e9;
      border-left: 3px solid #2e7d32;
      border-radius: 4px;
      color: #1b5e20;
      font-size: 13px;
      line-height: 1.4;
      word-break: break-word;
      font-family: system-ui, -apple-system, sans-serif;
      user-select: text;
      display: block;
    `;
    (textHolder || messageContainer).appendChild(resultBox);
  }

  resultBox.innerHTML = '<em>⏳ অনুবাদ হচ্ছে...</em>';

  chrome.runtime.sendMessage({
    action: "translate_incoming",
    text: textToTranslate
  }, (response) => {
    delete messageContainer.dataset.translating;
    if (response && response.success) {
      messageContainer.dataset.translated = "true";
      resultBox.innerHTML = `<strong>বাংলা:</strong> ${response.text}`;
    } else {
      resultBox.innerHTML = `<span style="color: #c62828;">❌ অনুবাদ করা যায়নি</span>`;
      setTimeout(() => resultBox.remove(), 3000);
    }
  });
}

function createTranslateButton(onClick) {
  const btn = document.createElement('button');
  btn.className = 'translate-btn';
  btn.innerText = '🌐 অনুবাদ';
  btn.title = 'বাংলায় অনুবাদ করুন';
  btn.style.cssText = `
    display: inline-block;
    margin-top: 4px;
    margin-bottom: 2px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 500;
    color: #00796b;
    background: rgba(0, 121, 107, 0.08);
    border: 1px solid rgba(0, 121, 107, 0.25);
    border-radius: 12px;
    cursor: pointer;
    line-height: 1.2;
    transition: all 0.2s ease;
    user-select: none;
    vertical-align: middle;
  `;

  btn.addEventListener('mouseenter', () => {
    btn.style.background = '#00796b';
    btn.style.color = '#ffffff';
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.background = 'rgba(0, 121, 107, 0.08)';
    btn.style.color = '#00796b';
  });

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    onClick();
  });

  return btn;
}

let isMutating = false;

// Attach exactly ONE translate button per message
function attachTranslateButtons() {
  if (isMutating) return;
  isMutating = true;

  try {
    const isWhatsApp = window.location.hostname.includes('whatsapp.com');

    if (isWhatsApp) {
      // In WhatsApp Web, each message is uniquely wrapped in a div[role="row"]
      const messageRows = document.querySelectorAll('div[role="row"]:not([data-tr-attached])');

      messageRows.forEach(row => {
        // Exclude side contact list, header, footer/compose box
        if (row.closest('#side, header, footer, form, [contenteditable="true"]')) return;

        row.setAttribute('data-tr-attached', 'true');

        // Check if button already exists in this row
        if (row.querySelector('.translate-btn')) return;

        // WhatsApp text holder
        const textHolder = row.querySelector('.copyable-text, .selectable-text, span[dir="ltr"]') || row;
        const text = extractTextFromContainer(textHolder);
        if (!text || text.length < 2) return;

        // Find visual bubble container
        const bubble = row.querySelector('[data-pre-plain-text]') || 
                       row.querySelector('.copyable-text') || 
                       row.firstElementChild || 
                       row;

        if (bubble.querySelector('.translate-btn')) return;

        const btn = createTranslateButton(() => {
          translateElement(bubble, textHolder);
        });

        const wrapper = document.createElement('div');
        wrapper.className = 'translate-btn-wrapper';
        wrapper.style.cssText = 'display: block; margin-top: 3px; clear: both;';
        wrapper.appendChild(btn);

        bubble.appendChild(wrapper);
      });
    } else {
      // Telegram Web (K and Z/A versions)
      const tgMessages = document.querySelectorAll('.message:not([data-tr-attached]), .Message:not([data-tr-attached])');

      tgMessages.forEach(msg => {
        if (msg.closest('form, [contenteditable="true"]')) return;

        msg.setAttribute('data-tr-attached', 'true');

        if (msg.querySelector('.translate-btn')) return;

        const textHolder = msg.querySelector('.text-content, .message-text') || msg;
        const text = extractTextFromContainer(textHolder);
        if (!text || text.length < 2) return;

        const btn = createTranslateButton(() => {
          translateElement(msg, textHolder);
        });

        textHolder.appendChild(btn);
      });
    }
  } finally {
    isMutating = false;
  }
}

// Double click anywhere on a message to translate
window.addEventListener('dblclick', (e) => {
  const target = e.target;
  if (target.isContentEditable || target.closest('footer, header, #side, [contenteditable="true"], input, textarea')) return;

  const msgRow = target.closest('div[role="row"], .message, .Message');
  if (msgRow) {
    const textHolder = msgRow.querySelector('.copyable-text, .selectable-text, .text-content, .message-text, span[dir="ltr"]') || msgRow;
    translateElement(msgRow, textHolder);
  }
}, true);


// ----------------- OUTGOING MESSAGES (Ctrl + Space -> Professional English) -----------------

// Locate active chat input field across WhatsApp Web and Telegram Web
function findChatInputField() {
  const active = document.activeElement;
  if (active && (active.isContentEditable || active.tagName === 'TEXTAREA' || active.tagName === 'INPUT')) {
    if (!active.closest('#side')) {
      return active.closest('[contenteditable="true"]') || active;
    }
  }

  // WhatsApp Web compose box
  const waCompose = 
    document.querySelector('[data-testid="conversation-compose-box-input"]') ||
    document.querySelector('footer div[contenteditable="true"]') ||
    document.querySelector('div[contenteditable="true"][data-lexical-editor="true"]') ||
    document.querySelector('div[contenteditable="true"][data-tab="10"]') ||
    document.querySelector('footer [role="textbox"][contenteditable="true"]') ||
    document.querySelector('div[role="textbox"][contenteditable="true"]:not([data-tab="3"])');

  if (waCompose) return waCompose;

  // Telegram Web compose box
  const tgCompose = 
    document.querySelector('#editable-message-text') ||
    document.querySelector('.input-message-input');

  if (tgCompose) return tgCompose;

  // General fallback
  const allEditables = document.querySelectorAll('div[contenteditable="true"]');
  for (const el of allEditables) {
    if (!el.closest('#side, header')) {
      return el;
    }
  }

  return null;
}

let isTranslating = false;

// Translate the user input
function translateActiveInput() {
  if (isTranslating) return;

  const inputEl = findChatInputField();
  if (!inputEl) {
    console.warn("[Chat Translator] No chat compose box detected");
    return;
  }

  const originalText = (inputEl.isContentEditable ? inputEl.innerText : inputEl.value) || "";
  if (!originalText.trim()) return;

  isTranslating = true;
  showToast("⏳ Translating to English...", "loading", 0);

  chrome.runtime.sendMessage({
    action: "translate_outgoing",
    text: originalText.trim()
  }, (response) => {
    isTranslating = false;

    if (response && response.success) {
      applyTranslatedText(inputEl, response.text, originalText.trim());
      showToast("✅ English updated!", "success", 1500);
    } else {
      showToast("❌ " + (response ? response.error : "Failed"), "error", 3500);
    }
  });
}

// Universal text replacement that cleanly replaces text in WhatsApp & Telegram
function applyTranslatedText(element, newText) {
  element.focus();

  // 1. Select all content inside the editor
  const sel = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(element);
  sel.removeAllRanges();
  sel.addRange(range);

  // 2. Try DataTransfer paste simulation (primary standard for Lexical/WhatsApp)
  let pasteDispatched = false;
  try {
    const dt = new DataTransfer();
    dt.setData('text/plain', newText);
    const pasteEvent = new ClipboardEvent('paste', {
      clipboardData: dt,
      bubbles: true,
      cancelable: true
    });
    pasteDispatched = element.dispatchEvent(pasteEvent);
  } catch (err) {
    console.warn("[Chat Translator] Paste event error:", err);
  }

  // 3. Fallback for Telegram Web or if paste was not intercepted
  setTimeout(() => {
    if (element.innerText.trim() !== newText.trim()) {
      range.selectNodeContents(element);
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand('insertText', false, newText);
    }

    // Notify React / Lexical of the state change
    element.dispatchEvent(new InputEvent('input', {
      bubbles: true,
      cancelable: true,
      inputType: 'insertText',
      data: newText
    }));
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));

    // Move cursor to the end
    try {
      const endRange = document.createRange();
      endRange.selectNodeContents(element);
      endRange.collapse(false);
      sel.removeAllRanges();
      sel.addRange(endRange);
    } catch (e) {}
  }, 30);
}

// Global hotkey listener: Ctrl + Space (with debounce to prevent duplicate firing)
let lastHotkeyTime = 0;

function handleGlobalKey(e) {
  if (e.ctrlKey && (e.code === 'Space' || e.key === ' ' || e.keyCode === 32)) {
    const now = Date.now();
    if (now - lastHotkeyTime < 800) {
      e.preventDefault();
      return;
    }
    lastHotkeyTime = now;

    const composeEl = findChatInputField();
    if (composeEl) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      translateActiveInput();
    }
  }
}

// Attach ONLY to window to avoid duplicate triggers
window.addEventListener('keydown', handleGlobalKey, true);

// Dynamic observer for incoming messages
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

const observer = new MutationObserver(debounce(() => {
  if (isMutating) return;
  attachTranslateButtons();
}, 300));

observer.observe(document.body, { childList: true, subtree: true });

// Run initial attachment
setTimeout(attachTranslateButtons, 600);
setTimeout(attachTranslateButtons, 2000);

console.log("[Chat Translator] Ready for WhatsApp and Telegram!");
