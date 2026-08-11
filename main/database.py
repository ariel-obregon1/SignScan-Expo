"""
Capa de base de datos (SQLite) para SignScan.

Maneja la tabla de usuarios: creación de cuenta, autenticación y
actualización de perfil. Las contraseñas nunca se guardan en texto
plano — se hashean con PBKDF2-HMAC-SHA256 + salt aleatorio por
usuario.

Ubicación: raíz del proyecto (junto a main.py, hand_detector.py, etc.)
El archivo .db se crea automáticamente la primera vez que se llama a
init_db().
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
# Conexión / esquema
# ------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea la tabla de usuarios si no existe. Llamar una vez al
    arrancar la app (desde main.py)."""
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
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Hashing de contraseñas
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
# Consultas
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
# Registro / autenticación
# ------------------------------------------------------------------

def create_user(name: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    """Crea una cuenta nueva. Devuelve (ok, mensaje, usuario|None)."""
    name = (name or "").strip()
    email = (email or "").strip().lower()

    if not name:
        return False, "Ingresa tu nombre completo", None
    if not EMAIL_RE.match(email):
        return False, "Correo electrónico inválido", None
    if not password or len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres", None
    if email_exists(email):
        return False, "Ya existe una cuenta con ese correo", None

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
        return False, "Ya existe una cuenta con ese correo", None
    finally:
        conn.close()

    return True, "Cuenta creada correctamente", get_user_by_id(user_id)


def authenticate_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    """Verifica credenciales. Devuelve (ok, mensaje, usuario|None)."""
    email = (email or "").strip().lower()

    if not email or not password:
        return False, "Ingresa tu correo y contraseña", None

    user = get_user_by_email(email)
    if user is None:
        return False, "No existe una cuenta con ese correo", None
    if not _verify_password(password, user["password_hash"], user["salt"]):
        return False, "Contraseña incorrecta", None

    return True, "Bienvenido de nuevo", user


def update_profile(user_id: int, name: str | None = None, avatar: str | None = None):
    conn = get_connection()
    try:
        if name is not None:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
        if avatar is not None:
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
        conn.commit()
    finally:
        conn.close()