# componentes/base_datos.py

import sqlite3
from datetime import datetime


def conectar():
    return sqlite3.connect("signscan.db", timeout=15)


def crear_base_datos():
    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                correo TEXT UNIQUE,
                password TEXT,
                avatar TEXT DEFAULT '👨',
                foto TEXT DEFAULT '',
                fecha_creacion TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progreso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correo TEXT,
                leccion_id TEXT,
                completado INTEGER DEFAULT 0,
                puntos INTEGER DEFAULT 0,
                fecha TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correo TEXT,
                tipo TEXT,
                descripcion TEXT,
                fecha TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comunidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                avatar TEXT,
                contenido TEXT,
                fecha TEXT,
                likes INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion (
                correo TEXT PRIMARY KEY,
                tema TEXT DEFAULT 'Claro',
                color_acento TEXT DEFAULT '#46D7CF',
                idioma TEXT DEFAULT 'Español (Panamá)',
                tamano_fuente TEXT DEFAULT 'Medio',
                racha TEXT DEFAULT '🔥 Fuego Clásico',
                notificaciones INTEGER DEFAULT 1,
                perfil_publico INTEGER DEFAULT 1,
                mensajes INTEGER DEFAULT 1,
                camara INTEGER DEFAULT 1,
                ubicacion INTEGER DEFAULT 0
            )
        """)

        conexion.commit()


def registrar_usuario(nombre, correo, password):
    try:
        correo = correo.strip().lower()

        with conectar() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """
                INSERT INTO usuarios(nombre, correo, password, avatar, foto, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nombre.strip(), correo, password, "👨", "", datetime.now().strftime("%d/%m/%Y"))
            )
            conexion.commit()

        asegurar_configuracion(correo)
        return True, "Cuenta creada correctamente."

    except sqlite3.IntegrityError:
        return False, "Ese correo ya existe."


def iniciar_sesion(correo, password):
    correo = correo.strip().lower()

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT nombre, correo, avatar, foto
            FROM usuarios
            WHERE correo=? AND password=?
            """,
            (correo, password)
        )
        resultado = cursor.fetchone()

    if resultado:
        asegurar_configuracion(resultado[1])
        return {
            "nombre": resultado[0],
            "correo": resultado[1],
            "avatar": resultado[2] or "👨",
            "foto": resultado[3] or "",
        }

    return None


def actualizar_usuario(correo, nombre=None, avatar=None, foto=None):
    if not correo:
        return

    with conectar() as conexion:
        cursor = conexion.cursor()

        if nombre is not None:
            cursor.execute("UPDATE usuarios SET nombre=? WHERE correo=?", (nombre, correo))

        if avatar is not None:
            cursor.execute("UPDATE usuarios SET avatar=? WHERE correo=?", (avatar, correo))

        if foto is not None:
            cursor.execute("UPDATE usuarios SET foto=? WHERE correo=?", (foto, correo))

        conexion.commit()


def asegurar_configuracion(correo):
    if not correo:
        return

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO configuracion(correo) VALUES (?)",
            (correo,)
        )
        conexion.commit()


def obtener_configuracion(correo):
    if not correo:
        return {
            "tema": "Claro",
            "color_acento": "#46D7CF",
            "idioma": "Español (Panamá)",
            "tamano_fuente": "Medio",
            "racha": "🔥 Fuego Clásico",
            "notificaciones": 1,
            "perfil_publico": 1,
            "mensajes": 1,
            "camara": 1,
            "ubicacion": 0,
        }

    asegurar_configuracion(correo)

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT tema, color_acento, idioma, tamano_fuente, racha,
                   notificaciones, perfil_publico, mensajes, camara, ubicacion
            FROM configuracion
            WHERE correo=?
            """,
            (correo,)
        )
        datos = cursor.fetchone()

    return {
        "tema": datos[0],
        "color_acento": datos[1],
        "idioma": datos[2],
        "tamano_fuente": datos[3],
        "racha": datos[4],
        "notificaciones": datos[5],
        "perfil_publico": datos[6],
        "mensajes": datos[7],
        "camara": datos[8],
        "ubicacion": datos[9],
    }


def actualizar_configuracion(correo, campo, valor):
    permitidos = [
        "tema", "color_acento", "idioma", "tamano_fuente", "racha",
        "notificaciones", "perfil_publico", "mensajes", "camara", "ubicacion"
    ]

    if campo not in permitidos or not correo:
        return

    asegurar_configuracion(correo)

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            f"UPDATE configuracion SET {campo}=? WHERE correo=?",
            (valor, correo)
        )
        conexion.commit()


def guardar_historial(correo, tipo, descripcion):
    if not correo:
        return

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO historial(correo, tipo, descripcion, fecha)
            VALUES (?, ?, ?, ?)
            """,
            (correo, tipo, descripcion, datetime.now().strftime("%d/%m/%Y %I:%M %p"))
        )
        conexion.commit()


def obtener_historial(correo):
    if not correo:
        return []

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT tipo, descripcion, fecha
            FROM historial
            WHERE correo=?
            ORDER BY id DESC
            """,
            (correo,)
        )
        return cursor.fetchall()


def completar_leccion(correo, leccion_id, puntos):
    if not correo:
        return

    with conectar() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM progreso WHERE correo=? AND leccion_id=?",
            (correo, leccion_id)
        )

        existe = cursor.fetchone()

        if existe:
            cursor.execute(
                """
                UPDATE progreso
                SET completado=1, puntos=?, fecha=?
                WHERE correo=? AND leccion_id=?
                """,
                (puntos, datetime.now().strftime("%d/%m/%Y"), correo, leccion_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO progreso(correo, leccion_id, completado, puntos, fecha)
                VALUES (?, ?, ?, ?, ?)
                """,
                (correo, leccion_id, 1, puntos, datetime.now().strftime("%d/%m/%Y"))
            )

        conexion.commit()


def obtener_progreso(correo):
    if not correo:
        return {}, 0

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT leccion_id, puntos
            FROM progreso
            WHERE correo=? AND completado=1
            """,
            (correo,)
        )
        datos = cursor.fetchall()

    completadas = {fila[0]: fila[1] for fila in datos}
    puntos = sum(fila[1] for fila in datos)

    return completadas, puntos


def guardar_post(nombre, avatar, contenido):
    if not contenido:
        return

    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO comunidad(nombre, avatar, contenido, fecha, likes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nombre, avatar, contenido, "Ahora", 0)
        )
        conexion.commit()


def obtener_posts():
    with conectar() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT nombre, avatar, contenido, fecha, likes
            FROM comunidad
            ORDER BY id DESC
            """
        )
        return cursor.fetchall()