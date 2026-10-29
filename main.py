from config import ASSISTANT_NAME, HISTORY_LOAD
from core import brain, router
from memory import activity, db
from tools import reminders

HELP = (
    "Commands:\n"
    "  /facts        saare facts dekho\n"
    "  /rules        seekhe hue rules dekho\n"
    "  /log          Lumo ne last 10 tool actions kya kiye\n"
    "  /good         pichla jawab achha tha\n"
    "  /bad          pichla jawab galat tha\n"
    "  /fix <jawab>  jo jawab hona chahiye tha wo likho\n"
    "  exit          band karo\n"
)


def notify(text: str) -> None:
    """Reminder ka time hone par chalta hai (background thread se)."""
    print(f"\n[REMINDER] {text}\nYou: ", end="", flush=True)
    try:
        import winsound

        winsound.Beep(1000, 400)
    except Exception:
        pass


def main() -> None:
    if not brain.check_ollama():
        return

    db.init_db()
    activity.init_activity()
    reminders.start_checker(notify)

    history = db.load_history() or []
    last_user = None
    last_reply = None

    print(f"{ASSISTANT_NAME} ready hai.")
    print(HELP)

    while True:
        text = input("You: ").strip()
        if not text:
            continue
        low = text.lower()

        if low in ("exit", "quit", "bye"):
            print(f"{ASSISTANT_NAME}: Theek hai, bye.")
            break

        if low == "/facts":
            facts = db.get_facts()
            print("\n".join(f"- {f}" for f in facts) if facts else "(abhi koi fact save nahi hai)")
            print()
            continue

        if low == "/rules":
            rules = db.get_rules()
            print("\n".join(f"- {r}" for r in rules) if rules else "(abhi koi rule nahi hai)")
            print()
            continue

        if low == "/log":
            rows = activity.get_recent_log(10)
            if not rows:
                print("(abhi koi tool action nahi hua)")
            for ts, tool, args, result in rows:
                print(f"{ts} | {tool} {args} -> {result[:80]}")
            print()
            continue

        if low in ("/good", "/bad") or low.startswith("/fix"):
            if not last_user:
                print("Pehle koi sawal poochho, phir feedback do.\n")
                continue
            if low == "/good":
                db.save_feedback(last_user, last_reply, 1)
                print("Theek hai, ye jawab achha example ban gaya.\n")
            elif low == "/bad":
                db.save_feedback(last_user, last_reply, -1)
                print("Note kar liya. Sahi jawab batana ho to: /fix <jawab>\n")
            else:
                correction = text[4:].strip()
                if not correction:
                    print("Aise likho: /fix <jo jawab hona chahiye tha>\n")
                    continue
                db.save_feedback(last_user, last_reply, -1, correction)
                print("Samajh gaya, agli baar is style mein jawab dunga.\n")
            continue

        # Pehle router try karo (instant), nahi to LLM
        history.append({"role": "user", "content": text})
        reply = router.try_route(text)
        if reply is None:
            try:
                reply = brain.think(history)
            except Exception as e:
                history.pop()  # fail hua to ye user message wapas hata do
                print("Error:", e, "\n")
                continue

        history.append({"role": "assistant", "content": reply})
        db.save_message("user", text)
        db.save_message("assistant", reply)
        last_user, last_reply = text, reply
        print(f"{ASSISTANT_NAME}: {reply}\n")

        history = history[-HISTORY_LOAD:]
        while history and history[0]["role"] != "user":
            history.pop(0)


if __name__ == "__main__":
    main()