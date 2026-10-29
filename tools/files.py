import os
from pathlib import Path

from config import FILE_SEARCH_DIRS

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "AppData"}
BLOCKED_EXT = {".exe", ".bat", ".cmd", ".ps1", ".msi", ".vbs", ".js", ".lnk", ".scr"}


def _roots() -> list:
    return [d for d in FILE_SEARCH_DIRS if d.exists()]


def find_files(query: str, limit: int = 8) -> str:
    words = [w for w in query.lower().split() if w]
    if not words:
        return "Search ke liye kuch likho."
    roots = _roots()
    if not roots:
        return "Search folders nahi mile. config.py mein FILE_SEARCH_DIRS check karo."

    found = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fname in filenames:
                low = fname.lower()
                if all(w in low for w in words):
                    found.append(str(Path(dirpath) / fname))
                    if len(found) >= limit:
                        return "\n".join(found)
    return "\n".join(found) if found else "Koi file nahi mili."


def open_file(path: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        return "File nahi mili."
    if not any(p.is_relative_to(r.resolve()) for r in _roots()):
        return "Ye file allowed folders ke bahar hai."
    if p.suffix.lower() in BLOCKED_EXT:
        return "Executable/script files yahan se nahi khulti."
    os.startfile(str(p))
    return f"Opened {p.name}"