import sqlite3

DB_NAME = "users.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone_number TEXT
            )
        """)

def save_phone_number(user_id, phone):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR REPLACE INTO users (user_id, phone_number) VALUES (?, ?)", (user_id, phone))

def get_phone_number(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("SELECT phone_number FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else None

init_db()
