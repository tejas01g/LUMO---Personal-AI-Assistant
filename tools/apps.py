import os
import platform
import re
import subprocess

# naam -> kya chalana hai. "cmd:" wale cmd ke through chalte hain.
APPS = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "explorer": "explorer",
    "file manager": "explorer",
    "task manager": "taskmgr",
    "settings": "ms-settings:",
    "cmd": "cmd",
    "terminal": "wt",
    "spotify": "spotify",
    "vscode": "cmd:code",
    "vs code": "cmd:code",
    "code": "cmd:code",
    "whatsapp": "whatsapp:",
    "camera": "microsoft.windows.camera:",
}


def open_app(name: str) -> str:
    if platform.system() != "Windows":
        return "Abhi sirf Windows support hai."

    key = name.strip().lower()
    target = APPS.get(key)
    if target is None:
        # List mein nahi hai to bhi try karo, par sirf safe naam allow hain
        if not re.fullmatch(r"[\w .\-]{1,40}", key):
            return "Invalid app name."
        target = key

    try:
        if target.startswith("cmd:"):
            subprocess.Popen(
                ["cmd", "/c", target[4:]], creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            os.startfile(target)
        return f"Opened {name}"
    except Exception as e:
        return f"Could not open {name}: {e}"