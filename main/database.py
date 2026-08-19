"""
Capa de base de datos (SQLite) de SignScan — database.py

Se encarga de la tabla `users`: alta de cuentas, autenticación y
actualización del perfil. Las contraseñas NUNCA se guardan en texto
plano: se cifran con PBKDF2-HMAC-SHA256 usando una sal aleatoria
distinta para cada usuario, así que dos personas con la misma clave
producen hashes diferentes.

Ubicación: la raíz del módulo de la app (junto a main.py,
hand_detector.py, etc.). El archivo .db se crea solo la primera vez que
se ejecuta init_db(), que main.py llama al arrancar.

Convención de esta capa: las funciones que pueden fallar por culpa del
usuario (email repetido, contraseña corta, credenciales incorrectas) no
lanzan excepciones; devuelven la tupla (ok, mensaje, usuario) para que
la pantalla muestre ese mensaje tal cual.

Esquema de la tabla `users`:
    id             INTEGER  clave primaria autoincremental
    name           TEXT     nombre visible
    email          TEXT     único, siempre en minúsculas
    password_hash  TEXT     hash PBKDF2 en hexadecimal
    salt           TEXT     sal aleatoria en hexadecimal
    avatar         TEXT     emoji del perfil (por defecto una estrella)
    created_at     TEXT     fecha de alta en formato ISO
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
# Conexión y esquema
# ------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Abre una conexión nueva a signscan.db y la devuelve.

    Cada llamada crea su propia conexión (y quien la usa debe cerrarla,
    normalmente en un bloque finally). Es lo más sencillo y seguro aquí:
    SQLite no permite compartir una conexión entre hilos, y el traductor
    corre en un hilo aparte.

    Detalles de la configuración:
        - row_factory = sqlite3.Row para poder leer las columnas por
          nombre (row["email"]) y convertirlas a dict fácilmente.
        - PRAGMA foreign_keys = ON porque SQLite las desactiva por
          defecto; así las tablas que se añadan en el futuro sí
          respetarán sus relaciones.

    Returns:
        Conexión abierta a la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea la tabla `users` si todavía no existe.

    Se llama una sola vez al arrancar la app (main.main). Es idempotente
    gracias a CREATE TABLE IF NOT EXISTS: ejecutarla mil veces no borra
    ni modifica nada, así que es seguro llamarla en cada arranque.

    Aviso: no hace migraciones. Si en el futuro se añade una columna
    (por ejemplo `photo` para la foto de perfil), hay que añadir aquí el
    ALTER TABLE correspondiente; a las bases de datos ya creadas no les
    aparecerá sola.
    """
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
# Cifrado de contraseñas
# ------------------------------------------------------------------

def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Calcula el hash PBKDF2-HMAC-SHA256 de una contraseña.

    Args:
        password: contraseña en texto plano, tal cual la escribió el
            usuario.
        salt: sal a reutilizar. Se pasa cuando se está VERIFICANDO una
            contraseña (hay que usar la misma sal con la que se guardó).
            Si es None se genera una sal aleatoria nueva de 16 bytes,
            que es lo que toca al CREAR una cuenta.

    Returns:
        Tupla (hash_hex, sal_hex), ambos en hexadecimal para poder
        guardarlos como texto en SQLite.

    Las 100.000 iteraciones (PBKDF2_ITERATIONS) están para que probar
    contraseñas por fuerza bruta sea lento a propósito.
    """
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return binascii.hexlify(pwd_hash).decode(), binascii.hexlify(salt).decode()


def _verify_password(password: str, stored_hash_hex: str, stored_salt_hex: str) -> bool:
    """Comprueba si una contraseña coincide con el hash guardado.

    Vuelve a cifrar lo que escribió el usuario con la MISMA sal que se
    guardó en su fila y compara los dos hashes. Nunca se descifra nada:
    PBKDF2 solo va en una dirección.

    Args:
        password: contraseña que acaba de escribir el usuario.
        stored_hash_hex: columna `password_hash` de la tabla.
        stored_salt_hex: columna `salt` de la tabla.

    Returns:
        True si la contraseña es correcta.
    """
    salt = binascii.unhexlify(stored_salt_hex)
    new_hash, _ = _hash_password(password, salt)
    return new_hash == stored_hash_hex


# ------------------------------------------------------------------
# Consultas
# ------------------------------------------------------------------

def get_user_by_email(email: str) -> dict | None:
    """Busca un usuario por su correo.

    Normaliza el email (quita espacios y lo pasa a minúsculas) antes de
    consultar, porque así es como se guarda en create_user; si no,
    "Ariel@X.com" y "ariel@x.com" parecerían cuentas distintas.

    Args:
        email: correo a buscar, en cualquier combinación de mayúsculas.

    Returns:
        La fila como diccionario, o None si no existe esa cuenta.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    """Busca un usuario por su clave primaria.

    Se usa sobre todo justo después de un INSERT, para devolver la fila
    completa (con created_at y avatar ya rellenos por la base de datos).

    Args:
        user_id: valor de la columna `id`.

    Returns:
        La fila como diccionario, o None si ese id no existe.
    """
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def email_exists(email: str) -> bool:
    """Indica si ya hay una cuenta registrada con ese correo.

    Es un atajo sobre get_user_by_email() para que create_user pueda dar
    un mensaje claro antes de intentar el INSERT.

    Args:
        email: correo a comprobar.

    Returns:
        True si el correo ya está en uso.
    """
    return get_user_by_email(email) is not None


# ------------------------------------------------------------------
# Alta de cuenta e inicio de sesión
# ------------------------------------------------------------------

def create_user(name: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    """Crea una cuenta nueva y devuelve el usuario ya guardado.

    Valida en este orden (y se detiene en el primer fallo, para que el
    mensaje que ve el usuario sea el del primer problema real):
        1. que el nombre no esté vacío,
        2. que el email tenga forma de email (EMAIL_RE),
        3. que la contraseña tenga 8 caracteres o más,
        4. que el email no esté ya registrado.

    Solo si todo pasa se cifra la contraseña y se inserta la fila. El
    email se guarda siempre en minúsculas y sin espacios.

    Args:
        name: nombre visible del usuario.
        email: correo, se normaliza a minúsculas.
        password: contraseña en texto plano (nunca se guarda así).

    Returns:
        Tupla (ok, mensaje, usuario):
            ok      -> True si se creó la cuenta.
            mensaje -> texto listo para mostrar en pantalla, tanto si
                       salió bien como si falló la validación.
            usuario -> la fila recién creada como dict, o None si falló.

    Nota: el IntegrityError se captura igualmente por si dos altas con el
    mismo correo ocurren a la vez y la comprobación previa se queda
    corta; la restricción UNIQUE de la tabla es la garantía final.
    """
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
    """Comprueba unas credenciales de inicio de sesión.

    Args:
        email: correo escrito en la pantalla de login.
        password: contraseña escrita en la pantalla de login.

    Returns:
        Tupla (ok, mensaje, usuario), igual que create_user(). Si las
        credenciales son correctas, `usuario` es la fila completa, que
        sign_in.py pasa directamente a session.set_current_user().

    Nota de seguridad: los mensajes distinguen entre "no existe esa
    cuenta" y "contraseña incorrecta", que es más cómodo de usar pero
    también le confirma a un atacante qué correos están registrados. Si
    algún día importa, ambos casos deberían devolver el mismo texto.
    """
    email = (email or "").strip().lower()

    if not email or not password:
        return False, "Enter your email and password", None

    user = get_user_by_email(email)
    if user is None:
        return False, "No account found with that email", None
    if not _verify_password(password, user["password_hash"], user["salt"]):
        return False, "Incorrect password", None

    return True, "Welcome back", user


def update_profile(user_id: int, name: str | None = None, avatar: str | None = None):
    """Actualiza el nombre y/o el avatar de un usuario ya existente.

    Los dos parámetros son opcionales: se actualiza solo lo que se pase
    distinto de None, así que se puede cambiar únicamente el avatar sin
    tocar el nombre.

    Args:
        user_id: id del usuario a modificar.
        name: nombre nuevo, o None para dejarlo como está.
        avatar: emoji nuevo, o None para dejarlo como está.

    Ojo: no acepta `photo`. La pantalla de perfil intenta llamarla con
    ese argumento y captura el TypeError para reintentar sin él, así que
    hoy la foto de perfil NO se guarda en la base de datos: solo vive en
    la sesión hasta que se cierra la app.
    """
    conn = get_connection()
    try:
        if name is not None:
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name.strip(), user_id))
        if avatar is not None:
            conn.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
        conn.commit()
    finally:
        conn.close()