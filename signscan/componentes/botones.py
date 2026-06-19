# componentes/botones.py

import flet as ft
from componentes.colores import AZUL, TURQUESA, BLANCO, GRIS_BORDE


def boton_principal(texto, accion=None, ancho=320, alto=54, color=TURQUESA, color_texto=AZUL):
    return ft.ElevatedButton(
        texto,
        width=ancho,
        height=alto,
        bgcolor=color,
        color=color_texto,
        on_click=accion,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18),
            text_style=ft.TextStyle(
                size=17,
                weight=ft.FontWeight.BOLD,
            ),
        ),
    )


def boton_secundario(texto, accion=None, ancho=320, alto=54, color_texto=AZUL):
    return ft.OutlinedButton(
        texto,
        width=ancho,
        height=alto,
        on_click=accion,
        style=ft.ButtonStyle(
            color=color_texto,
            side=ft.BorderSide(2, color_texto),
            shape=ft.RoundedRectangleBorder(radius=18),
            text_style=ft.TextStyle(
                size=17,
                weight=ft.FontWeight.BOLD,
            ),
        ),
    )


def boton_icono(icono, accion=None, tamano=54, color_fondo=BLANCO, color_icono=AZUL):
    return ft.Container(
        width=tamano,
        height=tamano,
        bgcolor=color_fondo,
        border_radius=18,
        alignment=ft.Alignment(0, 0),
        on_click=accion,
        border=ft.border.all(1, GRIS_BORDE),
        content=ft.Text(
            icono,
            size=24,
            color=color_icono,
            weight=ft.FontWeight.BOLD,
        ),
    )


def boton_flotante(accion=None, color=TURQUESA):
    return ft.Container(
        width=78,
        height=78,
        bgcolor=color,
        border_radius=50,
        alignment=ft.Alignment(0, 0),
        on_click=accion,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color="#00000030",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Text(
            "+",
            size=42,
            color=BLANCO,
            weight=ft.FontWeight.BOLD,
        ),
    )