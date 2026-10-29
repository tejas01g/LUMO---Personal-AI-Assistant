import sqlite3
from contextlib import closing
from datetime import datetime, timedelta

from config import DB_PATH

FMT = "%Y-%m-%d %H:%M:%S"


def _run(sql: str, params: tuple = (), fetch: bool = False):
    # Har call ka apna chhota connection, taaki reminder thread se bhi safe rahe
    with closing(sqlite3.connect(DB_PATH, timeout=10)) as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows


def init_activity() -> None:
    _run(
        "CREATE TABLE IF NOT EXISTS reminders ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, "
        "due_at TEXT NOT NULL, done INTEGER DEFAULT 0)"
    )
    _run(
        "CREATE TABLE IF NOT EXISTS tool_log ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, tool TEXT NOT NULL, "
        "args TEXT, result TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP)"
    )


# ------------------------------------------------------------ tool log
def log_tool(tool: str, args: dict, result: str) -> None:
    _run(
        "INSERT INTO tool_log (tool, args, result) VALUES (?, ?, ?)",
        (tool, str(args)[:500], str(result)[:500]),
    )


def get_recent_log(n: int = 10) -> list:
    rows = _run(
        "SELECT ts, tool, args, result FROM tool_log ORDER BY id DESC LIMIT ?",
        (n,),
        fetch=True,
    )
    return list(reversed(rows))


# ------------------------------------------------------------ reminders
def add_reminder(text: str, minutes: float) -> str:
    due = (datetime.now() + timedelta(minutes=minutes)).strftime(FMT)
    _run("INSERT INTO reminders (text, due_at) VALUES (?, ?)", (text, due))
    return due


def list_pending() -> list:
    return _run(
        "SELECT text, due_at FROM reminders WHERE done = 0 ORDER BY due_at",
        fetch=True,
    )


def pop_due() -> list:
    """Jin reminders ka time ho gaya unke texts return karta hai aur unhe done mark karta hai."""
    now = datetime.now().strftime(FMT)
    rows = _run(
        "SELECT id, text FROM reminders WHERE done = 0 AND due_at <= ?", (now,), fetch=True
    )
    for rid, _ in rows:
        _run("UPDATE reminders SET done = 1 WHERE id = ?", (rid,))
    return [text for _, text in rows]