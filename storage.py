import sqlite3
import threading
from config import DB_PATH

_lock = threading.Lock()


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock, get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                referrer_id INTEGER,
                is_verified INTEGER DEFAULT 0,
                referral_counted INTEGER DEFAULT 0,
                group_link_sent INTEGER DEFAULT 0,
                referral_count INTEGER DEFAULT 0,
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def add_user_if_not_exists(user_id: int, username: str, full_name: str, referrer_id: int | None):
    with _lock, get_conn() as conn:
        row = conn.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row:
            return False
        conn.execute(
            "INSERT INTO users (user_id, username, full_name, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, referrer_id),
        )
        conn.commit()
        return True


def get_user(user_id: int):
    with _lock, get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()


def mark_verified(user_id: int):
    with _lock, get_conn() as conn:
        conn.execute("UPDATE users SET is_verified=1 WHERE user_id=?", (user_id,))
        conn.commit()


def is_verified(user_id: int) -> bool:
    user = get_user(user_id)
    return bool(user and user["is_verified"])


def count_referral_once(user_id: int):
    """
    Foydalanuvchi tasdiqlangandan so'ng, agar uning referrer'i bo'lsa va
    hali hisoblanmagan bo'lsa - referrer hisobini +1 oshiradi.
    Qaytaradi: (referrer_id yoki None, referrer yangi jami soni)
    """
    user = get_user(user_id)
    if not user or not user["referrer_id"] or user["referral_counted"]:
        return None, None

    referrer_id = user["referrer_id"]
    with _lock, get_conn() as conn:
        conn.execute("UPDATE users SET referral_counted=1 WHERE user_id=?", (user_id,))
        conn.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id=?",
            (referrer_id,),
        )
        conn.commit()
        row = conn.execute(
            "SELECT referral_count FROM users WHERE user_id=?", (referrer_id,)
        ).fetchone()
        new_count = row["referral_count"] if row else None
        return referrer_id, new_count


def mark_group_link_sent(user_id: int):
    with _lock, get_conn() as conn:
        conn.execute("UPDATE users SET group_link_sent=1 WHERE user_id=?", (user_id,))
        conn.commit()


def total_users() -> int:
    with _lock, get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
        return row["c"] if row else 0
