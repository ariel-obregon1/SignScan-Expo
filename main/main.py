import flet as ft

import database

from screens.welcome_screen import screen_welcome
from screens.sign_up import screen_signup
from screens.sign_in import screen_signin
from screens.personalize_profile import screen_personalizeprofile
from screens.dashboard import screen_dashboard
from screens.translator import screen_translator, stop_active_translator

ROUTES = {
    "/": screen_welcome,
    "/crear-cuenta": screen_signup,
    "/login": screen_signin,
    "/perfil": screen_personalizeprofile,
    "/dashboard": screen_dashboard,
    "/escanear": screen_translator,
}


def main(page: ft.Page):
    database.init_db()

    page.title = "SignScan"
    page.padding = 0
    page.spacing = 0
    page.window.full_screen = True
    page.assets_dir = "assets"

    def route_change(e: ft.RouteChangeEvent):
        # Por si veníamos de la pantalla de traducción: apaga la cámara
        # antes de cambiar de pantalla. No hace nada si no estaba
        # corriendo, así que es seguro llamarlo en cada cambio de ruta.
        stop_active_translator()

        page.controls.clear()
        handler = ROUTES.get(page.route, screen_welcome)
        handler(page)
        page.update()

    def window_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.CLOSE:
            stop_active_translator()
            page.run_task(page.window.destroy)

    page.window.prevent_close = True
    page.window.on_event = window_event

    page.on_route_change = route_change
    page.go(page.route or "/")


ft.run(main)