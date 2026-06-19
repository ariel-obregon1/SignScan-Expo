# pantallas/perfil_inicial.py

import flet as ft

from componentes.colores import (
    AZUL,
    TURQUESA,
    BLANCO,
    FONDO_CLARO,
    TEXTO_GRIS,
)

from componentes.botones import boton_principal
from componentes.base_datos import actualizar_usuario


AVATARES = [
    "👨", "👩", "🧑", "👨‍💻",
    "👩‍💻", "👨‍🎓", "👩‍🎓",
    "🧑‍🎨", "👨‍⚕️", "👩‍⚕️"
]


def pantalla_perfil_inicial(page, ir, usuario, estado, mensaje):

    avatar_actual = {"valor": "👨"}

    nombre_visible = ft.TextField(
        hint_text="Nombre visible",
        width=420,
        height=58,
        border_radius=18,
    )

    fila_avatares = ft.Row(
        scroll=ft.ScrollMode.AUTO,
        spacing=15,
    )

    def seleccionar_avatar(icono):
        avatar_actual["valor"] = icono

        fila_avatares.controls.clear()

        for avatar in AVATARES:

            seleccionado = avatar == avatar_actual["valor"]

            fila_avatares.controls.append(
                ft.Container(
                    width=72,
                    height=72,
                    bgcolor=TURQUESA if seleccionado else BLANCO,
                    border_radius=20,
                    alignment=ft.Alignment(0, 0),
                    border=ft.border.all(
                        3 if seleccionado else 1,
                        AZUL if seleccionado else "#E5EAF1",
                    ),
                    on_click=lambda e, a=avatar: seleccionar_avatar(a),
                    content=ft.Text(
                        avatar,
                        size=34,
                    ),
                )
            )

        page.update()

    seleccionar_avatar("👨")

    def continuar(e):

        if nombre_visible.value:

            usuario["nombre"] = nombre_visible.value

        usuario["avatar"] = avatar_actual["valor"]

        actualizar_usuario(
            usuario["correo"],
            nombre=usuario["nombre"],
            avatar=usuario["avatar"],
        )

        ir("inicio")

    return ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[

                ft.Image(
                    src="assets/logo.png",
                    width=110,
                ),

                ft.Container(height=15),

                ft.Text(
                    "Completa tu perfil",
                    size=36,
                    color=AZUL,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Text(
                    "Personaliza tu experiencia en SignScan",
                    size=18,
                    color=TEXTO_GRIS,
                ),

                ft.Container(height=30),

                fila_avatares,

                ft.Container(height=25),

                nombre_visible,

                ft.Container(height=30),

                boton_principal(
                    "Continuar",
                    continuar,
                    420,
                    60,
                ),
            ],
        ),
    )