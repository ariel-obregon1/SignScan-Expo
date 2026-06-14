import flet as ft


def main(page: ft.Page):
    page.title = "Escanear Señas"

    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#082D78"
    page.theme_mode = ft.ThemeMode.DARK

    # Ventana
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
    # FUNCIONES
    # =========================

    def go_back(e):
        print("Volver")

    def expand_screen(e):
        page.window.full_screen = not page.window.full_screen
        page.update()

    def allow_camera(e):
        print("Permitir acceso")

    # =========================
    # TOP BAR
    # =========================

    top_bar = ft.Container(
        padding=ft.Padding(
            left=18,
            top=16,
            right=18,
            bottom=16,
        ),

        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[
                # BOTON ATRAS
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

                # TITULO
                ft.Text(
                    "Escanear Señas",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=white,
                ),

                # FULLSCREEN
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
                # ICONO
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

                # TITULO
                ft.Text(
                    "Activar Cámara",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=white,
                ),

                # DESCRIPCION
                ft.Text(
                    "Necesitamos acceso a tu cámara para traducir el\nlenguaje de señas en tiempo real",
                    size=14,
                    color=muted,
                    text_align=ft.TextAlign.CENTER,
                ),

                # BOTON
                ft.Container(
                    margin=ft.Margin(
                        left=0,
                        top=6,
                        right=0,
                        bottom=0,
                    ),

                    content=ft.ElevatedButton(
                        "Permitir acceso",
                        on_click=allow_camera,

                        style=ft.ButtonStyle(
                            bgcolor=accent,
                            color="#0D3E66",

                            padding=ft.Padding(
                                left=28,
                                top=16,
                                right=28,
                                bottom=16,
                            ),

                            shape=ft.RoundedRectangleBorder(
                                radius=18
                            ),

                            text_style=ft.TextStyle(
                                size=14,
                                weight=ft.FontWeight.W_600,
                            ),
                        ),
                    ),
                ),
            ],
        ),
    )

    # =========================
    # TARJETA CONSEJOS
    # =========================

    tips_card = ft.Container(
        width=600,
        bgcolor=card_dark,
        border_radius=16,

        padding=ft.Padding(
            left=18,
            top=14,
            right=18,
            bottom=14,
        ),

        content=ft.Column(
            spacing=8,

            controls=[
                ft.Row(
                    spacing=8,

                    controls=[
                        ft.Text(
                            "💡",
                            size=14,
                        ),

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
                        ft.Text(
                            "• Mantén tus manos visibles dentro del marco",
                            size=12,
                            color=muted,
                        ),

                        ft.Text(
                            "• Asegúrate de tener buena iluminación",
                            size=12,
                            color=muted,
                        ),

                        ft.Text(
                            "• Realiza las señas de forma clara y pausada",
                            size=12,
                            color=muted,
                        ),
                    ],
                ),
            ],
        ),
    )

    # =========================
    # CONTENIDO
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

                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, -1),
                        content=main_card,
                    ),

                    ft.Container(height=18),

                    tips_card,

                    ft.Container(height=24),
                ],
            ),
        )
    )


ft.run(main)