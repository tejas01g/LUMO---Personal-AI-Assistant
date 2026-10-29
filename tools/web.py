import urllib.parse
import webbrowser

# Router in naamon se seedha website khol deta hai
SITES = {
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "google maps": "https://maps.google.com",
    "maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://x.com",
    "whatsapp web": "https://web.whatsapp.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
}


def open_website(url: str) -> str:
    url = url.strip()
    if not url:
        return "No URL given."
    if "://" in url and not url.lower().startswith(("http://", "https://")):
        return "Sirf http/https links allowed hain."
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}"


def web_search(query: str) -> str:
    query = query.strip()
    if not query:
        return "No query given."
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
    return f"Searched Google for: {query}"