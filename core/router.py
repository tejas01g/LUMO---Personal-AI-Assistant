import re

from tools import registry, web

OPEN_TOKENS = {"kholo", "khol", "open", "start", "chalu", "launch", "chalao", "chala"}
FILLER = {"do", "karo", "kar", "de", "dena", "please", "plz", "pls", "ko", "app",
          "application", "mujhe", "zara", "jara", "na", "ek", "the", "a"}

# Time/date poochne ke liye: in words mein se koi ho aur sentence chhota ho
TIME_WORDS = {"time", "samay", "baje", "date", "tareekh", "tarikh"}
NOT_TIME_WORDS = {"reminder", "yaad", "alarm", "set", "zone", "timer"}

# Ye words ho to LLM ko sochne do (jaise "chrome pe youtube kholo")
COMPLEX_WORDS = {"pe", "par", "mein", "me", "on", "in", "se", "ka", "ki", "and", "aur", "phir"}

SEARCH_PATTERNS = [
    r"^(?:search|google)\s+(.+)$",
    r"^(.+?)\s+(?:search karo|search kar do|search kar|google karo|dhundo|dhundh)$",
]


def try_route(text: str):
    """Simple commands ka seedha jawab deta hai. None matlab LLM ko bhejo."""
    t = text.lower().strip().rstrip("?.! ")
    if not t:
        return None
    tokens = t.split()
    words = set(tokens)

    # time / date
    if words & TIME_WORDS and not (words & NOT_TIME_WORDS) and len(words) <= 5:
        return "Abhi: " + registry.run("get_time", {})

    # screenshot, battery
    if "screenshot" in t:
        return registry.run("take_screenshot", {})
    if "battery" in t:
        return registry.run("battery_status", {})

    # volume
    if "volume" in t or "awaaz" in t or t == "mute":
        if "mute" in t:
            return registry.run("set_volume", {"action": "mute"})
        if any(w in t for w in ["badha", "up", "increase", "zyada", "tez"]):
            return registry.run("set_volume", {"action": "up"})
        if any(w in t for w in ["kam", "down", "ghata", "decrease", "dheema"]):
            return registry.run("set_volume", {"action": "down"})

    # web search (sirf saaf patterns)
    for pattern in SEARCH_PATTERNS:
        m = re.match(pattern, t)
        if m:
            query = m.group(1).strip()
            registry.run("web_search", {"query": query})
            return f"'{query}' search kar diya."

    # app ya website kholna: "chrome kholo", "youtube kholo", "spotify open karo"
    if (OPEN_TOKENS & words) and not (words & COMPLEX_WORDS):
        target = " ".join(w for w in tokens if w not in OPEN_TOKENS and w not in FILLER)
        if target and len(target.split()) <= 3:
            if target in web.SITES:
                registry.run("open_website", {"url": web.SITES[target]})
                return f"{target} khol diya."
            result = registry.run("open_app", {"name": target})
            if result.startswith("Opened"):
                return f"{target} khol diya."
            return result

    return None