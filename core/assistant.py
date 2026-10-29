from config import HISTORY_LOAD
from core import brain, router
from memory import activity, db


class Assistant:
    """Text aur voice dono ka common dimaag: router -> LLM, aur DB mein save."""

    def __init__(self):
        db.init_db()
        activity.init_activity()
        self.history = db.load_history() or []

    def handle(self, text: str) -> str:
        self.history.append({"role": "user", "content": text})
        reply = router.try_route(text)
        if reply is None:
            try:
                reply = brain.think(self.history)
            except Exception as e:
                self.history.pop()
                print("Error:", e)
                return "Kuch gadbad ho gayi, dobara try karo."

        self.history.append({"role": "assistant", "content": reply})
        db.save_message("user", text)
        db.save_message("assistant", reply)

        self.history = self.history[-HISTORY_LOAD:]
        while self.history and self.history[0]["role"] != "user":
            self.history.pop(0)
        return reply