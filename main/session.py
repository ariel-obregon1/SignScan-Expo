"""
In-memory session for the logged-in user.

Deliberately simple: a module-level dictionary that screens read from
and write to, to know who's using the app right now. It resets every
time the app is closed (it does not persist across runs — that's what
the `users` table in the database is for).
"""

import flet as ft

current_user = {
    "id": None,
    "name": None,
    "email": None,
    "avatar": "🌟",
    "photo": None,
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


def get_avatar_control(size: int = 16, container_size: int | None = None) -> ft.Control:
    """Single source of truth for "what should the user's avatar look
    like right now". Returns an ft.Image of their chosen profile photo
    if they've set one, otherwise an ft.Text with their emoji avatar.

    Every screen should call this instead of building
    `ft.Text(session.current_user["avatar"], ...)` by hand, so that
    setting a photo in the profile screen makes it show up everywhere
    without having to remember to update each screen individually.

    Wrap the result in a Container with border_radius=999 and
    clip_behavior=ft.ClipBehavior.ANTI_ALIAS to get a circular avatar
    (required so a photo actually gets clipped into a circle instead
    of covering the container as a square).
    """
    photo = current_user.get("photo")
    if photo:
        dim = container_size or size
        return ft.Image(src=photo, width=dim, height=dim, fit=ft.BoxFit.COVER)
    return ft.Text(current_user.get("avatar") or "🌟", size=size)