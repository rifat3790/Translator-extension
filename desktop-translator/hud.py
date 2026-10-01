"""
Floating HUD Notification Overlay for Windows
Modern glassmorphic Dark-Mode UI using Tkinter
Developer: Md. Rifayet Hossen (Rifat)
"""

import threading
import queue
import time
import ctypes
import tkinter as tk
from tkinter import ttk

user32 = ctypes.windll.user32

def _apply_non_activating(win):
    try:
        win.update_idletasks()
        hwnd = win.winfo_id()
        root_hwnd = user32.GetAncestor(hwnd, 2)
        target = root_hwnd if root_hwnd else hwnd
        style = user32.GetWindowLongW(target, -20)
        # WS_EX_NOACTIVATE = 0x08000000, WS_EX_TOPMOST = 0x00000008
        user32.SetWindowLongW(target, -20, style | 0x08000000 | 0x00000008)
    except Exception:
        pass

class TranslatorHUD:
    def __init__(self):
        self.msg_queue = queue.Queue()
        self.root = None
        self.current_window = None
        self.hide_timer_id = None
        
        # Start GUI thread
        self.gui_thread = threading.Thread(target=self._run_gui_loop, daemon=True)
        self.gui_thread.start()
        
        # Wait until root is initialized
        for _ in range(50):
            if self.root is not None:
                break
            time.sleep(0.05)

    def _run_gui_loop(self):
        self.root = tk.Tk()
        self.root.withdraw() # Hide root window
        
        # Periodically check message queue
        self._check_queue()
        self.root.mainloop()

    def _check_queue(self):
        try:
            while not self.msg_queue.empty():
                item = self.msg_queue.get_nowait()
                msg_type = item.get("type")
                if msg_type == "toast":
                    self._render_toast(item)
                elif msg_type == "card":
                    self._render_card(item)
                elif msg_type == "close":
                    self._close_window()
        except Exception as e:
            print(f"HUD Queue error: {e}")
            
        if self.root:
            self.root.after(100, self._check_queue)

    def _close_window(self):
        if self.current_window:
            try:
                self.current_window.destroy()
            except Exception:
                pass
            self.current_window = None

    def _render_toast(self, item):
        self._close_window()
        
        win = tk.Toplevel(self.root)
        self.current_window = win
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.attributes('-alpha', 0.95)
        win.configure(bg="#0b0f19")
        
        title = item.get("title", "Translator AI")
        message = item.get("message", "")
        status_color = "#10b981" if item.get("is_success", True) else "#f87171"
        
        frame = tk.Frame(win, bg="#131b2e", highlightbackground="#10b981", highlightthickness=1, padx=14, pady=10)
        frame.pack(fill="both", expand=True)
        
        lbl_title = tk.Label(frame, text=title, font=("Segoe UI", 9, "bold"), fg=status_color, bg="#131b2e")
        lbl_title.pack(anchor="w")
        
        lbl_msg = tk.Label(frame, text=message, font=("Segoe UI", 9), fg="#f8fafc", bg="#131b2e")
        lbl_msg.pack(anchor="w", pady=(2, 0))
        
        # Position at bottom-right corner of primary screen
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = screen_w - w - 25
        y = screen_h - h - 65
        win.geometry(f"+{x}+{y}")
        _apply_non_activating(win)
        
        win.bind("<Button-1>", lambda e: self._close_window())
        frame.bind("<Button-1>", lambda e: self._close_window())
        
        duration = item.get("duration", 2500)
        self.root.after(duration, self._close_window)

    def _render_card(self, item):
        self._close_window()
        
        win = tk.Toplevel(self.root)
        self.current_window = win
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.attributes('-alpha', 0.98)
        win.configure(bg="#0b0f19")
        
        title = item.get("title", "🌐 Bengali Translation")
        text = item.get("text", "")
        
        frame = tk.Frame(win, bg="#131b2e", highlightbackground="rgba(255, 255, 255, 0.12)", highlightthickness=1, padx=16, pady=12)
        frame.pack(fill="both", expand=True)
        
        # Header bar
        header = tk.Frame(frame, bg="#131b2e")
        header.pack(fill="x", pady=(0, 6))
        
        lbl_title = tk.Label(header, text=title, font=("Segoe UI", 10, "bold"), fg="#34d399", bg="#131b2e")
        lbl_title.pack(side="left")
        
        close_btn = tk.Label(header, text="✕", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#131b2e", cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self._close_window())
        
        # Translation body box
        body_box = tk.Frame(frame, bg="#1c2640", padx=10, pady=8, highlightbackground="#334155", highlightthickness=1)
        body_box.pack(fill="both", expand=True)
        
        # Bengali text display
        lbl_text = tk.Label(
            body_box, 
            text=text, 
            font=("Nirmala UI", 11), 
            fg="#f8fafc", 
            bg="#1c2640", 
            wraplength=380, 
            justify="left"
        )
        lbl_text.pack(anchor="w", fill="both")
        
        # Footer
        footer = tk.Frame(frame, bg="#131b2e")
        footer.pack(fill="x", pady=(8, 0))
        
        badge = tk.Label(footer, text="✓ Copied to Clipboard", font=("Segoe UI", 8, "bold"), fg="#10b981", bg="#131b2e")
        badge.pack(side="left")
        
        credit = tk.Label(footer, text="by Md. Rifayet Hossen (Rifat)", font=("Segoe UI", 8), fg="#64748b", bg="#131b2e")
        credit.pack(side="right")
        
        # Position near bottom-right or center
        win.update_idletasks()
        w = max(win.winfo_width(), 360)
        h = win.winfo_height()
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = screen_w - w - 30
        y = screen_h - h - 70
        win.geometry(f"{w}x{h}+{x}+{y}")
        _apply_non_activating(win)
        
        # Click to close
        win.bind("<Button-1>", lambda e: self._close_window())
        
        duration = item.get("duration", 5000)
        self.root.after(duration, self._close_window)

    def show_toast(self, title, message, is_success=True, duration=2500):
        self.msg_queue.put({
            "type": "toast",
            "title": title,
            "message": message,
            "is_success": is_success,
            "duration": duration
        })

    def show_card(self, title, text, duration=5000):
        self.msg_queue.put({
            "type": "card",
            "title": title,
            "text": text,
            "duration": duration
        })

# Global singleton
hud = TranslatorHUD()
