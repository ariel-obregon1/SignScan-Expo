# pantallas/perfil.py

import flet as ft

from componentes.colores import AZUL, ROJO, BLANCO, FONDO_CLARO, TEXTO_GRIS, TEXTO_SUAVE
from componentes.sidebar import estructura_app, avatar_usuario
from componentes.tarjetas import tarjeta_base, tarjeta_opcion
from componentes.botones import boton_secundario
from componentes.base_datos import guardar_historial


def pantalla_perfil(page, ir, usuario, estado, mensaje):

    def cerrar_sesion(e):
        guardar_historial(usuario["correo"], "Sesión", "Cerró sesión en SignScan")

        usuario["nombre"] = ""
        usuario["correo"] = ""
        usuario["avatar"] = "👨"
        usuario["foto"] = ""

        ir("bienvenida")

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Perfil", size=36, color=AZUL, weight=ft.FontWeight.BOLD),
                ft.Text("Administra tu cuenta y preferencias", size=17, color=TEXTO_GRIS),

                ft.Container(height=25),

                tarjeta_base(
                    padding=26,
                    contenido=ft.Column(
                        controls=[
                            ft.Text("MI PERFIL", color=TEXTO_SUAVE, weight=ft.FontWeight.BOLD),
                            ft.Container(height=18),

                            ft.Row(
                                spacing=18,
                                controls=[
                                    avatar_usuario(usuario, 90),
                                    ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                usuario["nombre"] or "Usuario",
                                                size=25,
                                                color=AZUL,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                usuario["correo"] or "usuario@signscan.com",
                                                size=15,
                                                color=TEXTO_GRIS,
                                            ),
                                        ],
                                    ),
                                    ft.Container(expand=True),
                                    boton_secundario(
                                        "Editar perfil",
                                        lambda e: ir("perfil_inicial"),
                                        170,
                                        52,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(height=18),
                tarjeta_opcion("🔔", "Notificaciones", "Alertas y recordatorios", lambda e: ir("notificaciones")),
                ft.Container(height=14),
                tarjeta_opcion("🌐", "Idioma", "Idioma y lengua de señas", lambda e: ir("idioma")),
                ft.Container(height=14),
                tarjeta_opcion("🎨", "Apariencia", "Tema, color y estilo visual", lambda e: ir("apariencia")),
                ft.Container(height=14),
                tarjeta_opcion("🔒", "Privacidad", "Permisos y seguridad", lambda e: ir("privacidad")),
                ft.Container(height=14),
                tarjeta_opcion("❓", "Ayuda y soporte", "Centro de ayuda", lambda e: ir("soporte")),

                ft.Container(height=16),

                ft.Container(
                    height=76,
                    bgcolor="#FFF1F2",
                    border_radius=20,
                    padding=20,
                    on_click=cerrar_sesion,
                    content=ft.Row(
                        spacing=15,
                        controls=[
                            ft.Text("↪", size=24, color=ROJO),
                            ft.Text("Cerrar sesión", size=18, color=ROJO, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),

                ft.Container(height=40),
            ],
        ),
    )

    return estructura_app("perfil", ir, usuario, contenido, FONDO_CLARO)