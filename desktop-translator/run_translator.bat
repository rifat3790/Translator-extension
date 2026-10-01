@echo off
title Chat Translator AI - Global Desktop Assistant
echo ==============================================================
echo  Chat Translator AI - Windows Global Desktop Assistant
echo  Developed by Md. Rifayet Hossen (Rifat) - Shopify Developer
echo ==============================================================
echo.
echo Hotkeys:
echo   - Alt + T          : Outgoing Banglish/Bengali to English (Auto-Replace)
echo   - Ctrl+Shift+Space : Outgoing Banglish/Bengali to English (Auto-Replace)
echo   - Alt + B          : Incoming English to Bengali (বাংলা Floating Card)
echo   - Ctrl+Shift+B     : Incoming English to Bengali (বাংলা Floating Card)
echo.
echo Launching background service...
cd /d "%~dp0"
uv run --python 3.12 --with keyboard --with pyperclip --with requests --with pystray --with pillow main.py
pause
