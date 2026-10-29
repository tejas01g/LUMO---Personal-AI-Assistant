import difflib
import re

from config import WAKE_WORDS

PRIMARY = "lumo"
TOKEN = re.compile(r"[\w\u0900-\u097F]+")   # English + Devanagari
EXIT_PHRASES = ["band ho ja", "band ho jao", "band ho jaa", "goodbye", "good bye", "stop listening"]
EXIT_WORDS = {"bye", "exit", "quit"}


def find_wake(text: str):
    """(mila, command). Command = wake word ke baad ka text. Sirf shuru ke 4 words dekhta hai."""
    for i, m in enumerate(TOKEN.finditer(text)):
        if i >= 4:
            break
        tok = m.group().lower()
        if tok in WAKE_WORDS or difflib.SequenceMatcher(None, tok, PRIMARY).ratio() >= 0.75:
            return True, text[m.end():].strip(" ,.!?-")
    return False, ""


def is_exit(command: str) -> bool:
    low = command.lower()
    return any(p in low for p in EXIT_PHRASES) or bool(set(TOKEN.findall(low)) & EXIT_WORDS)