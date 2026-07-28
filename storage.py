import logging
import psycopg2
import psycopg2.extras

import config

log = logging.getLogger("storage")


def get_conn():
    return psycopg2.connect(config.DATABASE_URL)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    referrer_id BIGINT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    referral_counted BOOLEAN DEFAULT FALSE,
                    group_link_sent BOOLEAN DEFAULT FALSE,
                    referral_count INTEGER DEFAULT 0,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.commit()
    log.info("Baza (Supabase/PostgreSQL) tayyor")


def add_user_if_not_exists(user_id: int, username: str, full_name: str, referrer_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
            if cur.fetchone():
                return False
            cur.execute(
                "INSERT INTO users (user_id, username, full_name, referrer_id) VALUES (%s, %s, %s, %s)",
                (user_id, username, full_name, referrer_id),
            )
        conn.commit()
        return True


def get_user(user_id: int):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
            return cur.fetchone()


def mark_verified(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET is_verified=TRUE WHERE user_id=%s", (user_id,))
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
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("UPDATE users SET referral_counted=TRUE WHERE user_id=%s", (user_id,))
            cur.execute(
                "UPDATE users SET referral_count = referral_count + 1 WHERE user_id=%s",
                (referrer_id,),
            )
            cur.execute(
                "SELECT referral_count FROM users WHERE user_id=%s", (referrer_id,)
            )
            row = cur.fetchone()
            new_count = row["referral_count"] if row else None
        conn.commit()
        return referrer_id, new_count


def mark_group_link_sent(user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET group_link_sent=TRUE WHERE user_id=%s", (user_id,))
        conn.commit()


def total_users() -> int:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as c FROM users")
            row = cur.fetchone()
            return row["c"] if row else 0
