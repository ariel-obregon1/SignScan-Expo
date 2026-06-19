# componentes/carruseles.py

import flet as ft
from componentes.colores import BLANCO, AZUL, TURQUESA, NARANJA, MORADO


def carrusel_principal(ir):
    items = [
        ("📷", "Escanea señas", "Traducción visual preparada con IA", TURQUESA, "escanear"),
        ("📚", "Aprende paso a paso", "Cursos modernos con progreso", NARANJA, "aprender"),
        ("🤖", "Practica con IA", "Tutor inteligente para resolver dudas", MORADO, "ia"),
    ]

    return ft.Row(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        controls=[
            ft.Container(
                width=360,
                height=165,
                bgcolor=color,
                border_radius=26,
                padding=24,
                on_click=lambda e, destino=destino: ir(destino),
                shadow=ft.BoxShadow(
                    blur_radius=18,
                    color="#00000018",
                    offset=ft.Offset(0, 8),
                ),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(icono, size=34),
                        ft.Text(
                            titulo,
                            size=23,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            subtitulo,
                            size=15,
                            color=BLANCO,
                        ),
                    ],
                ),
            )
            for icono, titulo, subtitulo, color, destino in items
        ],
    )


def carrusel_cursos(cursos, abrir_curso):
    return ft.Row(
        scroll=ft.ScrollMode.AUTO,
        spacing=18,
        controls=[
            ft.Container(
                width=250,
                height=160,
                bgcolor=curso.get("color", TURQUESA),
                border_radius=26,
                padding=22,
                on_click=lambda e, c=curso: abrir_curso(c),
                shadow=ft.BoxShadow(
                    blur_radius=16,
                    color="#00000018",
                    offset=ft.Offset(0, 8),
                ),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(curso["icono"], size=32),
                        ft.Text(
                            curso["titulo"],
                            size=22,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            curso["nivel"],
                            size=14,
                            color=BLANCO,
                        ),
                    ],
                ),
            )
            for curso in cursos
        ],
    )