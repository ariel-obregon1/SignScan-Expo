"""
Sesión en memoria del usuario que tiene la app abierta — session.py

A propósito es simple: un diccionario a nivel de módulo que las
pantallas leen y escriben para saber quién está usando la app en este
momento. Se borra cada vez que se cierra la aplicación; NO persiste
entre ejecuciones — para eso está la tabla `users` (ver database.py).

Cómo se usa desde las pantallas:

    import session
    session.set_current_user(user)          # tras login o alta correcta
    session.current_user["name"]            # leer datos
    session.get_avatar_control(size=16)     # pintar el avatar
    session.clear_current_user()            # al cerrar sesión

Ojo: al ser un diccionario global, cualquier pantalla puede escribirlo.
Si algún día la app maneja varias sesiones a la vez (por ejemplo en modo
web con varios usuarios conectados), esto habría que moverlo a
page.session, que Flet mantiene separado por cliente.
"""

import flet as ft

# Datos del usuario activo. Las claves siempre existen (aunque valgan
# None) para que las pantallas puedan hacer .get() sin comprobaciones:
#   id     -> clave primaria en la tabla users (None = nadie logueado)
#   name   -> nombre visible
#   email  -> correo con el que inició sesión
#   avatar -> emoji elegido en la pantalla de perfil
#   photo  -> ruta de la foto de perfil relativa a assets/, o None
current_user = {
    "id": None,
    "name": None,
    "email": None,
    "avatar": "🌟",
    "photo": None,
}


def set_current_user(user: dict):
    """Marca a un usuario como el activo de la sesión.

    Se llama justo después de un alta correcta (sign_up.py) o de un
    login correcto (sign_in.py), pasándole el diccionario que devuelven
    database.create_user() / database.authenticate_user().

    Args:
        user: fila de la tabla `users` como diccionario. Debe traer al
            menos "id", "name" y "email"; "avatar" y "photo" son
            opcionales.
    """
    current_user["id"] = user["id"]
    current_user["name"] = user["name"]
    current_user["email"] = user["email"]
    current_user["avatar"] = user.get("avatar") or "🌟"
    current_user["photo"] = user.get("photo")


def clear_current_user():
    """Cierra la sesión: deja el diccionario como al arrancar la app.

    Lo usa el botón "Log out" antes de volver a la pantalla de
    bienvenida. No toca la base de datos: la cuenta sigue existiendo,
    solo se olvida quién estaba dentro.
    """
    current_user["id"] = None
    current_user["name"] = None
    current_user["email"] = None
    current_user["avatar"] = "🌟"
    current_user["photo"] = None


def is_logged_in() -> bool:
    """Indica si hay alguien con la sesión iniciada.

    Returns:
        True si se llamó a set_current_user() y todavía no se limpió la
        sesión. Se apoya en el "id" porque es el único dato que solo
        puede venir de la base de datos.
    """
    return current_user["id"] is not None


def get_avatar_control(size: int = 16, container_size: int | None = None) -> ft.Control:
    """Devuelve el control que representa el avatar del usuario.

    Es la ÚNICA fuente de verdad de "qué cara tiene el usuario ahora
    mismo": si eligió una foto devuelve un ft.Image con ella, y si no,
    un ft.Text con su emoji.

    Todas las pantallas deben llamar a esta función en vez de construir
    a mano `ft.Text(session.current_user["avatar"], ...)`. Así, cuando
    alguien se pone una foto en el perfil, aparece en toda la app sin
    tener que acordarse de tocar cada pantalla una por una.

    Args:
        size: tamaño del emoji, o de la foto si no se pasa
            container_size.
        container_size: tamaño de la foto en píxeles. Se usa cuando el
            emoji debe ser más pequeño que el círculo que lo contiene.

    Returns:
        Un ft.Image (foto) o un ft.Text (emoji).

    Importante: hay que meter el resultado en un Container con
    border_radius=999 y clip_behavior=ft.ClipBehavior.ANTI_ALIAS para
    que salga redondo. Sin el recorte, la foto se ve cuadrada y tapa el
    contenedor.
    """
    photo = current_user.get("photo")
    if photo:
        dim = container_size or size
        return ft.Image(src=photo, width=dim, height=dim, fit=ft.BoxFit.COVER)
    return ft.Text(current_user.get("avatar") or "🌟", size=size)