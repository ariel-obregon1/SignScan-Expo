# pantallas/ia.py

import flet as ft

from componentes.colores import AZUL, TURQUESA, BLANCO, FONDO_CLARO, GRIS, TEXTO_GRIS
from componentes.sidebar import estructura_app
from componentes.botones import boton_principal
from componentes.base_datos import guardar_historial


def pantalla_ia(page, ir, usuario, estado, mensaje):
    mensajes = ft.Column(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
    )

    entrada = ft.TextField(
        hint_text="Pregúntale algo a SignScan IA...",
        expand=True,
        height=55,
        bgcolor=GRIS,
        border_radius=18,
        border_color=GRIS,
    )

    def burbuja(texto, usuario_escribe=False):
        return ft.Row(
            alignment=ft.MainAxisAlignment.END if usuario_escribe else ft.MainAxisAlignment.START,
            controls=[
                ft.Container(
                    constraints=ft.BoxConstraints(max_width=620),
                    bgcolor=TURQUESA if usuario_escribe else BLANCO,
                    border_radius=20,
                    padding=16,
                    shadow=ft.BoxShadow(
                        blur_radius=8,
                        color="#00000010",
                    ),
                    content=ft.Text(
                        texto,
                        size=15,
                        color=AZUL,
                    ),
                )
            ],
        )

    def respuesta_ia(pregunta):
        pregunta = pregunta.lower()

        if "hola" in pregunta:
            return "Para practicar la seña de hola, usa el curso de Saludos y repite la carta hasta memorizar el movimiento."

        if "curso" in pregunta:
            return "Te recomiendo empezar por Abecedario, luego Saludos y después Números."

        if "camara" in pregunta or "cámara" in pregunta:
            return "La cámara está preparada para integrarse con el modelo de IA de reconocimiento de señas."

        if "gracias" in pregunta:
            return "La seña de gracias forma parte del curso de Saludos. Puedes practicarla con las tarjetas volteables."

        return "Soy SignScan IA. Puedo ayudarte con señas, cursos, progreso, cámara y práctica diaria."

    def enviar(e):
        if not entrada.value:
            mensaje("Escribe una pregunta primero.")
            return

        pregunta = entrada.value
        respuesta = respuesta_ia(pregunta)

        mensajes.controls.append(burbuja(pregunta, True))
        mensajes.controls.append(burbuja(respuesta, False))

        guardar_historial(
            usuario["correo"],
            "IA SignScan",
            f"Consulta: {pregunta}",
        )

        entrada.value = ""
        page.update()

    mensajes.controls.append(
        burbuja(
            "Hola, soy SignScan IA. Puedo ayudarte a aprender señas, recomendar cursos y resolver dudas.",
            False,
        )
    )

    contenido = ft.Container(
        expand=True,
        bgcolor=FONDO_CLARO,
        padding=40,
        content=ft.Column(
            controls=[
                ft.Text(
                    "IA SignScan",
                    size=36,
                    color=AZUL,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Tutor inteligente para practicar y aprender",
                    size=17,
                    color=TEXTO_GRIS,
                ),

                ft.Container(height=24),

                ft.Container(
                    height=520,
                    bgcolor="#F8FAFC",
                    border_radius=26,
                    padding=24,
                    shadow=ft.BoxShadow(
                        blur_radius=14,
                        color="#00000010",
                    ),
                    content=mensajes,
                ),

                ft.Container(height=18),

                ft.Row(
                    spacing=12,
                    controls=[
                        entrada,
                        boton_principal(
                            "Enviar",
                            enviar,
                            130,
                            55,
                            TURQUESA,
                            AZUL,
                        ),
                    ],
                ),
            ],
        ),
    )

    return estructura_app("ia", ir, usuario, contenido, FONDO_CLARO)