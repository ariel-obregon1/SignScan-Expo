# pantallas/video.py

import flet as ft

from componentes.colores import AZUL, AZUL_CLARO, TURQUESA, MORADO, BLANCO
from componentes.botones import boton_principal
from componentes.base_datos import guardar_historial


def tarjeta_interprete(nombre, detalle):
    return ft.Container(
        height=105,
        bgcolor=AZUL_CLARO,
        border_radius=20,
        padding=20,
        border=ft.border.all(1, "#5D78BA"),
        content=ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor="#4968B4",
                    border_radius=30,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("👨‍💼", size=30),
                ),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Text(nombre, size=20, color=BLANCO, weight=ft.FontWeight.BOLD),
                        ft.Text(detalle, color="#C9D8FF"),
                    ],
                ),
                ft.Container(expand=True),
                ft.Text("●  📹", size=22, color=TURQUESA),
            ],
        ),
    )


def pantalla_video(page, ir, usuario, estado, mensaje):
    estado_llamada = ft.Text("", color=BLANCO)

    def iniciar_llamada(e):
        guardar_historial(
            usuario["correo"],
            "Video Chat",
            "Inicio de llamada con intérprete",
        )
        estado_llamada.value = "Buscando intérprete disponible..."
        page.update()

    contenido = ft.Container(
        expand=True,
        bgcolor=AZUL,
        padding=35,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.TextButton(
                            "← Inicio",
                            on_click=lambda e: ir("inicio"),
                            style=ft.ButtonStyle(color=BLANCO),
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Image(src="assets/logo.png", width=45),
                                ft.Text("SignScan", size=24, color=BLANCO, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                        ft.Container(width=80),
                    ],
                ),

                ft.Container(height=25),

                ft.Container(
                    bgcolor=AZUL_CLARO,
                    border_radius=28,
                    padding=35,
                    border=ft.border.all(1, "#5D78BA"),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=110,
                                height=110,
                                bgcolor=MORADO,
                                border_radius=28,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("📹", size=55),
                            ),
                            ft.Text(
                                "Videollamada con intérprete",
                                size=30,
                                color=BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Conéctate con un intérprete certificado de lenguaje de señas",
                                size=16,
                                color="#C9D8FF",
                            ),
                            ft.Container(height=20),
                            boton_principal(
                                "📷  Llamar ahora",
                                iniciar_llamada,
                                1000,
                                65,
                                TURQUESA,
                                AZUL,
                            ),
                            ft.Text("👥  3 intérpretes disponibles", color="#C9D8FF"),
                            estado_llamada,
                        ],
                    ),
                ),

                ft.Container(height=30),

                ft.Text(
                    "👥 Intérpretes Disponibles",
                    size=22,
                    color=BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(height=15),

                tarjeta_interprete("Juan García", "LSM • ⭐ 4.9"),
                ft.Container(height=15),
                tarjeta_interprete("María López", "LSP • ⭐ 5"),
                ft.Container(height=15),
                tarjeta_interprete("Carlos Mendoza", "ASL • ⭐ 4.8"),
            ],
        ),
    )

    return contenido