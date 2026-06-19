# pantallas/aprender.py

import flet as ft

from componentes.colores import (
    AZUL,
    AZUL_CLARO,
    TURQUESA,
    TURQUESA_OSCURO,
    NARANJA,
    MORADO,
    AMARILLO,
    FONDO_CLARO,
    BLANCO,
    TEXTO_GRIS,
    TEXTO_SUAVE,
)

from componentes.sidebar import estructura_app
from componentes.tarjetas import tarjeta_curso_visual, tarjeta_base
from componentes.carruseles import carrusel_cursos
from componentes.base_datos import obtener_progreso, guardar_historial


LECCIONES = [
    {
        "id": "abecedario",
        "icono": "🔤",
        "titulo": "Abecedario",
        "descripcion": "Aprende las letras en lenguaje de señas",
        "nivel": "Básico",
        "total": 30,
        "puntos": 30,
        "bloqueado": False,
        "color": TURQUESA_OSCURO,
    },
    {
        "id": "saludos",
        "icono": "👋",
        "titulo": "Saludos",
        "descripcion": "Hola, adiós, gracias y expresiones básicas",
        "nivel": "Básico",
        "total": 15,
        "puntos": 15,
        "bloqueado": False,
        "color": AZUL_CLARO,
    },
    {
        "id": "numeros",
        "icono": "🔢",
        "titulo": "Números",
        "descripcion": "Aprende números del 1 al 100",
        "nivel": "Básico",
        "total": 11,
        "puntos": 20,
        "bloqueado": False,
        "color": AMARILLO,
    },
    {
        "id": "colores",
        "icono": "🎨",
        "titulo": "Colores",
        "descripcion": "Colores principales en señas",
        "nivel": "Básico",
        "total": 11,
        "puntos": 20,
        "bloqueado": False,
        "color": MORADO,
    },
    {
        "id": "familia",
        "icono": "👨‍👩‍👧",
        "titulo": "Familia",
        "descripcion": "Familiares y relaciones cercanas",
        "nivel": "Intermedio",
        "total": 20,
        "puntos": 25,
        "bloqueado": True,
        "color": NARANJA,
    },
    {
        "id": "comida",
        "icono": "🍎",
        "titulo": "Comida",
        "descripcion": "Alimentos, bebidas y comidas comunes",
        "nivel": "Intermedio",
        "total": 20,
        "puntos": 25,
        "bloqueado": True,
        "color": TURQUESA,
    },
]


def estadistica_oscura(icono, numero, etiqueta):
    return ft.Container(
        expand=True,
        height=118,
        bgcolor=AZUL_CLARO,
        border_radius=22,
        padding=20,
        border=ft.border.all(1, "#5D78BA"),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(icono, size=28),
                ft.Text(
                    str(numero),
                    size=28,
                    color=BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    etiqueta,
                    size=14,
                    color="#C9D8FF",
                ),
            ],
        ),
    )


def logro(icono, titulo, subtitulo, activo=False):
    return ft.Container(
        height=92,
        bgcolor="#FFF8D6" if activo else "#F1F5F9",
        border_radius=18,
        padding=18,
        content=ft.Row(
            spacing=15,
            controls=[
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor=AMARILLO if activo else "#E2E8F0",
                    border_radius=16,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(icono, size=26),
                ),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Text(
                            titulo,
                            size=18,
                            color=AZUL,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            subtitulo,
                            size=14,
                            color=TEXTO_GRIS,
                        ),
                    ],
                ),
            ],
        ),
    )


def pantalla_aprender(page, ir, usuario, estado, mensaje):
    completadas, puntos = obtener_progreso(usuario["correo"])

    def abrir_curso(curso):
        bloqueado = curso["bloqueado"]

        if curso["id"] in ["familia", "comida"] and len(completadas) >= 3:
            bloqueado = False

        if bloqueado:
            mensaje("Completa primero algunos cursos básicos.")
            return

        estado["leccion_actual"] = curso["id"]
        estado["carta_actual"] = 0
        estado["carta_volteada"] = False

        guardar_historial(
            usuario["correo"],
            "Aprender",
            f"Abrió el curso: {curso['titulo']}",
        )

        ir("leccion")

    cursos_recomendados = [curso for curso in LECCIONES if not curso["bloqueado"]]

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    bgcolor=AZUL,
                    padding=ft.padding.only(left=30, right=30, top=20, bottom=35),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                                            ft.Image(src="assets/logo.png", width=44),
                                            ft.Text(
                                                "SignScan",
                                                size=24,
                                                color=BLANCO,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                    ),
                                    ft.Container(width=70),
                                ],
                            ),

                            ft.Container(height=20),

                            ft.Row(
                                spacing=16,
                                controls=[
                                    estadistica_oscura("🔥", len(completadas), "Días activo"),
                                    estadistica_oscura("🎯", len(completadas), "Cursos"),
                                    estadistica_oscura("⭐", puntos, "Puntos"),
                                ],
                            ),
                        ],
                    ),
                ),

                ft.Container(
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Aprender señas",
                                size=32,
                                color=AZUL,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Cursos modernos, progreso y práctica interactiva",
                                size=17,
                                color=TEXTO_GRIS,
                            ),

                            ft.Container(height=24),

                            ft.Text(
                                "Recomendados para ti",
                                size=22,
                                color=AZUL,
                                weight=ft.FontWeight.BOLD,
                            ),

                            ft.Container(height=16),

                            carrusel_cursos(cursos_recomendados, abrir_curso),

                            ft.Container(height=30),

                            tarjeta_base(
                                padding=26,
                                contenido=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Cursos disponibles",
                                            size=24,
                                            color=AZUL,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Selecciona un curso para comenzar",
                                            size=15,
                                            color=TEXTO_GRIS,
                                        ),
                                        ft.Container(height=20),

                                        *[
                                            ft.Column(
                                                controls=[
                                                    tarjeta_curso_visual(
                                                        curso["icono"],
                                                        curso["titulo"],
                                                        curso["descripcion"],
                                                        curso["nivel"],
                                                        1 if curso["id"] in completadas else 0,
                                                        curso["color"],
                                                        lambda e, c=curso: abrir_curso(c),
                                                        curso["bloqueado"] and len(completadas) < 3,
                                                    ),
                                                    ft.Container(height=16),
                                                ],
                                            )
                                            for curso in LECCIONES
                                        ],
                                    ],
                                ),
                            ),

                            ft.Container(height=30),

                            tarjeta_base(
                                padding=26,
                                contenido=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Logros recientes",
                                            size=24,
                                            color=AZUL,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Container(height=18),
                                        logro(
                                            "🏆",
                                            "Primera lección",
                                            "Completa tu primera lección",
                                            len(completadas) >= 1,
                                        ),
                                        ft.Container(height=14),
                                        logro(
                                            "⭐",
                                            "Tres cursos",
                                            "Completa tres cursos básicos",
                                            len(completadas) >= 3,
                                        ),
                                        ft.Container(height=14),
                                        logro(
                                            "🔥",
                                            "Racha activa",
                                            "Mantén una práctica constante",
                                            len(completadas) >= 2,
                                        ),
                                    ],
                                ),
                            ),

                            ft.Container(height=50),
                        ],
                    ),
                ),
            ],
        ),
    )

    return estructura_app("aprender", ir, usuario, contenido, FONDO_CLARO)