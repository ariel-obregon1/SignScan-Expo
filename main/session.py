"""
In-memory session for the logged-in user.

Deliberately simple: a module-level dictionary that screens read from
and write to, to know who's using the app right now. It resets every
time the app is closed (it does not persist across runs — that's what
the `users` table in the database is for).
"""

current_user = {
    "id": None,
    "name": None,
    "email": None,
    "avatar": "🌟",
    "photo": None
}


def set_current_user(user: dict):
    current_user["id"] = user["id"]
    current_user["name"] = user["name"]
    current_user["email"] = user["email"]
    current_user["avatar"] = user.get("avatar") or "🌟"
    current_user["photo"] = user.get("photo")


def clear_current_user():
    current_user["id"] = None
    current_user["name"] = None
    current_user["email"] = None
    current_user["avatar"] = "🌟"
    current_user["photo"] = None


def is_logged_in() -> bool:
    return current_user["id"] is not None