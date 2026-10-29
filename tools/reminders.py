import threading
import time

from memory import activity


def set_reminder(text: str, minutes: float) -> str:
    minutes = float(minutes)
    if minutes <= 0 or minutes > 60 * 24 * 30:
        return "Minutes 0 se zyada aur 43200 (30 din) se kam hone chahiye."
    due = activity.add_reminder(text, minutes)
    return f"Reminder set: '{text}' at {due}"


def list_reminders() -> str:
    rows = activity.list_pending()
    if not rows:
        return "Koi pending reminder nahi hai."
    return "\n".join(f"- {text} (at {due})" for text, due in rows)


def start_checker(notify, interval: int = 10) -> None:
    """Background thread: har 'interval' second mein check karta hai ki kisi reminder ka time hua ya nahi."""

    def loop():
        while True:
            try:
                for text in activity.pop_due():
                    notify(text)
            except Exception as e:
                print("Reminder checker error:", e)
            time.sleep(interval)

    threading.Thread(target=loop, daemon=True).start()