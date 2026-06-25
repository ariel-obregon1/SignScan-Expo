import flet as ft
from screens.bienvenida import pantalla_bienvenida


def main(page: ft.Page):
    page.title = "SignScan"

    page.padding = 0
    page.spacing = 0

    page.window.full_screen = True
    page.assets_dir = "assets"
    pantalla_bienvenida(page)

ft.run(main)