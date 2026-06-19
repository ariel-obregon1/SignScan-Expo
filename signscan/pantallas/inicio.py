# pantallas/inicio.py

import flet as ft

from componentes.sidebar import estructura_app
from componentes.carruseles import carrusel_principal

from componentes.tarjetas import (
    tarjeta_estadistica,
    tarjeta_modulo,
)

from componentes.colores import (
    AZUL,
    TURQUESA,
    NARANJA,
    MORADO,
    FONDO_CLARO,
)

from componentes.botones import boton_flotante


def pantalla_inicio(page, ir, usuario, estado, mensaje):

    dialogo = ft.AlertDialog(
        modal=True,
    )

    def abrir_modal(e):

        dialogo.title = ft.Text("¿Qué deseas hacer hoy?")

        dialogo.content = ft.Column(
            tight=True,
            controls=[
                ft.TextButton(
                    "📖 Aprender nuevas señas",
                    on_click=lambda e: ir("aprender"),
                ),
                ft.TextButton(
                    "📷 Escanear señas",
                    on_click=lambda e: ir("escanear"),
                ),
                ft.TextButton(
                    "🤖 Consultar IA",
                    on_click=lambda e: ir("ia"),
                ),
            ],
        )

        page.dialog = dialogo
        dialogo.open = True
        page.update()

    contenido = ft.Container(
        expand=True,
        padding=40,
        content=ft.Stack(
            controls=[

                ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[

                        ft.Text(
                            f"Hola, {usuario['nombre']} 👋",
                            size=38,
                            color=AZUL,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Text(
                            "Bienvenido nuevamente a SignScan",
                            size=18,
                        ),

                        ft.Container(height=25),

                        carrusel_principal(ir),

                        ft.Container(height=30),

                        ft.Row(
                            spacing=18,
                            controls=[

                                tarjeta_estadistica(
                                    "🔥",
                                    5,
                                    "Días de racha",
                                ),

                                tarjeta_estadistica(
                                    "⭐",
                                    150,
                                    "Puntos",
                                ),

                                tarjeta_estadistica(
                                    "📚",
                                    8,
                                    "Lecciones",
                                ),
                            ],
                        ),

                        ft.Container(height=35),

                        ft.Text(
                            "Accesos rápidos",
                            size=26,
                            color=AZUL,
                            weight=ft.FontWeight.BOLD,
                        ),

                        ft.Container(height=20),

                        ft.Row(
                            spacing=18,
                            controls=[

                                tarjeta_modulo(
                                    "📖",
                                    "Aprender",
                                    "Cursos interactivos",
                                    TURQUESA,
                                    lambda e: ir("aprender"),
                                ),

                                tarjeta_modulo(
                                    "📷",
                                    "Escanear",
                                    "Traductor visual",
                                    NARANJA,
                                    lambda e: ir("escanear"),
                                ),

                                tarjeta_modulo(
                                    "🤖",
                                    "IA",
                                    "Tutor inteligente",
                                    MORADO,
                                    lambda e: ir("ia"),
                                ),
                            ],
                        ),

                        ft.Container(height=60),
                    ],
                ),

                ft.Container(
                    right=20,
                    bottom=20,
                    content=boton_flotante(
                        abrir_modal,
                    ),
                ),
            ],
        ),
    )

    return estructura_app(
        "inicio",
        ir,
        usuario,
        contenido,
        FONDO_CLARO,
    )