"""
Sesión en memoria del usuario que tiene la app abierta (session.py).

A propósito es simple: un diccionario a nivel de módulo que las
pantallas leen y escriben para saber quién está usando la app en este
momento. Se borra cada vez que se cierra la aplicación; NO persiste
entre ejecuciones — para eso está la tabla `users` de la base de datos
(ver database.py).

Cómo se usa desde las pantallas:

    import session
    session.set_current_user(user)      # tras login o alta correcta
    session.current_user["name"]        # leer datos en el dashboard
    session.clear_current_user()        # al cerrar sesión

Ojo: al ser un diccionario global, cualquier pantalla puede escribirlo.
Si algún día la app maneja varias sesiones a la vez (por ejemplo en modo
web con varios usuarios conectados), esto habría que moverlo a
page.session, que Flet mantiene separado por cliente.
"""

# Datos del usuario activo. Las claves siempre existen (aunque valgan
# None) para que las pantallas puedan hacer .get() sin comprobaciones:
#   id     -> clave primaria en la tabla users (None = nadie logueado)
#   name   -> nombre visible, se muestra en el dashboard y el perfil
#   email  -> correo con el que inició sesión
#   avatar -> emoji elegido en la pantalla de perfil
current_user = {
    "id": None,
    "name": None,
    "email": None,
    "avatar": "🌟",
}


def set_current_user(user: dict):
    """Marca a un usuario como el activo de la sesión.

    Se llama justo después de un alta correcta (sign_up.py) o de un
    login correcto (sign_in.py), pasándole el diccionario que devuelven
    database.create_user() / database.authenticate_user().

    Args:
        user: fila de la tabla `users` como diccionario. Debe traer al
            menos las claves "id", "name" y "email"; "avatar" es
            opcional y, si viene vacía, se usa el emoji por defecto.
    """
    current_user["id"] = user["id"]
    current_user["name"] = user["name"]
    current_user["email"] = user["email"]
    current_user["avatar"] = user.get("avatar") or "🌟"


def clear_current_user():
    """Cierra la sesión: deja el diccionario como al arrancar la app.

    Lo usa el botón "Log out" del dashboard antes de volver a la
    pantalla de bienvenida. No toca la base de datos: la cuenta sigue
    existiendo, solo se olvida quién estaba dentro.
    """
    current_user["id"] = None
    current_user["name"] = None
    current_user["email"] = None
    current_user["avatar"] = "🌟"


def is_logged_in() -> bool:
    """Indica si hay alguien con la sesión iniciada.

    Returns:
        True si se llamó a set_current_user() y todavía no se limpió la
        sesión. Se apoya en el "id" porque es el único dato que solo
        puede venir de la base de datos.
    """
    return current_user["id"] is not None
