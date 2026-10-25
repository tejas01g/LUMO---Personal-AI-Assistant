from config import ASSISTANT_NAME, HISTORY_LOAD
from core import brain
from memory import db

def main() -> None:
    if not brain.check_ollama():
        return

    db.init_db()
    history = db.load_history()
    print(f"{ASSISTANT_NAME} ready hai.")
    print("Commands: /facts (saare facts dekho), exit (band karo)\n")

    while True:
        text = input("you: "). strip()
        if not text:
            continue
        if text.lower() in ("exit", "quit" , "bye"):
            print(f"{ASSISTANT_NAME}: Theek hai, bye.")
            break
        if text.lower() == "/facts":
            facts = db.get_facts()
            print("\n".join(f"- {f}" for f in facts) if facts else "(abhi koi fact save nhi h)")
            print()
            continue

        history.append({"role": "user", "content": text})
        try:
            reply = brain.think(history)
        except Exception as e:
            history.pop()  # fail hua to ye user message wapas hata do
            print("Error:", e, "\n")
            continue

        history.append({"role": "assistant", "content": reply})
        db.save_message("user", text)
        db.save_message("assistant", reply)
        print(f"{ASSISTANT_NAME}: {reply}\n")

        history = history[-HISTORY_LOAD:]
        while history and history[0]["role"] != "user":
            history.pop(0)


if __name__ == "__main__":
    main()