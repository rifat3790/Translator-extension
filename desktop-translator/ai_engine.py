"""
AI Translation Engine with Waterfall Multi-Model Fallback
Created for Chat Translator AI (Desktop Edition)
Developer: Md. Rifayet Hossen (Rifat)
"""

import sys
import os
import json
import base64
import urllib.parse
import requests

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(APP_DIR, "config.json")

_KEY_B64 = "QVEuQWI4Uk42TDlJUzdpa0VuVVN4RTN3NTJtdXpZSXVVWGNTdnpGaE13OEFLMVRGdnoyYUE="
DEFAULT_API_KEY = base64.b64decode(_KEY_B64).decode()

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash"
]

def get_api_key():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                key = data.get("api_key", "").strip()
                if key:
                    return key
    except Exception:
        pass
    
    meipass = getattr(sys, '_MEIPASS', '')
    if meipass:
        bundled = os.path.join(meipass, "config.json")
        if os.path.exists(bundled):
            try:
                with open(bundled, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    key = data.get("api_key", "").strip()
                    if key:
                        return key
            except Exception:
                pass
                
    return DEFAULT_API_KEY

def call_gemini(payload, model_index=0):
    if model_index >= len(MODELS):
        return None
    
    model = MODELS[model_index]
    api_key = get_api_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
        data = response.json()
        
        if "error" in data:
            print(f"[{model}] Error: {data['error'].get('message')}")
            # Rate limit or quota exhausted -> try next model
            return call_gemini(payload, model_index + 1)
        
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            for p in reversed(parts):
                if "text" in p and not p.get("thought", False):
                    text = p["text"].strip()
                    if text:
                        return text
        
        return call_gemini(payload, model_index + 1)
    except Exception as e:
        print(f"[{model}] Exception: {e}")
        return call_gemini(payload, model_index + 1)

def fallback_google_translate(text, target_lang="en"):
    try:
        q = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={q}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data and len(data) > 0 and data[0]:
            translated_pieces = [item[0] for item in data[0] if item and item[0]]
            return "".join(translated_pieces).strip()
    except Exception as e:
        print(f"[Google Translate Fallback] Error: {e}")
    return None

def translate_outgoing(text, tone="professional"):
    if not text or not text.strip():
        return ""
    
    tone_instruction = "fluent, natural, grammatically correct, and professional English suitable for a workplace or client conversation"
    if tone == "casual":
        tone_instruction = "friendly, warm, natural, and polite conversational English"
    elif tone == "executive":
        tone_instruction = "formal, polished, executive-level corporate English"
    
    prompt = (
        f"You are a professional business translator and editor. Translate the following Banglish "
        f"(Bengali written in English letters or Latin script) or Bengali text into {tone_instruction}. "
        f"Output ONLY the translated English sentence(s). Do not add explanations, notes, or quotation marks:\n\n{text}"
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    result = call_gemini(payload)
    if result:
        return result
    
    # Fallback
    fallback = fallback_google_translate(text, target_lang="en")
    return fallback if fallback else text

def translate_incoming(text):
    if not text or not text.strip():
        return ""
    
    prompt = (
        "Translate the following chat message (which may be in English, Banglish/Latin script Bengali, or another language) "
        "into natural, fluent Bengali (বাংলা). Output ONLY the final Bengali translation in Bengali script. "
        f"Do not output English or explanations or quotes:\n\n{text}"
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    result = call_gemini(payload)
    if result:
        return result
    
    # Fallback
    fallback = fallback_google_translate(text, target_lang="bn")
    return fallback if fallback else text
