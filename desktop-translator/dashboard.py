"""
Desktop Dashboard GUI for Chat Translator AI
Includes Quick Translator, ChatGPT-style AI Assistant, Shortcuts, and Settings
Developer: Md. Rifayet Hossen (Rifat) - Shopify Developer
"""

import sys
import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

import ai_engine

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(APP_DIR, "config.json")

class DashboardWindow:
    def __init__(self, on_close_callback=None):
        self.on_close_callback = on_close_callback
        self.win = None
        self.chat_history = []
        self.selected_tone = "professional"

    def show(self):
        if self.win and self.win.winfo_exists():
            self.win.deiconify()
            self.win.lift()
            self.win.focus_force()
            return

        self.win = tk.Toplevel()
        self.win.title("Chat Translator AI — Desktop Assistant")
        self.win.geometry("500x620")
        self.win.minsize(460, 560)
        self.win.configure(bg="#0b0f19")
        self.win.attributes('-topmost', True)

        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self.win.focus_force()

    def _on_close(self):
        if self.win:
            self.win.withdraw()
        if self.on_close_callback:
            self.on_close_callback()

    def _build_ui(self):
        # ----------------- HEADER -----------------
        header = tk.Frame(self.win, bg="#131b2e", padx=16, pady=12, highlightbackground="rgba(255,255,255,0.08)", highlightthickness=1)
        header.pack(fill="x")

        brand_frame = tk.Frame(header, bg="#131b2e")
        brand_frame.pack(side="left")

        icon_lbl = tk.Label(brand_frame, text="✨", font=("Segoe UI", 14), bg="#10b981", fg="white", width=2, height=1)
        icon_lbl.pack(side="left", padx=(0, 10))

        title_frame = tk.Frame(brand_frame, bg="#131b2e")
        title_frame.pack(side="left")

        title_lbl = tk.Label(title_frame, text="Chat Translator AI", font=("Segoe UI", 12, "bold"), fg="#f8fafc", bg="#131b2e")
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(title_frame, text="WhatsApp, Telegram & PC Assistant", font=("Segoe UI", 8), fg="#94a3b8", bg="#131b2e")
        sub_lbl.pack(anchor="w")

        status_badge = tk.Label(header, text="● Active", font=("Segoe UI", 9, "bold"), fg="#10b981", bg="#131b2e", padx=8, pady=3)
        status_badge.pack(side="right")

        # ----------------- TABS NAVIGATION -----------------
        nav_frame = tk.Frame(self.win, bg="#131b2e")
        nav_frame.pack(fill="x")

        self.tab_buttons = {}
        tabs = [
            ("translate", "🌐 Translate"),
            ("ai_chat", "🤖 AI Chat"),
            ("shortcuts", "⚡ Shortcuts"),
            ("settings", "⚙️ Settings")
        ]

        for tab_id, label in tabs:
            btn = tk.Button(
                nav_frame,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg="#131b2e",
                fg="#94a3b8",
                activebackground="#1c2640",
                activeforeground="#34d399",
                bd=0,
                padx=14,
                pady=8,
                cursor="hand2",
                command=lambda tid=tab_id: self._switch_tab(tid)
            )
            btn.pack(side="left", expand=True, fill="x")
            self.tab_buttons[tab_id] = btn

        # ----------------- CONTENT CONTAINER -----------------
        self.container = tk.Frame(self.win, bg="#0b0f19", padx=16, pady=12)
        self.container.pack(fill="both", expand=True)

        self.tab_frames = {
            "translate": self._build_translate_tab(),
            "ai_chat": self._build_chat_tab(),
            "shortcuts": self._build_shortcuts_tab(),
            "settings": self._build_settings_tab()
        }

        # ----------------- FOOTER -----------------
        footer = tk.Frame(self.win, bg="#131b2e", padx=14, pady=8, highlightbackground="rgba(255,255,255,0.08)", highlightthickness=1)
        footer.pack(fill="x", side="bottom")

        author_lbl = tk.Label(footer, text="Developed by Md. Rifayet Hossen (Rifat) • Shopify Developer", font=("Segoe UI", 8), fg="#34d399", bg="#131b2e")
        author_lbl.pack(side="left")

        version_lbl = tk.Label(footer, text="Desktop Edition v2.1", font=("Segoe UI", 8), fg="#64748b", bg="#131b2e")
        version_lbl.pack(side="right")

        self._switch_tab("translate")

    def _switch_tab(self, active_tab_id):
        for tid, frame in self.tab_frames.items():
            if tid == active_tab_id:
                frame.pack(fill="both", expand=True)
                self.tab_buttons[tid].configure(fg="#34d399", bg="#1c2640")
            else:
                frame.pack_forget()
                self.tab_buttons[tid].configure(fg="#94a3b8", bg="#131b2e")

    # ================= TAB 1: TRANSLATE =================
    def _build_translate_tab(self):
        f = tk.Frame(self.container, bg="#0b0f19")

        # Tone Pills Bar
        tone_frame = tk.Frame(f, bg="#0b0f19")
        tone_frame.pack(fill="x", pady=(0, 10))

        self.tone_buttons = {}
        tones = [
            ("professional", "💼 Professional"),
            ("casual", "✨ Friendly"),
            ("executive", "👔 Formal Executive"),
            ("bangla", "🇧🇩 Translate to বাংলা")
        ]

        for tid, tlbl in tones:
            btn = tk.Button(
                tone_frame,
                text=tlbl,
                font=("Segoe UI", 8, "bold"),
                bg="#1c2640",
                fg="#94a3b8",
                activebackground="#10b981",
                activeforeground="white",
                bd=0,
                padx=8,
                pady=4,
                cursor="hand2",
                command=lambda t=tid: self._select_tone(t)
            )
            btn.pack(side="left", padx=3)
            self.tone_buttons[tid] = btn

        self._select_tone("professional")

        # Text input card
        input_card = tk.Frame(f, bg="#1c2640", padx=10, pady=8, highlightbackground="#334155", highlightthickness=1)
        input_card.pack(fill="x", pady=(0, 10))

        self.input_text = tk.Text(input_card, height=4, bg="#1c2640", fg="#f8fafc", font=("Segoe UI", 10), insertbackground="white", bd=0, wrap="word")
        self.input_text.pack(fill="x")
        self.input_text.insert("1.0", "Type Banglish, Bengali, or English here... (e.g. 'thik ache ami kaj kore update dissi')")
        self.input_text.bind("<FocusIn>", self._clear_placeholder)

        # Clear button
        clear_btn = tk.Button(input_card, text="Clear", font=("Segoe UI", 8), bg="#1c2640", fg="#64748b", bd=0, cursor="hand2", command=self._clear_input)
        clear_btn.pack(anchor="e")

        # Translate Action Button
        self.translate_btn = tk.Button(
            f,
            text="✨ Translate Now",
            font=("Segoe UI", 10, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            bd=0,
            pady=8,
            cursor="hand2",
            command=self._do_gui_translate
        )
        self.translate_btn.pack(fill="x", pady=(0, 10))

        # Output Card
        output_card = tk.Frame(f, bg="#111a2e", padx=12, pady=10, highlightbackground="rgba(16,185,129,0.3)", highlightthickness=1)
        output_card.pack(fill="both", expand=True)

        self.output_lbl = tk.Label(output_card, text="Your translated message will appear here...", font=("Nirmala UI", 11), fg="#cbd5e1", bg="#111a2e", wraplength=420, justify="left", anchor="nw")
        self.output_lbl.pack(fill="both", expand=True, anchor="nw")

        action_bar = tk.Frame(output_card, bg="#111a2e")
        action_bar.pack(fill="x", side="bottom", pady=(8, 0))

        self.output_badge = tk.Label(action_bar, text="ENGLISH", font=("Segoe UI", 8, "bold"), fg="#34d399", bg="#111a2e")
        self.output_badge.pack(side="left")

        self.copy_btn = tk.Button(action_bar, text="📋 Copy", font=("Segoe UI", 8, "bold"), bg="#1e293b", fg="#f8fafc", bd=0, padx=8, pady=3, cursor="hand2", command=self._copy_output)
        self.copy_btn.pack(side="right")

        return f

    def _clear_placeholder(self, event):
        content = self.input_text.get("1.0", "end-1c")
        if "Type Banglish, Bengali, or English here..." in content:
            self.input_text.delete("1.0", "end")

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self.output_lbl.configure(text="Your translated message will appear here...")

    def _select_tone(self, tone):
        self.selected_tone = tone
        for tid, btn in self.tone_buttons.items():
            if tid == tone:
                btn.configure(bg="#10b981", fg="white")
            else:
                btn.configure(bg="#1c2640", fg="#94a3b8")
        if tone == "bangla":
            self.output_badge.configure(text="বাংলা (BENGALI)")
        else:
            self.output_badge.configure(text=tone.upper())

    def _copy_output(self):
        text = self.output_lbl.cget("text")
        if text and not text.startswith("Your translated message") and not text.startswith("⏳"):
            pyperclip.copy(text)
            self.copy_btn.configure(text="✓ Copied!", fg="#34d399")
            self.win.after(1500, lambda: self.copy_btn.configure(text="📋 Copy", fg="#f8fafc"))

    def _do_gui_translate(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text or "Type Banglish" in text:
            return

        self.output_lbl.configure(text="⏳ Translating with Gemini AI waterfall...", fg="#94a3b8")
        self.translate_btn.configure(state="disabled", bg="#065f46")

        def _worker():
            if self.selected_tone == "bangla":
                res = ai_engine.translate_incoming(text)
            else:
                res = ai_engine.translate_outgoing(text, tone=self.selected_tone)

            def _update():
                self.translate_btn.configure(state="normal", bg="#10b981")
                if res:
                    self.output_lbl.configure(text=res, fg="#f8fafc")
                else:
                    self.output_lbl.configure(text="❌ Translation failed. Check API key or connection.", fg="#f87171")

            if self.win:
                self.win.after(0, _update)

        threading.Thread(target=_worker, daemon=True).start()

    # ================= TAB 2: AI CHAT (ChatGPT Style) =================
    def _build_chat_tab(self):
        f = tk.Frame(self.container, bg="#0b0f19")

        # Chat message feed box
        feed_frame = tk.Frame(f, bg="#131b2e", highlightbackground="#334155", highlightthickness=1)
        feed_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.chat_display = tk.Text(
            feed_frame,
            bg="#131b2e",
            fg="#f8fafc",
            font=("Segoe UI", 10),
            padx=10,
            pady=10,
            wrap="word",
            state="disabled",
            bd=0
        )
        scrollbar = tk.Scrollbar(feed_frame, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.chat_display.pack(side="left", fill="both", expand=True)

        # Style tags
        self.chat_display.tag_configure("user", foreground="#34d399", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("ai", foreground="#f8fafc", font=("Segoe UI", 10))
        self.chat_display.tag_configure("system", foreground="#94a3b8", font=("Segoe UI", 9, "italic"))

        # Welcome text in chat
        self._append_chat("🤖 Assistant", "Assalamu Alaikum! I am your AI Assistant created by Md. Rifayet Hossen (Rifat). Ask me anything in English, বাংলা, or Banglish!\n")

        # Quick prompt pills
        pills_frame = tk.Frame(f, bg="#0b0f19")
        pills_frame.pack(fill="x", pady=(0, 6))

        prompts = [
            ("👨‍💻 About Developer", "Who is Refayet (Rifat) and what services does he offer?"),
            ("📧 Client Update", "Kaj ta complete kore client k ekta professional update email likhe dao"),
            ("💬 Late Apology", "Meeting e 10 min late hobe, polite vabe ekta message likhe dao")
        ]

        for label, ptext in prompts:
            btn = tk.Button(
                pills_frame,
                text=label,
                font=("Segoe UI", 8),
                bg="#1c2640",
                fg="#34d399",
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda pt=ptext: self._send_chat(pt)
            )
            btn.pack(side="left", padx=2)

        # Chat input bar
        input_bar = tk.Frame(f, bg="#1c2640", padx=8, pady=6, highlightbackground="#334155", highlightthickness=1)
        input_bar.pack(fill="x")

        self.chat_input = tk.Entry(input_bar, bg="#1c2640", fg="#f8fafc", font=("Segoe UI", 10), insertbackground="white", bd=0)
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        send_btn = tk.Button(input_bar, text="Send ➤", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="white", bd=0, padx=10, pady=4, cursor="hand2", command=self._send_chat)
        send_btn.pack(side="right")

        return f

    def _append_chat(self, sender, text):
        self.chat_display.configure(state="normal")
        if "User" in sender:
            self.chat_display.insert("end", f"\n👤 You: ", "user")
        elif "Assistant" in sender:
            self.chat_display.insert("end", f"\n🤖 Rifat's AI: ", "user")
        else:
            self.chat_display.insert("end", f"\n{sender}: ", "system")
        self.chat_display.insert("end", f"{text}\n", "ai")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _send_chat(self, preset_text=None):
        msg = preset_text or self.chat_input.get().strip()
        if not msg:
            return

        if not preset_text:
            self.chat_input.delete(0, "end")

        self._append_chat("👤 User", msg)
        self.chat_history.append({"role": "user", "parts": [{"text": msg}]})

        self._append_chat("System", "Thinking...")

        def _worker():
            developer_prompt = (
                "You are a helpful, intelligent, polite, and professional AI assistant created by Md. Rifayet Hossen "
                "(commonly known as Refayet, Rifat, or Rifayet / রিফাত / রেফায়েত) for this Chat Translator AI assistant.\n\n"
                "DEVELOPER PROFILE:\n"
                "- Name: Md. Rifayet Hossen (Rifat / Refayet)\n"
                "- Profession: Professional Shopify Developer & E-commerce/Web Specialist\n"
                "- WhatsApp/Phone: 01952321390 (+8801952321390)\n"
                "- Email: mdrifayethossen@gmail.com\n"
                "- Facebook: https://www.facebook.com/Rifayet221/\n"
                "- GitHub: https://github.com/rifat3790\n\n"
                "INSTRUCTIONS:\n"
                "If asked about Refayet/Rifat or who developed you, enthusiastically introduce him as an expert Shopify Developer and provide his contact info. "
                "Respond accurately and politely in Bengali, Banglish, or English as requested."
            )

            payload = {
                "contents": self.chat_history,
                "systemInstruction": {"parts": [{"text": developer_prompt}]}
            }

            reply = ai_engine.call_gemini(payload)
            if not reply:
                reply = "I apologize, but I could not reach the server right now. Please check your internet or API key."

            def _update():
                # Remove the "Thinking..." line
                self.chat_display.configure(state="normal")
                # delete last 2 lines
                self.chat_display.delete("end-2l", "end")
                self.chat_display.configure(state="disabled")

                self._append_chat("🤖 Assistant", reply)
                self.chat_history.append({"role": "model", "parts": [{"text": reply}]})

            if self.win:
                self.win.after(0, _update)

        threading.Thread(target=_worker, daemon=True).start()

    # ================= TAB 3: SHORTCUTS =================
    def _build_shortcuts_tab(self):
        f = tk.Frame(self.container, bg="#0b0f19")

        shortcuts = [
            ("🌐 Outgoing Translation", "Ctrl + Space  /  Alt + T", "Translates Banglish/Bengali in your chat box to Professional English and auto-replaces it instantly."),
            ("🇧🇩 Incoming Translation", "Alt + B  /  Ctrl + Shift + B", "Translates any English/foreign message to natural Bengali (বাংলা) and displays a floating card."),
            ("🔘 Floating Widget", "Always Visible on Screen", "Click '🌐 অনুবাদ' to translate incoming messages or '✨ English' to translate outgoing messages.")
        ]

        for title, key, desc in shortcuts:
            card = tk.Frame(f, bg="#131b2e", padx=12, pady=10, highlightbackground="#334155", highlightthickness=1)
            card.pack(fill="x", pady=5)

            tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#131b2e").pack(anchor="w")
            tk.Label(card, text=f"Shortcut: {key}", font=("Consolas", 10, "bold"), fg="#34d399", bg="#131b2e").pack(anchor="w", pady=2)
            tk.Label(card, text=desc, font=("Segoe UI", 8), fg="#94a3b8", bg="#131b2e", wraplength=420, justify="left").pack(anchor="w")

        return f

    # ================= TAB 4: SETTINGS =================
    def _build_settings_tab(self):
        f = tk.Frame(self.container, bg="#0b0f19")

        card = tk.Frame(f, bg="#131b2e", padx=14, pady=14, highlightbackground="#334155", highlightthickness=1)
        card.pack(fill="x", pady=6)

        tk.Label(card, text="Gemini AI API Key", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#131b2e").pack(anchor="w")
        tk.Label(card, text="A high-performance Gemini 3.5 key is pre-configured. You can enter your custom key here:", font=("Segoe UI", 8), fg="#94a3b8", bg="#131b2e", wraplength=420, justify="left").pack(anchor="w", pady=(2, 8))

        self.key_entry = tk.Entry(card, bg="#1c2640", fg="#f8fafc", font=("Consolas", 9), insertbackground="white", bd=0, show="*")
        self.key_entry.pack(fill="x", pady=(0, 10))

        # Load existing key
        existing_key = ai_engine.get_api_key()
        if existing_key:
            self.key_entry.insert(0, existing_key)

        save_btn = tk.Button(card, text="Save API Key", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="white", bd=0, padx=12, pady=6, cursor="hand2", command=self._save_api_key)
        save_btn.pack(anchor="w")

        # Developer info card
        dev_card = tk.Frame(f, bg="#131b2e", padx=14, pady=12, highlightbackground="#10b981", highlightthickness=1)
        dev_card.pack(fill="x", pady=12)

        tk.Label(dev_card, text="👨‍💻 Developer Information", font=("Segoe UI", 10, "bold"), fg="#34d399", bg="#131b2e").pack(anchor="w")
        tk.Label(dev_card, text="Md. Rifayet Hossen (Rifat) — Professional Shopify Developer", font=("Segoe UI", 9), fg="#f8fafc", bg="#131b2e").pack(anchor="w", pady=2)
        tk.Label(dev_card, text="• WhatsApp/Phone: 01952321390\n• Email: mdrifayethossen@gmail.com\n• Facebook: https://www.facebook.com/Rifayet221/", font=("Segoe UI", 8), fg="#94a3b8", bg="#131b2e", justify="left").pack(anchor="w", pady=4)

        return f

    def _save_api_key(self):
        new_key = self.key_entry.get().strip()
        data = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["api_key"] = new_key
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "API Key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save key: {e}")

# Global instance
dashboard = DashboardWindow()
