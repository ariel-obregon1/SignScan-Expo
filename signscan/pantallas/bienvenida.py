# pantallas/bienvenida.py

import flet as ft

from componentes.colores import (
    AZUL,
    AZUL_OSCURO,
    TURQUESA,
    BLANCO,
    FONDO_CLARO,
    TEXTO_GRIS,
    TEXTO_SUAVE,
)
from componentes.botones import boton_principal, boton_secundario


def icono_bienvenida(icono, titulo):
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=76,
                height=76,
                bgcolor="#FFFFFF22",
                border_radius=20,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(icono, size=30),
            ),
            ft.Container(height=8),
            ft.Text(
                titulo,
                size=14,
                color=BLANCO,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )


def pantalla_bienvenida(page, ir, usuario, estado, mensaje):
    lado_izquierdo = ft.Container(
        width=725,
        gradient=ft.LinearGradient(
            colors=[AZUL_OSCURO, AZUL, TURQUESA],
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
        ),
        content=ft.Stack(
            controls=[
                ft.Container(
                    width=350,
                    height=350,
                    border_radius=180,
                    bgcolor="#FFFFFF10",
                    right=-120,
                    top=-145,
                ),
                ft.Container(
                    width=260,
                    height=260,
                    border_radius=130,
                    bgcolor="#FFFFFF10",
                    left=-115,
                    bottom=-110,
                ),
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="assets/logo.png", width=190),
                        ft.Container(height=34),
                        ft.Text(
                            "SignScan",
                            size=64,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            "Rompiendo barreras de comunicación",
                            size=23,
                            color=TURQUESA,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=54),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=55,
                            controls=[
                                icono_bienvenida("🤟", "Lenguaje de\nseñas"),
                                icono_bienvenida("🧠", "IA avanzada"),
                                icono_bienvenida("🌎", "Comunidad"),
                            ],
                        ),
                        ft.Container(height=52),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=9,
                            controls=[
                                ft.Text("●", size=22, color=AZUL),
                                ft.Text("●", size=22, color=TURQUESA),
                                ft.Text("●", size=22, color=BLANCO),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    lado_derecho = ft.Container(
        expand=True,
        bgcolor=BLANCO,
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=610,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(
                                "Comunicación\naccesible para todos",
                                size=58,
                                color=AZUL,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "Aprende, comunícate y conecta usando\n"
                                "inteligencia artificial y lenguaje de señas.",
                                size=22,
                                color=TEXTO_GRIS,
                            ),
                            ft.Container(height=50),
                            boton_principal(
                                "Crear cuenta",
                                lambda e: ir("crear_cuenta"),
                                520,
                                70,
                                TURQUESA,
                                AZUL,
                            ),
                            ft.Container(height=20),
                            boton_secundario(
                                "Iniciar sesión",
                                lambda e: ir("iniciar_sesion"),
                                520,
                                70,
                                AZUL,
                            ),
                            ft.Container(height=40),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        "Al continuar aceptas nuestros ",
                                        size=16,
                                        color=TEXTO_SUAVE,
                                    ),
                                    ft.Text(
                                        "Términos de servicio",
                                        size=16,
                                        color=TURQUESA,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Row(
        expand=True,
        spacing=0,
        controls=[
            lado_izquierdo,
            lado_derecho,
        ],
    )