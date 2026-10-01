"""
Chat Translator AI - Windows Desktop Global Edition
Developer: Md. Rifayet Hossen (Rifat) - Shopify Developer
Works across WhatsApp Desktop, Telegram Desktop, Word, Notepad, Discord, etc.
"""

import sys
import os

if sys.stdout is None:
    try:
        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    except Exception:
        pass
else:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

if sys.stderr is None:
    try:
        sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    except Exception:
        pass
else:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import time
import json
import ctypes
import threading
import keyboard
import pyperclip
from PIL import Image, ImageDraw

import ai_engine
from hud import hud

# Win32 Keyboard Event Constants
user32 = ctypes.windll.user32
VK_CONTROL = 0x11
VK_C = 0x43
VK_V = 0x56
VK_A = 0x41
KEYEVENTF_KEYUP = 0x0002

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(APP_DIR, "config.json")

CURRENT_TONE = "professional"

def load_tone():
    global CURRENT_TONE
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                CURRENT_TONE = data.get("tone", "professional")
    except Exception:
        pass

def save_tone(tone):
    global CURRENT_TONE
    CURRENT_TONE = tone
    try:
        data = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["tone"] = tone
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def release_all_modifiers():
    # Release any stuck modifiers in Windows
    for vk in [0x11, 0x12, 0x10, 0x20, 0x54, 0x42]: # Ctrl, Alt, Shift, Space, T, B
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)

def send_ctrl_key(vk_char):
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(vk_char, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(vk_char, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.03)

# ----------------- OUTGOING TRANSLATION HANDLER -----------------
def handle_outgoing_translation():
    target_hwnd = user32.GetForegroundWindow()
    threading.Thread(target=_do_outgoing_translation, args=(target_hwnd,), daemon=True).start()

def _do_outgoing_translation(target_hwnd):
    # Wait for user to release physical hotkeys
    start_t = time.time()
    while time.time() - start_t < 0.35:
        if not (keyboard.is_pressed('alt') or keyboard.is_pressed('ctrl') or keyboard.is_pressed('shift') or keyboard.is_pressed('space') or keyboard.is_pressed('t')):
            break
        time.sleep(0.02)
    
    release_all_modifiers()
    
    if target_hwnd:
        user32.SetForegroundWindow(target_hwnd)
        time.sleep(0.02)

    # 1. Try to copy currently selected text
    pyperclip.copy("")
    send_ctrl_key(VK_C)
    time.sleep(0.06)
    copied = pyperclip.paste()
    
    # 2. If nothing was selected, select all in current input (Ctrl+A) and copy (Ctrl+C)
    if not copied or not copied.strip():
        send_ctrl_key(VK_A)
        time.sleep(0.05)
        send_ctrl_key(VK_C)
        time.sleep(0.06)
        copied = pyperclip.paste()
    
    text_to_translate = copied.strip()
    if not text_to_translate:
        return
    
    # Translate (do not show any toast yet to preserve window focus)
    translated = ai_engine.translate_outgoing(text_to_translate, tone=CURRENT_TONE)
    if not translated:
        hud.show_toast("Translation Error", "Could not translate text.", is_success=False)
        return
    
    # Put translated text in clipboard and paste (Ctrl+V)
    pyperclip.copy(translated)
    time.sleep(0.04)
    
    if target_hwnd:
        user32.SetForegroundWindow(target_hwnd)
        time.sleep(0.02)
        
    send_ctrl_key(VK_V)
    time.sleep(0.03)
    
    # Play subtle confirmation sound
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass
    
    # Show success toast AFTER replacement is complete
    hud.show_toast(
        "✓ Translated to English", 
        f"Replaced with {CURRENT_TONE.capitalize()} English", 
        is_success=True, 
        duration=2000
    )

# ----------------- INCOMING TRANSLATION HANDLER -----------------
def handle_incoming_translation():
    target_hwnd = user32.GetForegroundWindow()
    threading.Thread(target=_do_incoming_translation, args=(target_hwnd,), daemon=True).start()

def _do_incoming_translation(target_hwnd):
    # Wait for hotkey release
    start_t = time.time()
    while time.time() - start_t < 0.35:
        if not (keyboard.is_pressed('alt') or keyboard.is_pressed('ctrl') or keyboard.is_pressed('shift') or keyboard.is_pressed('b')):
            break
        time.sleep(0.02)
        
    release_all_modifiers()
    
    # Check if text is ALREADY in clipboard (e.g. user right-clicked -> Copy text)
    existing_clip = ""
    try:
        existing_clip = pyperclip.paste().strip()
    except Exception:
        pass
        
    # Also attempt Ctrl+C in case user drag-selected text with mouse
    if target_hwnd:
        user32.SetForegroundWindow(target_hwnd)
        time.sleep(0.02)
        
    send_ctrl_key(VK_C)
    time.sleep(0.06)
    new_clip = ""
    try:
        new_clip = pyperclip.paste().strip()
    except Exception:
        pass
    
    # Use newly copied text or existing copied message
    text_to_translate = new_clip if new_clip else existing_clip
    if not text_to_translate:
        hud.show_toast("Chat Translator AI", "Copy (Ctrl+C) any message or select text, then press Alt+B", is_success=False)
        return
        
    hud.show_toast("⏳ Translating to বাংলা...", "Connecting to Gemini AI...", is_success=True, duration=1500)
    
    bengali_text = ai_engine.translate_incoming(text_to_translate)
    if not bengali_text:
        hud.show_toast("Translation Error", "Could not translate to Bengali.", is_success=False)
        return
        
    # Copy to clipboard for easy reuse
    pyperclip.copy(bengali_text)
    
    # Play subtle confirmation sound
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass
        
    # Show dark-mode card HUD
    hud.show_card("🌐 Bengali Translation (বাংলা)", bengali_text, duration=8000)

# ----------------- SYSTEM TRAY ICON -----------------
def create_tray_image():
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, 60, 60), radius=16, fill="#0b0f19", outline="#10b981", width=3)
    d.ellipse((14, 14, 50, 50), fill="#10b981")
    d.ellipse((26, 26, 38, 38), fill="#0b0f19")
    return img

    def open_dashboard_gui(icon=None, item=None):
        hud.open_dashboard()

    def toggle_widget_gui(icon=None, item=None):
        hud.toggle_floating_widget()

    menu = (
        item("✨ Open AI Dashboard & Translator", open_dashboard_gui, default=True),
        item("🔘 Toggle Floating Translate Button", toggle_widget_gui),
        item("---", None),
        item("🌐 Outgoing: Ctrl+Space / Alt+T", lambda: None, enabled=False),
        item("🇧🇩 Incoming: Alt+B / Ctrl+Shift+B", lambda: None, enabled=False),
        item("---", None),
        item("💼 Tone: Professional", on_tone_click("professional"), checked=is_tone_checked("professional")),
        item("✨ Tone: Friendly", on_tone_click("casual"), checked=is_tone_checked("casual")),
        item("👔 Tone: Executive", on_tone_click("executive"), checked=is_tone_checked("executive")),
        item("---", None),
        item("⚙️ Settings (Edit Config)", open_config),
        item("👨‍💻 Developer: Md. Rifayet Hossen (Rifat)", lambda: None, enabled=False),
        item("---", None),
        item("❌ Exit", exit_app)
    )

    image = create_tray_image()
    tray = pystray.Icon("ChatTranslatorAI", image, "Chat Translator AI (Running)", menu)
    return tray

# ----------------- MAIN ENTRY POINT -----------------
def main():
    load_tone()
    
    print("=" * 60)
    print(" [Chat Translator AI] - Windows Global Desktop Assistant")
    print(" Developed by Md. Rifayet Hossen (Rifat) - Shopify Developer")
    print("=" * 60)
    print(" Hotkeys Active:")
    print("   * Ctrl + Space      : Outgoing Banglish/Bengali -> English (Auto-replace)")
    print("   * Alt + T           : Outgoing Banglish/Bengali -> English (Auto-replace)")
    print("   * Ctrl+Shift+Space  : Outgoing Banglish/Bengali -> English (Auto-replace)")
    print("   * Alt + B           : Incoming English -> Bengali (Bangla Floating Card)")
    print("   * Ctrl+Shift+B      : Incoming English -> Bengali (Bangla Floating Card)")
    print("=" * 60)
    print(" Running silently in the background / system tray...")

    # Register Global Hotkeys
    try:
        keyboard.add_hotkey('ctrl+space', handle_outgoing_translation, suppress=True)
        keyboard.add_hotkey('alt+t', handle_outgoing_translation, suppress=True)
        keyboard.add_hotkey('ctrl+shift+space', handle_outgoing_translation, suppress=True)
        keyboard.add_hotkey('alt+b', handle_incoming_translation, suppress=True)
        keyboard.add_hotkey('ctrl+shift+b', handle_incoming_translation, suppress=True)
    except Exception as e:
        print(f"Warning: Could not bind some hotkeys: {e}")

    # Show startup welcome toast
    hud.show_toast(
        "Chat Translator AI Started", 
        "Global Hotkeys & Floating Widget Active! Press Ctrl+Space or Alt+T.",
        is_success=True,
        duration=3000
    )

    # Show on-screen floating widget
    hud.show_floating_widget(
        on_outgoing=handle_outgoing_translation,
        on_incoming=handle_incoming_translation
    )

    # Launch System Tray
    try:
        tray = setup_tray()
        tray.run()
    except Exception as e:
        print(f"Tray error: {e}")
        keyboard.wait()

if __name__ == "__main__":
    main()
