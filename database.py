import sqlite3
import random
import string
from datetime import datetime

DB_PATH = "shortener.db"
CHARS = string.ascii_letters + string.digits
CODE_LENGTH = 6


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the links table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            code        TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            clicks      INTEGER DEFAULT 0,
            created_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")


def generate_code():
    """Generate a unique 6-character alphanumeric code."""
    while True:
        code = "".join(random.choices(CHARS, k=CODE_LENGTH))
        conn = get_connection()
        row = conn.execute("SELECT code FROM links WHERE code = ?", (code,)).fetchone()
        conn.close()
        if not row:
            return code


def add_link(original_url: str, custom_alias: str = None) -> str:
    """Insert a new link and return the assigned code."""
    code = custom_alias if custom_alias else generate_code()
    created_at = datetime.utcnow().isoformat()

    conn = get_connection()
    conn.execute(
        "INSERT INTO links (code, original_url, clicks, created_at) VALUES (?, ?, 0, ?)",
        (code, original_url, created_at),
    )
    conn.commit()
    conn.close()
    return code


def get_link(code: str) -> dict | None:
    """Fetch a link record by its short code."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_links() -> list[dict]:
    """Return all links ordered by creation date descending."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM links ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def increment_clicks(code: str):
    """Increment the click counter for a given code."""
    conn = get_connection()
    conn.execute("UPDATE links SET clicks = clicks + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()


def delete_link(code: str) -> bool:
    """Delete a link by code. Returns True if a row was deleted."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM links WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0