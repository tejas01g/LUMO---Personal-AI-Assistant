from datetime import datetime

import ollama

from config import ASSISTANT_NAME, EXAMPLES_IN_PROMPT, MODEL, NUM_CTX
from memory import db
from tools import registry
from tools.registry import make_tool

BASE_SYSTEM = (
    f"You are {ASSISTANT_NAME}, a personal assistant running on the user's Windows laptop. "
    "The user speaks casual Hinglish; reply in short, natural Hinglish (no markdown, no lists). "
    "You can control the laptop with tools: open apps and websites, web search, find and open files, "
    "screenshot, battery, volume, brightness, reminders, and shell commands. "
    "For reminders, convert phrases like '10 minute baad' or '2 ghante baad' into minutes from now. "
    "Use run_shell only when no other tool fits. "
    "After a tool succeeds, confirm in one short sentence. "
    "Never claim you did something unless a tool result confirms it. "
    "When the user asks you to remember something about themselves, call remember_fact. "
    "When the user asks you to forget something, call forget_fact. "
    "When the user gives a standing instruction about how you should reply or behave in future "
    "(style, language, length, format), call learn_rule. "
    "To remove such an instruction, call forget_rule. "
    "Never store passwords, OTPs, PINs or card details."
)

MEMORY_TOOLS = [
    make_tool("remember_fact", "Save a long-term fact about the user so it is remembered across restarts.",
              {"fact": {"type": "string"}}, ["fact"]),
    make_tool("forget_fact", "Delete saved facts that contain the given keyword.",
              {"keyword": {"type": "string"}}, ["keyword"]),
    make_tool("learn_rule", "Save a standing instruction about how the assistant should reply or behave in future.",
              {"rule": {"type": "string"}}, ["rule"]),
    make_tool("forget_rule", "Remove saved behavior rules that contain the given keyword.",
              {"keyword": {"type": "string"}}, ["keyword"]),
]

TOOLS = MEMORY_TOOLS + registry.TOOLS


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
    parts = [BASE_SYSTEM, "Current date and time: " + datetime.now().strftime("%A, %d %B %Y, %I:%M %p")]

    facts = db.get_facts()
    if facts:
        parts.append("Things you know about the user:\n" + "\n".join(f"- {f}" for f in facts))

    rules = db.get_rules()
    if rules:
        parts.append("Rules the user taught you (always follow):\n" + "\n".join(f"- {r}" for r in rules))

    examples = db.get_corrections(EXAMPLES_IN_PROMPT)
    if examples:
        lines = [f"User: {u}\nIdeal reply: {c}" for u, c in examples]
        parts.append("Examples of replies the user preferred (match this style):\n" + "\n\n".join(lines))

    return "\n\n".join(parts)


def run_tool(name: str, args: dict) -> str:
    if name == "remember_fact":
        return db.add_fact(args.get("fact", ""))
    if name == "forget_fact":
        return db.delete_fact(args.get("keyword", ""))
    if name == "learn_rule":
        return db.add_rule(args.get("rule", ""))
    if name == "forget_rule":
        return db.delete_rule(args.get("keyword", ""))
    return registry.run(name, args)


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
            args = dict(fn.arguments)
            output = run_tool(fn.name, args)
            print(f"  [tool] {fn.name}({args}) -> {output}")  # debugging ke liye
            messages.append({"role": "tool", "content": output, "tool_name": fn.name})

    return "Ye kaam poora nahi ho paya."