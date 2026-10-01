"""
Chat Translator AI - Windows Desktop Global Edition
Developer: Md. Rifayet Hossen (Rifat)
Works across WhatsApp Desktop, Telegram Desktop, Word, Notepad, Discord, etc.
"""

import sys
import os
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

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

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

def send_key_combo(vk_modifier, vk_key):
    user32.keybd_event(vk_modifier, 0, 0, 0)
    user32.keybd_event(vk_key, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(vk_key, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(vk_modifier, 0, KEYEVENTF_KEYUP, 0)

def copy_selected_text():
    # Save previous clipboard
    prev_clipboard = ""
    try:
        prev_clipboard = pyperclip.paste()
    except Exception:
        pass
    
    # Empty clipboard and simulate Ctrl+C
    pyperclip.copy("")
    time.sleep(0.05)
    send_key_combo(VK_CONTROL, VK_C)
    
    # Wait up to 300ms for clipboard update
    copied = ""
    for _ in range(6):
        time.sleep(0.05)
        try:
            copied = pyperclip.paste()
            if copied and copied.strip():
                break
        except Exception:
            pass
            
    return copied, prev_clipboard

# ----------------- OUTGOING TRANSLATION HANDLER -----------------
def handle_outgoing_translation():
    threading.Thread(target=_do_outgoing_translation, daemon=True).start()

def _do_outgoing_translation():
    time.sleep(0.12) # Let user key release settle
    
    copied, prev_clip = copy_selected_text()
    
    # If nothing was selected, try selecting all in current box (Ctrl+A then Ctrl+C)
    if not copied or not copied.strip():
        send_key_combo(VK_CONTROL, VK_A)
        time.sleep(0.06)
        copied, _ = copy_selected_text()
    
    text_to_translate = copied.strip()
    if not text_to_translate:
        hud.show_toast("Chat Translator AI", "No text selected to translate", is_success=False)
        return
    
    hud.show_toast("⏳ AI Translating...", f"Converting to {CURRENT_TONE.capitalize()} English...", is_success=True, duration=2000)
    
    translated = ai_engine.translate_outgoing(text_to_translate, tone=CURRENT_TONE)
    if not translated:
        hud.show_toast("Translation Error", "Could not translate text.", is_success=False)
        return
    
    # Put translated text in clipboard and paste (Ctrl+V)
    pyperclip.copy(translated)
    time.sleep(0.08)
    send_key_combo(VK_CONTROL, VK_V)
    
    hud.show_toast("✓ Translated to English", f"Replaced with {CURRENT_TONE.capitalize()} English", is_success=True, duration=2200)

# ----------------- INCOMING TRANSLATION HANDLER -----------------
def handle_incoming_translation():
    threading.Thread(target=_do_incoming_translation, daemon=True).start()

def _do_incoming_translation():
    time.sleep(0.12) # Wait for key release
    
    copied, prev_clip = copy_selected_text()
    text_to_translate = copied.strip()
    if not text_to_translate:
        hud.show_toast("Chat Translator AI", "Select an incoming message first, then press Alt+B", is_success=False)
        return
        
    hud.show_toast("⏳ Translating to বাংলা...", "Connecting to Gemini AI...", is_success=True, duration=1500)
    
    bengali_text = ai_engine.translate_incoming(text_to_translate)
    if not bengali_text:
        hud.show_toast("Translation Error", "Could not translate to Bengali.", is_success=False)
        return
        
    # Copy to clipboard for easy reuse
    pyperclip.copy(bengali_text)
    
    # Show dark-mode card HUD
    hud.show_card("🌐 Bengali Translation (বাংলা)", bengali_text, duration=6000)

# ----------------- SYSTEM TRAY ICON -----------------
def create_tray_image():
    # Generate 64x64 emerald gradient icon with globe
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Rounded badge background
    d.rounded_rectangle((4, 4, 60, 60), radius=16, fill="#0b0f19", outline="#10b981", width=3)
    # Inner emerald accent
    d.ellipse((14, 14, 50, 50), fill="#10b981")
    # Central dot
    d.ellipse((26, 26, 38, 38), fill="#0b0f19")
    return img

def setup_tray():
    import pystray
    from pystray import MenuItem as item

    def on_tone_click(tone_name):
        def _set(icon, item):
            save_tone(tone_name)
            hud.show_toast("Tone Changed", f"Active tone: {tone_name.capitalize()}", is_success=True)
        return _set

    def is_tone_checked(tone_name):
        return lambda item: CURRENT_TONE == tone_name

    def open_config(icon, item):
        os.system(f'notepad.exe "{CONFIG_PATH}"')

    def exit_app(icon, item):
        icon.stop()
        os._exit(0)

    menu = (
        item("✨ Chat Translator AI (Active)", lambda: None, enabled=False),
        item("🌐 Outgoing English: Alt+T / Ctrl+Shift+Space", lambda: None, enabled=False),
        item("🇧🇩 Incoming Bangla: Alt+B / Ctrl+Shift+B", lambda: None, enabled=False),
        item("---", None),
        item("💼 Tone: Professional", on_tone_click("professional"), checked=is_tone_checked("professional")),
        item("✨ Tone: Friendly", on_tone_click("casual"), checked=is_tone_checked("casual")),
        item("👔 Tone: Executive", on_tone_click("executive"), checked=is_tone_checked("executive")),
        item("---", None),
        item("⚙️ Settings (Edit API Key)", open_config),
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
    print(" 🌐 Chat Translator AI - Windows Global Desktop Assistant")
    print(" Developed by Md. Rifayet Hossen (Rifat) - Shopify Developer")
    print("=" * 60)
    print(" Hotkeys Active:")
    print("   • Alt + T           : Outgoing Banglish/Bengali -> English (Auto-replace)")
    print("   • Ctrl+Shift+Space  : Outgoing Banglish/Bengali -> English (Auto-replace)")
    print("   • Alt + B           : Incoming English -> Bengali (বাংলা Floating Card)")
    print("   • Ctrl+Shift+B      : Incoming English -> Bengali (বাংলা Floating Card)")
    print("=" * 60)
    print(" Running silently in the background / system tray...")

    # Register Global Hotkeys
    try:
        keyboard.add_hotkey('alt+t', handle_outgoing_translation, suppress=True)
        keyboard.add_hotkey('ctrl+shift+space', handle_outgoing_translation, suppress=True)
        keyboard.add_hotkey('alt+b', handle_incoming_translation, suppress=True)
        keyboard.add_hotkey('ctrl+shift+b', handle_incoming_translation, suppress=True)
    except Exception as e:
        print(f"Warning: Could not bind some hotkeys: {e}")

    # Show startup welcome toast
    hud.show_toast(
        "Chat Translator AI Started", 
        "Global Hotkeys Active! Press Alt+T to translate & replace.",
        is_success=True,
        duration=3500
    )

    # Launch System Tray
    try:
        tray = setup_tray()
        tray.run()
    except Exception as e:
        print(f"Tray error: {e}")
        # Keep alive if tray fails
        keyboard.wait()

if __name__ == "__main__":
    main()
