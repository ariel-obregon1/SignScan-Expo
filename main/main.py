import flet as ft
from screens.bienvenida import pantalla_bienvenida


def main(page: ft.Page):
    page.title = "SignScan"

    page.padding = 0
    page.spacing = 0

    page.window.width = 1400
    page.window.height = 800
    page.assets_dir = "assets"
    pantalla_bienvenida(page)

ft.run(main)