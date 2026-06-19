# pantallas/splash.py

import flet as ft
from componentes.colores import BLANCO, AZUL


def pantalla_splash(page, ir, usuario, estado, mensaje):
    return ft.Container(
        expand=True,
        bgcolor=BLANCO,
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=260,
                    height=260,
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e: ir("bienvenida"),
                    content=ft.Image(
                        src="assets/logo.png",
                        width=240,
                    ),
                ),
                ft.Container(height=12),
                ft.Text(
                    "Toca el logo para comenzar",
                    size=16,
                    color=AZUL,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
    )