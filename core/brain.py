import ollama

from config import ASSISTANT_NAME, MODEL, NUM_CTX
from memory import db

BASE_SYSTEM = (
     f"You are {ASSISTANT_NAME}, a personal assistant running on the user's laptop. "
    "The user speaks casual Hinglish; reply in short, natural Hinglish (no markdown, no lists). "
    "When the user asks you to remember something, call remember_fact. "
    "When the user asks you to forget something, call forget_fact. "
    "Never store passwords, OTPs, PINs or card details."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "Save a long-term fact about the user so it is remembered across restarts.",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string"}},
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "forget_fact",
            "description": "Delete saved facts that contain the given keyword.",
            "parameters": {
                "type": "object",
                "properties": {"keyword": {"type": "string"}},
                "required": ["keyword"],
            },
        },
    },
]


def check_ollama() -> bool:
    """Ollama chal raha hai aur model download hai ya nahi, ye check karta hai."""
    try:
        ollama.list()
    except Exception:
        print("Ollama se connect nahi ho paya. Start menu se Ollama kholo ya 'ollama serve' chalao.")
        return False
    try:
        ollama.show(MODEL)
    except Exception:
        print(f"Model '{MODEL}' nahi mila. Pehle chalao: ollama pull {MODEL}")
        return False
    return True


def build_system() -> str:
    facts = db.get_facts()
    if not facts:
        return BASE_SYSTEM
    return BASE_SYSTEM + "\n\nThings you know about the user:\n" + "\n".join(f"- {f}" for f in facts)


def run_tool(name: str, args: dict) -> str:
    if name == "remember_fact":
        return db.add_fact(args.get("fact", ""))
    if name == "forget_fact":
        return db.delete_fact(args.get("keyword", ""))
    return "Unknown tool"


def think(history: list) -> str:
    """history mein sirf user/assistant messages hain. Reply text return karta hai."""
    messages = [{"role": "system", "content": build_system()}] + history
    for _ in range(5):  # tool loop ki limit, taaki atak na jaye
        resp = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            options={"num_ctx": NUM_CTX, "temperature": 0.3},
            keep_alive="30m",
        )
        msg = resp.message
        messages.append(msg)

        if not msg.tool_calls:
            return (msg.content or "").strip() or "Ho gaya."

        for call in msg.tool_calls:
            fn = call.function
            output = run_tool(fn.name, dict(fn.arguments))
            print(f"  [tool] {fn.name}({dict(fn.arguments)}) -> {output}")  # debugging ke liye
            messages.append({"role": "tool", "content": output, "tool_name": fn.name})

    return "Ye kaam poora nahi ho paya."