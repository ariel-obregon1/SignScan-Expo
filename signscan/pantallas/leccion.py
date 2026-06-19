# pantallas/leccion.py

import flet as ft

from componentes.colores import (
    AZUL,
    BLANCO,
    TURQUESA,
    TURQUESA_OSCURO,
    AZUL_CLARO,
    AMARILLO,
    NARANJA,
    MORADO,
)
from componentes.botones import boton_principal, boton_secundario
from componentes.base_datos import completar_leccion, guardar_historial


CARTAS = {
    "abecedario": [
        {"frente": "A", "titulo": "Letra A", "descripcion": "Cierra la mano formando un puño y mantén el pulgar al lado."},
        {"frente": "B", "titulo": "Letra B", "descripcion": "Extiende los dedos juntos y coloca el pulgar hacia la palma."},
        {"frente": "C", "titulo": "Letra C", "descripcion": "Forma una C con la mano, como si sostuvieras un objeto redondo."},
        {"frente": "D", "titulo": "Letra D", "descripcion": "Levanta el dedo índice y curva los demás dedos."},
    ],
    "saludos": [
        {"frente": "👋", "titulo": "Hola", "descripcion": "Saludo básico para iniciar una conversación."},
        {"frente": "🙏", "titulo": "Gracias", "descripcion": "Seña usada para expresar agradecimiento."},
        {"frente": "🤝", "titulo": "Mucho gusto", "descripcion": "Se usa cuando conoces a una persona."},
        {"frente": "👋", "titulo": "Adiós", "descripcion": "Seña usada para despedirse."},
    ],
    "numeros": [
        {"frente": "1", "titulo": "Número 1", "descripcion": "Levanta un dedo."},
        {"frente": "2", "titulo": "Número 2", "descripcion": "Levanta dos dedos."},
        {"frente": "3", "titulo": "Número 3", "descripcion": "Levanta tres dedos."},
        {"frente": "4", "titulo": "Número 4", "descripcion": "Levanta cuatro dedos."},
    ],
    "colores": [
        {"frente": "🔴", "titulo": "Rojo", "descripcion": "Color rojo en lenguaje de señas."},
        {"frente": "🔵", "titulo": "Azul", "descripcion": "Color azul en lenguaje de señas."},
        {"frente": "🔵", "titulo": "Amarillo", "descripcion": "Color amarillo en lenguaje de señas."},
        {"frente": "🟢", "titulo": "Verde", "descripcion": "Color verde en lenguaje de señas."},
    ],
    "familia": [
        {"frente": "👨", "titulo": "Papá", "descripcion": "Seña relacionada con el padre."},
        {"frente": "👩", "titulo": "Mamá", "descripcion": "Seña relacionada con la madre."},
        {"frente": "👧", "titulo": "Hija", "descripcion": "Seña relacionada con hija."},
    ],
    "comida": [
        {"frente": "🍎", "titulo": "Comida", "descripcion": "Seña general para comida."},
        {"frente": "🥤", "titulo": "Bebida", "descripcion": "Seña relacionada con beber."},
        {"frente": "🍞", "titulo": "Pan", "descripcion": "Seña relacionada con pan."},
    ],
}


DATOS = {
    "abecedario": ("Abecedario", TURQUESA_OSCURO, 30),
    "saludos": ("Saludos", AZUL_CLARO, 15),
    "numeros": ("Números", AMARILLO, 20),
    "colores": ("Colores", MORADO, 20),
    "familia": ("Familia", NARANJA, 25),
    "comida": ("Comida", TURQUESA, 25),
}


def pantalla_leccion(page, ir, usuario, estado, mensaje):
    leccion_id = estado.get("leccion_actual", "abecedario")
    cartas = CARTAS.get(leccion_id, CARTAS["abecedario"])
    nombre, color, puntos = DATOS.get(leccion_id, ("Lección", TURQUESA, 10))

    indice = estado.get("carta_actual", 0)
    volteada = estado.get("carta_volteada", False)
    carta = cartas[indice]

    def voltear(e):
        estado["carta_volteada"] = not estado["carta_volteada"]
        ir("leccion")

    def anterior(e):
        if estado["carta_actual"] > 0:
            estado["carta_actual"] -= 1
            estado["carta_volteada"] = False
            ir("leccion")
        else:
            mensaje("Ya estás en la primera carta.")

    def siguiente(e):
        if estado["carta_actual"] < len(cartas) - 1:
            estado["carta_actual"] += 1
            estado["carta_volteada"] = False
            ir("leccion")
        else:
            mensaje("Ya estás en la última carta.")

    def completar(e):
        completar_leccion(usuario["correo"], leccion_id, puntos)
        guardar_historial(
            usuario["correo"],
            "Lección completada",
            f"Completó la lección {nombre}",
        )
        mensaje("Lección completada correctamente.")
        ir("aprender")

    contenido_frente = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Image(src="assets/logo.png", width=120),
            ft.Container(height=20),
            ft.Text(
                "Toca para ver",
                size=25,
                color=BLANCO,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                "Descubre la seña de esta carta",
                size=16,
                color="#E0F2FE",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )

    contenido_reverso = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=130,
                height=130,
                bgcolor="#FFFFFF25",
                border_radius=32,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    carta["frente"],
                    size=72,
                    color=BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
            ),
            ft.Container(height=24),
            ft.Text(
                carta["titulo"],
                size=32,
                color=BLANCO,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=12),
            ft.Text(
                carta["descripcion"],
                size=17,
                color="#E0F2FE",
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )

    return ft.Container(
        expand=True,
        bgcolor=AZUL,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=25, right=25, top=18, bottom=25),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.TextButton(
                                "← Aprender",
                                on_click=lambda e: ir("aprender"),
                                style=ft.ButtonStyle(color=BLANCO),
                            ),
                            ft.Text(
                                nombre,
                                size=26,
                                color=BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(width=90),
                        ],
                    ),
                ),

                ft.Text(
                    f"Carta {indice + 1} de {len(cartas)}",
                    size=18,
                    color="#C9D8FF",
                ),

                ft.Container(height=22),

                ft.Container(
                    width=520,
                    padding=28,
                    bgcolor="#FFFFFF14",
                    border_radius=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=430,
                                height=430,
                                bgcolor=color,
                                border_radius=35,
                                padding=30,
                                alignment=ft.Alignment(0, 0),
                                animate=ft.Animation(450, "easeInOut"),
                                shadow=ft.BoxShadow(
                                    blur_radius=35,
                                    color="#00000030",
                                    offset=ft.Offset(0, 10),
                                ),
                                on_click=voltear,
                                content=contenido_reverso if volteada else contenido_frente,
                            ),

                            ft.Container(height=24),

                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=18,
                                controls=[
                                    boton_secundario(
                                        "Anterior",
                                        anterior,
                                        140,
                                        52,
                                        BLANCO,
                                    ),
                                    boton_principal(
                                        "Voltear",
                                        voltear,
                                        140,
                                        52,
                                        TURQUESA,
                                        AZUL,
                                    ),
                                    boton_secundario(
                                        "Siguiente",
                                        siguiente,
                                        140,
                                        52,
                                        BLANCO,
                                    ),
                                ],
                            ),

                            ft.Container(height=22),

                            boton_principal(
                                "Completar lección",
                                completar,
                                430,
                                58,
                                TURQUESA,
                                AZUL,
                            ),
                        ],
                    ),
                ),

                ft.Container(height=40),
            ],
        ),
    )