import sqlite3
from config import DB_PATH, HISTORY_LOAD, MAX_STORED_MESSAGES
conn = sqlite3.connect(DB_PATH)

BLOCKED_WORDS = ['password', 'passcode', 'otp', 'pin', 'cvv', 'card number', 'atm pin', 'upi', 'pin']

def init_db() -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id Integer PRIMARY KEY AUTOINCREMENT,role TEXT NOT NULL, "
        "content TEXT NOT NULL, ts TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute(
            "CREATE TABLE IF NOT EXISTS Facts ("
            "id Integer PRIMARY KEY AUTOINCREMENT,fact TEXT NOT NULL UNIQUE, "
            "ts TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
    conn.commit()

def save_message(role: str, content: str) -> None:
    conn.execute("INSERT INTO messages(role, content) VALUES(?, ?)", (role, content)) 
    conn.execute(
        "DELETE FROM messages WHERE id NOT IN"
        "(SELECT id FROM messages ORDER BY id DESC LIMIT ?)",
        (MAX_STORED_MESSAGES,),
    )   
    conn.commit()

def load_history(n: int = HISTORY_LOAD) -> list:
    rows = conn.execute(
        "SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    history = [{"role": role, "content": content} for role, content in reversed(rows)]
    while history and history[0]["role"] != "user":
        history.pop(0)
    return history

def get_facts() -> list:
    rows = conn.execute('SELECT fact FROM facts ORDER BY id').fetchall()
    return [row[0] for row in rows]

def add_fact(fact: str) -> str:
    fact = fact.strip()
    if not fact:
        return "Empty fact, nothing saved."
    if any(word in fact.lower() for word in BlOCKED_WORDS):
        return "Refused: password/OTP/PIN/card jaisi sensitive cheezein store nahi hoti."
    conn.execute("INSERT OR IGNORE INTO facts (fact) VALUES (?)", (fact,))
    conn.commit()
    return f"Remembered: {fact}"

def delete_fact(keyword: str) -> str:
    keyword = keyword.strip()
    if not keyword:
        return "No keyword again"
    cur = conn.execute("DELETE FROM facts WHERE fact LIKE ?", (f"%{keyword}%",))
    conn.commit()
    return f"FORGOT {curr.rowcount} fact(s) matching '{keyword}'."
                                                              
                                                        
