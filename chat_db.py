# chat_db.py – Persistent chat history using SQLite
import sqlite3
import os
from datetime import datetime
from typing import List, Dict

DB_PATH = "chat_history.db"

def init_db():
    """Create table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            module TEXT,
            question TEXT,
            answer TEXT,
            language TEXT,
            sources TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_chat(module: str, question: str, answer: str, language: str = "English", sources: str = ""):
    """Insert a chat record."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO chat_history (timestamp, module, question, answer, language, sources)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), module, question, answer, language, sources))
    conn.commit()
    conn.close()

def get_all_chats(limit: int = 100) -> List[Dict]:
    """Retrieve recent chats."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, module, question, answer, language, sources FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{
        "timestamp": row[0],
        "module": row[1],
        "question": row[2],
        "answer": row[3],
        "language": row[4],
        "sources": row[5]
    } for row in rows]

def clear_all_chats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()