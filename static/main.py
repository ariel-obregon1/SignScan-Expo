import flet as ft
import threading
import time
from sign_engine import SignEngine
import asyncio
engine = None


def main(page: ft.Page):

    page.title = "Escanear Señas"

    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#082D78"
    page.theme_mode = ft.ThemeMode.DARK

    page.window.width = 960
    page.window.height = 540
    page.window.min_width = 820
    page.window.min_height = 520

    # =========================
    # COLORES
    # =========================

    bg = "#082D78"
    card = "#2F6796"
    card_dark = "#1B3F83"
    accent = "#48E6E0"
    white = "#FFFFFF"
    muted = "#C9D3E3"

    # =========================
    # TEXTO DINÁMICO
    # =========================

    text_view = ft.Text(
        "Texto: -",
        size=16,
        color=white,
        selectable=True
    )

    # =========================
    # FUNCIONES
    # =========================

    def go_back(e):
        print("Volver")

    def expand_screen(e):
        page.window.full_screen = not page.window.full_screen
        page.update()

    def start_camera(e):
        global engine

        if engine is None:
            engine = SignEngine()

            def run_engine():
                engine.start()

            threading.Thread(
                target=run_engine,
                daemon=True
            ).start()

    def stop_camera(e):
        if engine:
            engine.stop()

    async def auto_refresh():

        while True:

            if engine:

                nuevo_texto = engine.get_text()

                if text_view.value != f"Texto: {nuevo_texto}":

                    text_view.value = f"Texto: {nuevo_texto}"
                    page.update()

            await asyncio.sleep(0.2)

    def refresh_text(e):
        if engine:
            text_view.value = f"Texto: {engine.get_text()}"
            page.update()

    # =========================
    # TOP BAR
    # =========================

    top_bar = ft.Container(
        padding=ft.Padding(18, 16, 18, 16),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=38,
                    height=38,
                    border_radius=19,
                    bgcolor="#173D86",
                    alignment=ft.Alignment(0, 0),
                    content=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=white,
                        icon_size=20,
                        on_click=go_back,
                    ),
                ),

                ft.Text(
                    "Escanear Señas",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=white,
                ),

                ft.Container(
                    width=38,
                    height=38,
                    border_radius=19,
                    bgcolor="#173D86",
                    alignment=ft.Alignment(0, 0),
                    content=ft.IconButton(
                        icon=ft.Icons.OPEN_IN_FULL,
                        icon_color=white,
                        icon_size=18,
                        on_click=expand_screen,
                    ),
                ),
            ],
        ),
    )

    # =========================
    # TARJETA PRINCIPAL
    # =========================

    main_card = ft.Container(
        width=600,
        height=318,
        bgcolor=card,
        border_radius=24,
        alignment=ft.Alignment(0, 0),
        padding=28,

        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,

            controls=[
                ft.Container(
                    width=80,
                    height=80,
                    border_radius=16,
                    bgcolor="#3E739F",
                    alignment=ft.Alignment(0, 0),

                    content=ft.Icon(
                        ft.Icons.PHOTO_CAMERA_OUTLINED,
                        size=36,
                        color=accent,
                    ),
                ),

                ft.Text(
                    "Activar Cámara",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=white,
                ),

                ft.Text(
                    "Inicia la cámara para traducir lenguaje de señas en tiempo real",
                    size=14,
                    color=muted,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.ElevatedButton(
                    "Iniciar IA",
                    on_click=start_camera,
                    bgcolor=accent,
                    color="#0D3E66",
                ),

                ft.ElevatedButton(
                    "Actualizar texto",
                    on_click=refresh_text,
                    bgcolor="#3E739F",
                    color=white,
                ),
            ],
        ),
    )

    # =========================
    # CONSEJOS
    # =========================

    tips_card = ft.Container(
        width=600,
        bgcolor=card_dark,
        border_radius=16,
        padding=ft.Padding(18, 14, 18, 14),

        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("💡", size=14),
                        ft.Text(
                            "Consejos para mejor detección",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=white,
                        ),
                    ],
                ),

                ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text("• Mantén tus manos visibles", size=12, color=muted),
                        ft.Text("• Buena iluminación", size=12, color=muted),
                        ft.Text("• Movimientos claros", size=12, color=muted),
                    ],
                ),

                text_view,
            ],
        ),
    )

    # =========================
    # HILO DE ACTUALIZACIÓN
    # =========================

    page.run_task(auto_refresh)

    # =========================
    # UI
    # =========================

    page.add(
        ft.Container(
            expand=True,
            bgcolor=bg,

            content=ft.Column(
                expand=True,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                controls=[
                    top_bar,
                    ft.Container(height=24),
                    main_card,
                    ft.Container(height=18),
                    tips_card,
                    ft.Container(height=24),
                ],
            ),
        )
    )


ft.run(main)