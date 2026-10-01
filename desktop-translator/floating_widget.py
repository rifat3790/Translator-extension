"""
Floating Translate Widget for Windows Desktop
Always-on-top draggable assistant pill for one-click translation and chat
Developer: Md. Rifayet Hossen (Rifat) - Shopify Developer
"""

import sys
import os
import time
import threading
import tkinter as tk
import pyperclip

import ai_engine
from hud import hud

class FloatingWidget:
    def __init__(self, on_open_dashboard=None, on_outgoing_translate=None, on_incoming_translate=None):
        self.on_open_dashboard = on_open_dashboard
        self.on_outgoing_translate = on_outgoing_translate
        self.on_incoming_translate = on_incoming_translate
        self.win = None
        self._drag_data = {"x": 0, "y": 0}

    def show(self, root=None):
        if self.win and self.win.winfo_exists():
            self.win.deiconify()
            self.win.lift()
            return

        parent = root if root else tk._default_root
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes('-topmost', True)
        self.win.attributes('-alpha', 0.94)
        self.win.configure(bg="#0b0f19")

        # Outer rounded border frame
        container = tk.Frame(
            self.win,
            bg="#131b2e",
            highlightbackground="#10b981",
            highlightthickness=1,
            padx=4,
            pady=4
        )
        container.pack(fill="both", expand=True)

        # Drag handle icon
        drag_handle = tk.Label(
            container,
            text="⋮⋮",
            font=("Segoe UI", 10, "bold"),
            fg="#64748b",
            bg="#131b2e",
            cursor="fleur",
            padx=4
        )
        drag_handle.pack(side="left")

        drag_handle.bind("<ButtonPress-1>", self._start_drag)
        drag_handle.bind("<ButtonRelease-1>", self._stop_drag)
        drag_handle.bind("<B1-Motion>", self._do_drag)

        # 1. Translate Incoming Button (🌐 অনুবাদ)
        btn_bn = tk.Button(
            container,
            text="🌐 অনুবাদ",
            font=("Segoe UI", 9, "bold"),
            bg="#1c2640",
            fg="#34d399",
            activebackground="#10b981",
            activeforeground="white",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._click_translate_incoming
        )
        btn_bn.pack(side="left", padx=2)

        # 2. Translate Outgoing Button (✨ English)
        btn_en = tk.Button(
            container,
            text="✨ English",
            font=("Segoe UI", 9, "bold"),
            bg="#1c2640",
            fg="#f8fafc",
            activebackground="#10b981",
            activeforeground="white",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._click_translate_outgoing
        )
        btn_en.pack(side="left", padx=2)

        # 3. AI Chat Button (🤖)
        btn_chat = tk.Button(
            container,
            text="🤖",
            font=("Segoe UI", 10),
            bg="#1c2640",
            fg="#38bdf8",
            activebackground="#0284c7",
            activeforeground="white",
            bd=0,
            padx=6,
            pady=3,
            cursor="hand2",
            command=self._click_open_chat
        )
        btn_chat.pack(side="left", padx=2)

        # Close / Hide (✕)
        btn_close = tk.Label(
            container,
            text="✕",
            font=("Segoe UI", 8, "bold"),
            fg="#64748b",
            bg="#131b2e",
            cursor="hand2",
            padx=4
        )
        btn_close.pack(side="left", padx=(2, 0))
        btn_close.bind("<Button-1>", lambda e: self.win.withdraw())

        # Position at top-right side of screen by default
        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w = self.win.winfo_width()
        h = self.win.winfo_height()
        x = sw - w - 40
        y = 100
        self.win.geometry(f"+{x}+{y}")

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _stop_drag(self, event):
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def _do_drag(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.win.winfo_x() + deltax
        y = self.win.winfo_y() + deltay
        self.win.geometry(f"+{x}+{y}")

    def _click_translate_incoming(self):
        if self.on_incoming_translate:
            self.on_incoming_translate()
        else:
            threading.Thread(target=self._do_auto_incoming, daemon=True).start()

    def _click_translate_outgoing(self):
        if self.on_outgoing_translate:
            self.on_outgoing_translate()

    def _click_open_chat(self):
        if self.on_open_dashboard:
            self.on_open_dashboard()

    def _do_auto_incoming(self):
        # Read text currently in clipboard
        text = ""
        try:
            text = pyperclip.paste().strip()
        except Exception:
            pass

        if not text:
            hud.show_toast("Chat Translator", "Copy (Ctrl+C) any message first, then click 🌐 অনুবাদ", is_success=False)
            return

        hud.show_toast("⏳ Translating to বাংলা...", "Connecting to Gemini AI...", is_success=True, duration=1500)
        res = ai_engine.translate_incoming(text)
        if res:
            pyperclip.copy(res)
            hud.show_card("🌐 Bengali Translation (বাংলা)", res, duration=6000)
        else:
            hud.show_toast("Translation Error", "Could not translate text.", is_success=False)
