# 🌐 Chat Translator AI (WhatsApp & Telegram Web)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Gemini AI](https://img.shields.io/badge/Powered%20By-Google%20Gemini%203.5-blue.svg)](https://ai.google.dev/)
[![Platform: Chrome Extension](https://img.shields.io/badge/Platform-Chrome%20Extension%20MV3-green.svg)](https://developer.chrome.com/docs/extensions/)
[![Developer: Rifat](https://img.shields.io/badge/Developer-Rifat-emerald.svg)](https://github.com/rifat3790)

> A smart, premium Chrome Extension designed for seamless real-time communication on **WhatsApp Web** and **Telegram Web**. Automatically translate incoming messages to natural Bengali and convert outgoing Banglish (or Bengali) into grammatically perfect, executive-level professional English with a single keystroke.

---

## ✨ Key Features

### 1. 🚀 Instant Outgoing Translation (`Ctrl + Space`)
- Type in **Banglish** (e.g., `thik ache ami ei kaj gula kore tomake update janabo`) or Bengali in your chat box.
- Press **`Ctrl + Space`** — the text is instantly transformed into polished, business-ready English:
  > *"All right, I will complete these tasks and provide you with an update."*
- Full native support for **WhatsApp Web's Lexical Rich-Text Editor** and **Telegram Web (K/A/Z versions)** with zero duplicate text or glitching.

### 2. 🌐 One-Click Incoming Message Translation
- Automatically attaches a single, non-intrusive **`🌐 অনুবাদ`** button to every message bubble.
- Converts English, foreign languages, and even informal Banglish into clear, natural Bengali script (বাংলা লিপি).
- **Double-click shortcut**: Double-click any message bubble to toggle its translation on the fly.

### 3. 🤖 Built-in ChatGPT-Style AI Chatbot
- Open the extension popup and switch to the **🤖 AI Chat** tab.
- Chat naturally with an intelligent AI assistant in **English, বাংলা, or Banglish**.
- Ask questions, brainstorm messages, draft client responses, write professional emails, or get explanations.
- Features multi-turn conversation memory, instant prompt suggestion chips, live typing indicators, and one-click copy.

### 4. 💬 Quick Translator Dashboard
- Translate text directly inside the popup with custom tone controls:
  - 💼 **Professional**: Best for workplace, freelancing, and clients.
  - ✨ **Friendly**: Warm, conversational, polite.
  - 👔 **Formal Executive**: High-level corporate correspondence.
  - 🇧🇩 **Translate to বাংলা**: Instant natural Bengali conversion.
- Features one-click copy (`📋 Copy`) and live character counting.

### 5. ⚡ Intelligent Model Waterfall (Zero Quota Errors)
- Powered by a multi-tiered AI architecture that automatically bypasses rate limits:
  1. **Primary**: `gemini-3.5-flash-lite` (Ultra-fast, fresh quota)
  2. **Secondary**: `gemini-3-flash-preview`
  3. **Tertiary**: `gemini-2.5-flash`
  4. **Universal Fallback**: Free Google Translate Engine
- If any model reaches its rate limit, it cascades seamlessly to the next engine in less than 200ms.

---

## 🛠️ Installation Guide

Follow these simple steps to install the extension in Google Chrome:

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/rifat3790/Translator-extension.git
   ```
   *(Or download the repository as a ZIP file and extract it).*

2. **Open Extensions in Chrome:**
   - In your Chrome URL bar, navigate to:
     ```
     chrome://extensions/
     ```

3. **Enable Developer Mode:**
   - Toggle the **"Developer mode"** switch in the top-right corner.

4. **Load the Extension:**
   - Click the **"Load unpacked"** button in the top-left corner.
   - Select the folder containing this project (`Translator extension`).

5. **Pin & Start Using:**
   - Click the puzzle icon (🧩) in the Chrome toolbar and pin **Chat Translator AI**.
   - Open [WhatsApp Web](https://web.whatsapp.com) or [Telegram Web](https://web.telegram.org) and start chatting!

---

## ⌨️ Keyboard Shortcuts & Usage

| Action | How to Trigger | Description |
| :--- | :--- | :--- |
| **Outgoing English** | `Ctrl + Space` | Converts Banglish/Bengali in compose box to Professional English. |
| **Incoming Bengali** | Click `🌐 অনুবাদ` | Translates the selected message bubble to Bengali. |
| **Quick Toggle** | `Double-Click` | Double-click any message bubble to toggle Bengali translation. |
| **Popup Translate** | `Ctrl + Enter` | Translates text inside the extension popup quick chat. |

---

## 🏗️ Project Architecture

```
Translator extension/
├── manifest.json       # Chrome Extension Manifest V3 configuration
├── background.js      # Service worker: Multi-model AI waterfall & API calls
├── content.js         # DOM observer & Lexical/React event synthesizer
├── popup.html         # Modern glassmorphism dashboard UI
├── popup.js           # Popup controller, tone selector, and clipboard manager
└── README.md          # Complete project documentation
```

### Technical Highlights
- **Manifest V3 Compliant:** Uses lightweight service workers and non-blocking background messaging.
- **Lexical Editor Reconciliation:** Overcomes Meta's complex Lexical virtual DOM synchronization using trusted clipboard `DataTransfer` events and atomic deletion.
- **Race Condition Prevention:** MutationObservers are locked during DOM mutations with debounce protection to prevent infinite attachment loops.

---

## ⚙️ API Configuration

A high-performance **Google Gemini 3.5 AI** key is already configured out-of-the-box. 

If you prefer using your own personal API key:
1. Open the extension popup.
2. Go to the **⚙️ Settings** tab.
3. Paste your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and click **Save API Key**.

---

## 👨‍💻 Author

**Developed with ❤️ by Rifat**
- GitHub: [@rifat3790](https://github.com/rifat3790)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
