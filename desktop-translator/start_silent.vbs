Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "uv run --python 3.12 --with keyboard --with pyperclip --with requests --with pystray --with pillow main.py", 0, False
