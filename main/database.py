"""
Database layer (SQLite) for SignScan.

Handles the users table: account creation, authentication, and
profile updates. Passwords are never stored in plain text — they are
hashed with PBKDF2-HMAC-SHA256 plus a random per-user salt.

Location: project root (next to main.py, hand_detector.py, etc.)
The .db file is created automatically the first time init_db() runs.
"""

import binascii
import datetime
import hashlib
import os
import re
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "signscan.db")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PBKDF2_ITERATIONS = 100_000


# ------------------------------------------------------------------
# Connection / schema
# ------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _add_missing_columns(conn: sqlite3.Connection):
    """Migration step: CREATE TABLE IF NOT EXISTS only creates the
    table the first time it's ever run - it does nothing to a table
    that already exists with an older schema. So a users table created
    before the `photo` column was added stays without it forever,
    unless we explicitly ALTER it in here. Safe to call on every
    startup: it only adds columns that are actually missing."""
    existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}

    if "photo" not in existing_columns:
        conn.execute("ALTER TABLE users ADD COLUMN photo TEXT")


def init_db():
    """Creates the users table if it doesn't exist yet, and migrates
    it if it exists but is missing newer columns. Call once on app
    startup (from main.py)."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                avatar TEXT NOT NULL DEFAULT '🌟',
                photo TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        _add_missing_columns(conn)
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------

def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return binascii.hexlify(pwd_hash).decode(), binascii.hexlify(salt).decode()


def _verify_password(password: str, stored_hash_hex: str, stored_salt_hex: str) -> bool:
    salt = binascii.unhexlify(stored_salt_hex)
    new_hash, _ = _hash_password(password, salt)
    return new_hash == stored_hash_hex


# ------------------------------------------------------------------
# Queries
# ------------------------------------------------------------------

def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


# ------------------------------------------------------------------
# Sign up / sign in
# ------------------------------------------------------------------

def create_user(name: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    """Creates a new account. Returns (ok, message, user|None)."""
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name:
        return False, "Please enter your full name", None
    if not EMAIL_RE.match(email):
        return False, "Invalid email address", None
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long", None
    if email_exists(email):
        return False, "An account with that email already exists", None

    pwd_hash, salt = _hash_password(password)
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, pwd_hash, salt, datetime.datetime.utcnow().isoformat()),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists", None
    finally:
        conn.close()

    return True, "Account created successfully", get_user_by_id(user_id)


def authenticate_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    """Verifies credentials. Returns (ok, message, user|None)."""
    email = (email or "").strip().lower()

    if not email or not password:
        return False, "Enter your email and password", None

    user = get_user_by_email(email)
    if user is None:
        return False, "No account found with that email", None
    if not _verify_password(password, user["password_hash"], user["salt"]):
        return False, "Incorrect password", None

    return True, "Welcome back", user


def update_profile(user_id: int, name: str | None = None, avatar: str | None = None, photo: str | None = None,):
    conn = get_connection()
    try:
        if name is not None:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
        if avatar is not None:
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
        if photo is not None:
            conn.execute(
                "UPDATE users SET photo=? WHERE id=?",
                (photo, user_id)
            )
        conn.commit()
    finally:
        conn.close()