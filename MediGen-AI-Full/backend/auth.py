"""
Simple authentication layer for the academic project.

Login/signup use an email address (Gmail) + password instead of a
separate username. Every account also has a role -- "user" or
"admin" -- chosen at signup, so both types of accounts can log in
with the same simple form.

Stores users in the same SQLite database as diagnosis history.
Passwords are hashed with SHA-256 + a per-user random salt (no
external dependency needed). A random token is issued on login and
stored server-side so the frontend can just send it back on each
request -- this is intentionally simple (no JWT/OAuth) since the goal
is a working login system for a major/minor project, not a
production-grade auth service.
"""
import sqlite3
import os
import re
import hashlib
import secrets
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "history.db")

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
DEFAULT_ADMIN_EMAIL = "admin@medigen.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"
VALID_ROLES = ("user", "admin")


def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT
        )
        """
    )
    cur.execute("SELECT id FROM users WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
    if not cur.fetchone():
        salt = secrets.token_hex(8)
        cur.execute(
            "INSERT INTO users (email, password_hash, salt, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
            (DEFAULT_ADMIN_EMAIL, _hash_password(DEFAULT_ADMIN_PASSWORD, salt), salt, datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def register_user(email: str, password: str, role: str = "user") -> tuple[bool, str]:
    email = email.strip().lower()
    role = role.strip().lower() if role else "user"

    if not EMAIL_PATTERN.match(email):
        return False, "Please enter a valid email address (e.g. you@example.com)."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if role not in VALID_ROLES:
        return False, "Role must be either 'user' or 'admin'."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False, "An account with this email address already exists."

    salt = secrets.token_hex(8)
    password_hash = _hash_password(password, salt)
    cur.execute(
        "INSERT INTO users (email, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
        (email, password_hash, salt, role, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return True, "Account created successfully."


def verify_login(email: str, password: str) -> tuple[bool, str]:
    """Returns (True, token) on success, or (False, error_message) on failure."""
    email = email.strip().lower()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False, "No account found with that email address."

    computed_hash = _hash_password(password, row["salt"])
    if computed_hash != row["password_hash"]:
        conn.close()
        return False, "Incorrect password."

    token = secrets.token_hex(24)
    cur.execute(
        "INSERT INTO sessions (token, email, role, created_at) VALUES (?, ?, ?, ?)",
        (token, row["email"], row["role"], datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return True, token


def get_session(token: str):
    """Returns {'email': ..., 'role': ...} for a valid token, else None."""
    if not token:
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT email, role FROM sessions WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return {"email": row["email"], "role": row["role"]} if row else None


def get_user_from_token(token: str):
    """Backwards-compatible helper: returns just the email string, or None."""
    session = get_session(token)
    return session["email"] if session else None


def logout(token: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def list_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT email, role, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(email: str) -> bool:
    email = email.strip().lower()
    if email == DEFAULT_ADMIN_EMAIL:
        return False
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE email = ?", (email,))
    cur.execute("DELETE FROM users WHERE email = ?", (email,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
