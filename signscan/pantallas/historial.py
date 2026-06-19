# pantallas/historial.py

import flet as ft

from componentes.colores import AZUL, BLANCO, FONDO_CLARO, TEXTO_GRIS, TEXTO_SUAVE
from componentes.sidebar import estructura_app
from componentes.base_datos import obtener_historial


def icono_tipo(tipo):
    if "Lección" in tipo or "Aprender" in tipo:
        return "📖"
    if "Cuenta" in tipo:
        return "👤"
    if "Comunidad" in tipo:
        return "👥"
    if "Video" in tipo:
        return "🎥"
    if "Escanear" in tipo:
        return "📷"
    if "IA" in tipo:
        return "🤖"
    return "🕒"


def tarjeta_historial(tipo, descripcion, fecha):
    return ft.Container(
        bgcolor=BLANCO,
        border_radius=20,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
        content=ft.Row(
            controls=[
                ft.Container(
                    width=58,
                    height=58,
                    bgcolor="#F1F5F9",
                    border_radius=18,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(icono_tipo(tipo), size=26),
                ),
                ft.Column(
                    expand=True,
                    spacing=4,
                    controls=[
                        ft.Text(tipo, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                        ft.Text(descripcion, color=TEXTO_GRIS, size=14),
                    ],
                ),
                ft.Text(fecha, color=TEXTO_SUAVE, size=13),
            ],
        ),
    )


def pantalla_historial(page, ir, usuario, estado, mensaje):
    datos = obtener_historial(usuario["correo"])

    if not datos:
        datos = [("Historial", "Aún no tienes actividad registrada.", "—")]

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Historial", size=36, color=AZUL, weight=ft.FontWeight.BOLD),
                ft.Text("Tus actividades recientes en SignScan", size=17, color=TEXTO_GRIS),
                ft.Container(height=25),

                ft.Container(
                    bgcolor=BLANCO,
                    border_radius=24,
                    padding=24,
                    shadow=ft.BoxShadow(blur_radius=14, color="#00000010"),
                    content=ft.Column(
                        controls=[
                            ft.Text("Actividad reciente", size=24, color=AZUL, weight=ft.FontWeight.BOLD),
                            ft.Container(height=18),
                            *[
                                ft.Column(
                                    controls=[
                                        tarjeta_historial(tipo, descripcion, fecha),
                                        ft.Container(height=14),
                                    ]
                                )
                                for tipo, descripcion, fecha in datos
                            ],
                        ],
                    ),
                ),
            ],
        ),
    )

    return estructura_app("historial", ir, usuario, contenido, FONDO_CLARO)