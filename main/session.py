"""
Sesión en memoria del usuario logueado.

Muy simple a propósito: un diccionario a nivel de módulo que las
pantallas leen/escriben para saber quién está usando la app en este
momento. Se resetea cada vez que se cierra la app (no persiste entre
ejecuciones — para eso está la tabla `users` en la base de datos).
"""

current_user = {
    "id": None,
    "name": None,
    "email": None,
    "avatar": "🌟",
}


def set_current_user(user: dict):
    current_user["id"] = user["id"]
    current_user["name"] = user["name"]
    current_user["email"] = user["email"]
    current_user["avatar"] = user.get("avatar") or "🌟"


def clear_current_user():
    current_user["id"] = None
    current_user["name"] = None
    current_user["email"] = None
    current_user["avatar"] = "🌟"


def is_logged_in() -> bool:
    return current_user["id"] is not None