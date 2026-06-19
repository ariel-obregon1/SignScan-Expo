# componentes/tarjetas.py

import flet as ft
from componentes.colores import (
    AZUL, BLANCO, GRIS_BORDE, TEXTO_GRIS, TEXTO_SUAVE, SOMBRA
)


def tarjeta_base(contenido, ancho=None, alto=None, padding=24, color=BLANCO):
    return ft.Container(
        width=ancho,
        height=alto,
        bgcolor=color,
        border_radius=24,
        padding=padding,
        shadow=ft.BoxShadow(
            blur_radius=18,
            color=SOMBRA,
            offset=ft.Offset(0, 6),
        ),
        content=contenido,
    )


def tarjeta_estadistica(icono, numero, etiqueta, color_texto=AZUL):
    return ft.Container(
        expand=True,
        height=120,
        bgcolor=BLANCO,
        border_radius=20,
        padding=18,
        shadow=ft.BoxShadow(
            blur_radius=12,
            color=SOMBRA,
            offset=ft.Offset(0, 6),
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(icono, size=28),
                ft.Text(
                    str(numero),
                    size=28,
                    color=color_texto,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    etiqueta,
                    size=14,
                    color=TEXTO_SUAVE,
                ),
            ],
        ),
    )


def tarjeta_modulo(icono, titulo, descripcion, color, accion=None):
    return ft.Container(
        expand=True,
        height=140,
        bgcolor=color,
        border_radius=22,
        padding=24,
        on_click=accion,
        shadow=ft.BoxShadow(
            blur_radius=16,
            color="#00000018",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(icono, size=30),
                ft.Text(
                    titulo,
                    size=19,
                    color=BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    descripcion,
                    size=14,
                    color=BLANCO,
                ),
            ],
        ),
    )


def tarjeta_opcion(icono, titulo, subtitulo, accion=None, color_texto=AZUL):
    return ft.Container(
        height=84,
        bgcolor=BLANCO,
        border_radius=20,
        padding=20,
        border=ft.border.all(1, GRIS_BORDE),
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="#00000010",
        ),
        on_click=accion,
        content=ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    bgcolor="#F1F5F9",
                    border_radius=16,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(icono, size=24),
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            titulo,
                            size=18,
                            color=color_texto,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            subtitulo,
                            size=13,
                            color=TEXTO_GRIS,
                        ),
                    ],
                ),
                ft.Text(
                    "›",
                    size=28,
                    color=TEXTO_SUAVE,
                ),
            ],
        ),
    )


def tarjeta_curso_visual(icono, titulo, descripcion, nivel, progreso, color, accion=None, bloqueado=False):
    return ft.Container(
        height=122,
        bgcolor=BLANCO,
        border_radius=22,
        padding=22,
        border=ft.border.all(1, GRIS_BORDE),
        on_click=accion,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color="#00000010",
        ),
        content=ft.Row(
            spacing=18,
            controls=[
                ft.Container(
                    width=72,
                    height=72,
                    bgcolor="#F1F5F9",
                    border_radius=22,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("🔒" if bloqueado else icono, size=30),
                ),
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Text(
                                    titulo,
                                    size=20,
                                    color=TEXTO_SUAVE if bloqueado else AZUL,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    bgcolor="#EAF1FF",
                                    border_radius=12,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    content=ft.Text(
                                        nivel,
                                        size=12,
                                        color="#5573A6",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ),
                            ],
                        ),
                        ft.Text(
                            descripcion,
                            size=14,
                            color=TEXTO_GRIS,
                        ),
                        ft.Container(
                            height=8,
                            bgcolor="#F1F5F9",
                            border_radius=20,
                            content=ft.Row(
                                controls=[
                                    ft.Container(
                                        height=8,
                                        width=260 * progreso,
                                        bgcolor=color,
                                        border_radius=20,
                                    )
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Text(
                    "✓" if progreso >= 1 else ("🔒" if bloqueado else "▷"),
                    size=24,
                    color=color if not bloqueado else TEXTO_SUAVE,
                ),
            ],
        ),
    )