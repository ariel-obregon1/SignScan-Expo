# pantallas/escanear.py

import flet as ft

from componentes.colores import AZUL, AZUL_CLARO, TURQUESA, BLANCO
from componentes.botones import boton_principal, boton_secundario
from componentes.base_datos import guardar_historial


def pantalla_escanear(page, ir, usuario, estado, mensaje):
    resultado = ft.Text(
        "Resultado: esperando cámara...",
        size=16,
        color="#C9D8FF",
    )

    estado_camara = ft.Text(
        "",
        size=15,
        color=BLANCO,
    )

    def activar_camara(e):
        guardar_historial(
            usuario["correo"],
            "Escanear Señas",
            "Activó la pantalla de cámara",
        )

        estado_camara.value = "Cámara preparada para reconocimiento."
        resultado.value = "IA lista para integrarse con el modelo de señas."
        page.update()

    def simular_ia(e):
        resultado.value = "Seña detectada: HOLA • Confianza: 95%"
        guardar_historial(
            usuario["correo"],
            "IA Escáner",
            "Seña detectada: HOLA",
        )
        page.update()

    contenido = ft.Container(
        expand=True,
        bgcolor=AZUL,
        padding=35,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
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
                        ft.Text(
                            "Escanear Señas",
                            size=26,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(width=80),
                    ],
                ),

                ft.Container(height=30),

                ft.Container(
                    width=820,
                    height=420,
                    bgcolor="#1F5C8A",
                    border_radius=32,
                    alignment=ft.Alignment(0, 0),
                    shadow=ft.BoxShadow(
                        blur_radius=28,
                        color="#00000030",
                        offset=ft.Offset(0, 8),
                    ),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=110,
                                height=110,
                                bgcolor="#3C739B",
                                border_radius=28,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("📷", size=48, color=TURQUESA),
                            ),
                            ft.Container(height=18),
                            ft.Text(
                                "Activar Cámara",
                                size=30,
                                color=BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Usa la cámara para preparar la traducción visual de señas",
                                size=16,
                                color="#C9D8FF",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=22),
                            boton_principal(
                                "Permitir acceso",
                                activar_camara,
                                230,
                                55,
                                TURQUESA,
                                AZUL,
                            ),
                            ft.Container(height=12),
                            boton_secundario(
                                "Simular detección IA",
                                simular_ia,
                                230,
                                50,
                                BLANCO,
                            ),
                            estado_camara,
                        ],
                    ),
                ),

                ft.Container(height=25),

                ft.Container(
                    width=820,
                    bgcolor=AZUL_CLARO,
                    border_radius=24,
                    padding=24,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "🤖 Resultado de IA",
                                size=20,
                                color=BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                            resultado,
                            ft.Text(
                                "Esta sección queda lista para conectar OpenCV, MediaPipe y el modelo de reconocimiento.",
                                size=14,
                                color="#C9D8FF",
                            ),
                        ],
                    ),
                ),

                ft.Container(height=18),

                ft.Container(
                    width=820,
                    bgcolor="#102F84",
                    border_radius=24,
                    padding=24,
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text(
                                "💡 Consejos para mejor detección",
                                size=18,
                                color=BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text("• Mantén tus manos visibles dentro del marco.", color="#C9D8FF"),
                            ft.Text("• Usa buena iluminación.", color="#C9D8FF"),
                            ft.Text("• Realiza las señas de forma clara y pausada.", color="#C9D8FF"),
                        ],
                    ),
                ),
            ],
        ),
    )

    return contenido