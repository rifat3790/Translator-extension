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

### 6. 🖥️ Windows Global Desktop Edition (Works Everywhere!)
- Need translation outside the browser? Use the included **Desktop Assistant** located in `desktop-translator/`!
- Works globally in **WhatsApp Desktop (.exe)**, **Telegram Desktop**, **MS Word**, **Notepad**, **Discord**, etc.
  - **`Alt + T`** *(or `Ctrl + Shift + Space`)*: Translates Banglish to Professional English and **auto-replaces** in place!
  - **`Alt + B`** *(or `Ctrl + Shift + B`)*: Select any incoming English message and press `Alt + B` to see a floating **Bengali Translation Card**!
- Includes a standalone **`ChatTranslatorAI.exe`** and System Tray menu with live tone switching.

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

### 🌐 Chrome Extension (WhatsApp Web & Telegram Web)
| Action | How to Trigger | Description |
| :--- | :--- | :--- |
| **Outgoing English** | `Ctrl + Space` | Converts Banglish/Bengali in compose box to Professional English. |
| **Incoming Bengali** | Click `🌐 অনুবাদ` | Translates the selected message bubble to Bengali. |
| **Quick Toggle** | `Double-Click` | Double-click any message bubble to toggle Bengali translation. |
| **Popup Translate** | `Ctrl + Enter` | Translates text inside the extension popup quick chat. |

### 🖥️ Windows Desktop Edition (Telegram Desktop, WhatsApp Desktop, Word, etc.)
| Action | How to Trigger | Description |
| :--- | :--- | :--- |
| **Outgoing English** | `Ctrl + Space` / `Alt + T` | Converts Banglish/Bengali to Professional English & auto-replaces anywhere! |
| **Incoming Bengali** | Click `🌐 অনুবাদ` / `Alt + B` | Translates copied/selected message to natural Bengali with floating card. |
| **Floating Assistant** | Always on Screen | Draggable floating bar with `🌐 অনুবাদ`, `✨ English`, and `🤖 AI Chat`. |
| **Open AI Dashboard** | Click Tray Icon / `🤖` | Opens the full ChatGPT-style desktop AI assistant and translator. |

---

## 🏗️ Project Architecture

```
Translator extension/
├── manifest.json            # Chrome Extension Manifest V3 configuration
├── background.js           # Multi-model AI waterfall & service worker
├── content.js              # DOM observer & Lexical/React synthesizer
├── popup.html              # Modern glassmorphism dashboard UI
├── popup.js                # Popup controller, tone selector & AI chat
├── desktop-translator/     # 🖥️ Windows Global Desktop Edition
│   ├── ChatTranslatorAI.exe # Standalone double-clickable executable
│   ├── main.py             # Global keyboard hooks & tray controller
│   ├── dashboard.py        # Desktop AI Assistant & Translator GUI
│   ├── floating_widget.py  # On-screen draggable floating translate button
│   ├── ai_engine.py        # AI waterfall translation engine
│   ├── hud.py              # Floating card & toast notifications
│   ├── run_translator.bat  # One-click batch launcher
│   └── start_silent.vbs    # Background silent launcher
└── README.md               # Complete project documentation
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

## 👨‍💻 Author & Developer

**Md. Rifayet Hossen (Rifat)**  
*Professional Shopify Developer & Web Specialist*  
Creator of **Chat Translator AI**

- 📱 **WhatsApp / Phone:** [+880 1952321390](https://wa.me/8801952321390) (`01952321390`)
- ✉️ **Email:** [mdrifayethossen@gmail.com](mailto:mdrifayethossen@gmail.com)
- 🌐 **Facebook:** [facebook.com/Rifayet221](https://www.facebook.com/Rifayet221/)
- 💻 **GitHub:** [@rifat3790](https://github.com/rifat3790)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
