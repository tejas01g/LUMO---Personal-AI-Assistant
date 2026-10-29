import subprocess

from config import SHELL_TIMEOUT

# Ye sirf ek safety net hai (perfect nahi). Asli suraksha confirmation hai.
BLOCKED = [
    " del ", " erase ", " rmdir ", " rd ", " format ", " shutdown ", " diskpart ",
    "reg delete", " remove-item ", " rm ", "mkfs", " cipher ", " takeown ", " icacls ",
    "net user", " -enc ", " -encodedcommand ", " iex ", "downloadstring",
]


def _terminal_confirm(command: str) -> bool:
    ans = input(f"\n[CONFIRM] Ye command chalaun?\n  {command}\n(y/n): ").strip().lower()
    return ans in ("y", "yes", "haan", "ha")


# Voice phase mein is hook ko voice confirmation se badal denge
confirm_fn = _terminal_confirm


def run_shell(command: str) -> str:
    cmd = command.strip()
    if not cmd:
        return "Empty command."
    padded = f" {cmd.lower()} "
    if any(b in padded for b in BLOCKED):
        return "Blocked: ye command khatarnaak lag raha hai, Lumo ise nahi chalayega."
    if not confirm_fn(cmd):
        return "User ne command chalane se mana kar diya."
    try:
        res = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=SHELL_TIMEOUT
        )
        return ((res.stdout or res.stderr or "Done.").strip())[:1500]
    except subprocess.TimeoutExpired:
        return "Command timeout ho gaya."
    except Exception as e:
        return f"Error: {e}"