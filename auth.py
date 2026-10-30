import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

ITERATIONS = 100_000
MIN_PASSWORD_LENGTH = 8
MAX_ATTEMPTS = 5


def create_user_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY,
            username      TEXT NOT NULL UNIQUE,
            password_hash BLOB NOT NULL,
            salt          BLOB NOT NULL,
            created_at    TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_courses (
            id             INTEGER PRIMARY KEY,
            user_id        INTEGER NOT NULL,
            destination    TEXT NOT NULL,
            total_budget   REAL NOT NULL,
            restaurant_ids TEXT NOT NULL,
            saved_at       TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)


def register(conn: sqlite3.Connection, username: str, password: str,
             confirm: str) -> tuple[bool, str]:
    """Create an account. Returns (success, message)."""
    username = username.strip()

    if not username:
        return False, "Username cannot be empty."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return False, "Passwords do not match."

    existing = conn.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        return False, "That username is already taken."

    salt = os.urandom(16)
    conn.execute(
        "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
        (username, _derive(password, salt), salt, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    return True, "Account created."


def authenticate(conn: sqlite3.Connection, username: str,
                 password: str) -> tuple[bool, str, int | None]:
    """
    Check a username and password. Returns (success, message, user_id).

    The same message is returned whether the username is unknown or the
    password is wrong, so the interface cannot be used to discover which
    usernames exist.
    """
    generic = "Username or password is incorrect."

    row = conn.execute(
        "SELECT id, password_hash, salt FROM users WHERE username = ?",
        (username.strip(),),
    ).fetchone()

    if row is None:
        # Derive anyway against a throwaway salt so a missing username does
        # not return measurably faster than a wrong password.
        _derive(password, os.urandom(16))
        return False, generic, None

    candidate = _derive(password, row["salt"])
    if hmac.compare_digest(candidate, row["password_hash"]):
        return True, "", row["id"]
    return False, generic, None
