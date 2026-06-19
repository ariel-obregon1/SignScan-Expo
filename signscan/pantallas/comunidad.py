# pantallas/comunidad.py

import flet as ft

from componentes.colores import AZUL, NARANJA, BLANCO, FONDO_CLARO, TEXTO_GRIS, TEXTO_SUAVE
from componentes.sidebar import estructura_app, avatar_usuario
from componentes.botones import boton_principal
from componentes.base_datos import guardar_post, obtener_posts, guardar_historial


def tarjeta_publicacion(nombre, avatar, contenido, fecha, likes, page, usuario):
    contador = ft.Text(f"♡ {likes}", color=TEXTO_SUAVE, size=14)

    def dar_like(e):
        contador.value = "❤️ Me gusta"
        guardar_historial(usuario["correo"], "Comunidad", "Dio like a una publicación")
        page.update()

    return ft.Container(
        bgcolor=BLANCO,
        border_radius=22,
        padding=22,
        shadow=ft.BoxShadow(blur_radius=12, color="#00000010"),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=48,
                            height=48,
                            bgcolor="#F1F5F9",
                            border_radius=24,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(avatar or "👤", size=24),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(nombre, size=18, color=AZUL, weight=ft.FontWeight.BOLD),
                                ft.Text(str(fecha), size=13, color=TEXTO_SUAVE),
                            ],
                        ),
                    ],
                ),
                ft.Text(contenido, size=17, color="#0F172A"),
                ft.Row(
                    spacing=22,
                    controls=[
                        ft.Container(content=contador, on_click=dar_like),
                        ft.Text("💬 Responder", color=TEXTO_SUAVE, weight=ft.FontWeight.BOLD),
                        ft.Text("↗ Compartir", color=TEXTO_SUAVE, weight=ft.FontWeight.BOLD),
                    ],
                ),
            ],
        ),
    )


def pantalla_comunidad(page, ir, usuario, estado, mensaje):
    entrada = ft.TextField(
        hint_text="¿Qué estás aprendiendo hoy?",
        multiline=True,
        min_lines=3,
        max_lines=3,
        bgcolor="#F8FAFC",
        border_radius=18,
        border_color="#E5EAF1",
    )

    def publicar(e):
        if not entrada.value:
            mensaje("Escribe algo para publicar.")
            return

        guardar_post(usuario["nombre"] or "Usuario", usuario["avatar"], entrada.value)
        guardar_historial(usuario["correo"], "Comunidad", "Creó una publicación")
        mensaje("Publicación creada.")
        ir("comunidad")

    publicaciones = obtener_posts()

    if not publicaciones:
        publicaciones = [
            ("María López", "👩‍💻", '¡Acabo de aprender la seña de "familia"! 🤟', "hace 5 min", 12),
            ("Carlos Ruiz", "👨‍💻", "¿Alguien practica lenguaje de señas panameña?", "hace 1 h", 8),
            ("Ana Torres", "👩‍🎓", "Completé el módulo de colores. ¡Al fin! 🎉", "hace 2 h", 24),
        ]

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Comunidad",
                    size=36,
                    color=AZUL,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Comparte avances, dudas y experiencias con otros usuarios",
                    size=17,
                    color=TEXTO_GRIS,
                ),
                ft.Container(height=25),

                ft.Container(
                    height=105,
                    bgcolor=NARANJA,
                    border_radius=24,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("👥 Comunidad SignScan", size=24, color=BLANCO, weight=ft.FontWeight.BOLD),
                            ft.Text("Conecta con personas interesadas en la lengua de señas", size=15, color=BLANCO),
                        ],
                    ),
                ),

                ft.Container(height=25),

                ft.Container(
                    bgcolor=BLANCO,
                    border_radius=22,
                    padding=24,
                    shadow=ft.BoxShadow(blur_radius=12, color="#00000010"),
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Row(
                                spacing=14,
                                controls=[
                                    avatar_usuario(usuario, 50),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(usuario["nombre"] or "Usuario", size=17, color=AZUL, weight=ft.FontWeight.BOLD),
                                            ft.Text("Comparte con la comunidad", color=TEXTO_SUAVE, size=14),
                                        ],
                                    ),
                                ],
                            ),
                            entrada,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Máximo recomendado: 280 caracteres", color=TEXTO_SUAVE, size=13),
                                    boton_principal("Publicar", publicar, 150, 48),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(height=22),

                *[
                    ft.Column(
                        controls=[
                            tarjeta_publicacion(n, a, c, f, l, page, usuario),
                            ft.Container(height=14),
                        ]
                    )
                    for n, a, c, f, l in publicaciones
                ],

                ft.Container(height=40),
            ],
        ),
    )

    return estructura_app("comunidad", ir, usuario, contenido, FONDO_CLARO)