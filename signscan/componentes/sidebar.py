# componentes/sidebar.py

import os
import flet as ft

from componentes.colores import AZUL, BLANCO, TURQUESA, TEXTO_SUAVE


LOGO = "assets/logo.png"


def logo_signscan(ancho=55):
    return ft.Image(src=LOGO, width=ancho)


def avatar_usuario(usuario, tamano=58):
    foto = usuario.get("foto", "")

    if foto and os.path.exists(foto):
        return ft.Container(
            width=tamano,
            height=tamano,
            border_radius=tamano // 2,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Image(
                src=foto,
                width=tamano,
                height=tamano,
                fit=ft.ImageFit.COVER,
            ),
        )

    return ft.Container(
        width=tamano,
        height=tamano,
        bgcolor="#E7FBF8",
        border_radius=tamano // 2,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            usuario.get("avatar", "👨"),
            size=int(tamano * 0.48),
        ),
    )


def item_menu(nombre, icono, destino, activo, ir, color_acento=TURQUESA):
    seleccionado = activo == destino

    return ft.Container(
        height=56,
        border_radius=18,
        bgcolor=color_acento if seleccionado else "transparent",
        padding=ft.padding.symmetric(horizontal=18),
        on_click=lambda e: ir(destino),
        content=ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    icono,
                    size=22,
                    color=AZUL if seleccionado else BLANCO,
                ),
                ft.Text(
                    nombre,
                    size=17,
                    color=AZUL if seleccionado else BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
    )


def barra_lateral(activo, ir, usuario, color_acento=TURQUESA):
    return ft.Container(
        width=320,
        bgcolor=AZUL,
        padding=25,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        logo_signscan(55),
                        ft.Text(
                            "SignScan",
                            size=27,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),

                ft.Container(height=30),

                ft.Container(
                    bgcolor="#FFFFFF18",
                    border_radius=18,
                    padding=15,
                    content=ft.Row(
                        spacing=14,
                        controls=[
                            avatar_usuario(usuario, 58),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        usuario.get("nombre") or "Usuario",
                                        size=17,
                                        color=BLANCO,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        usuario.get("correo") or "usuario@signscan.com",
                                        color="#CBD5E1",
                                        size=13,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(height=25),
                ft.Container(height=1, bgcolor="#FFFFFF20"),
                ft.Container(height=25),

                item_menu("Inicio", "⌂", "inicio", activo, ir, color_acento),
                item_menu("Historial", "🕒", "historial", activo, ir, color_acento),
                item_menu("Aprender", "📖", "aprender", activo, ir, color_acento),
                item_menu("Escanear", "📷", "escanear", activo, ir, color_acento),
                item_menu("Video", "▣", "video", activo, ir, color_acento),
                item_menu("IA SignScan", "🤖", "ia", activo, ir, color_acento),
                item_menu("Comunidad", "👥", "comunidad", activo, ir, color_acento),
                item_menu("Perfil", "⚙", "perfil", activo, ir, color_acento),

                ft.Container(expand=True),

                ft.Container(
                    height=50,
                    on_click=lambda e: ir("bienvenida"),
                    content=ft.Row(
                        spacing=14,
                        controls=[
                            ft.Text("↪", size=22, color="#C9D8FF"),
                            ft.Text(
                                "Cerrar sesión",
                                size=17,
                                color="#C9D8FF",
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )


def estructura_app(activo, ir, usuario, contenido, fondo="#F5F7FA", color_acento=TURQUESA):
    return ft.Row(
        expand=True,
        spacing=0,
        controls=[
            barra_lateral(activo, ir, usuario, color_acento),
            ft.Container(
                expand=True,
                bgcolor=fondo,
                content=contenido,
            ),
        ],
    )