"""
Pantalla de inicio de sesión (screens/login_screen.py).

Layout de dos paneles: panel izquierdo con marca (logo + tagline),
panel derecho con el formulario de login. Los campos ya son
ft.TextField funcionales — falta conectar la lógica real de
autenticación (se hace en el siguiente paso del flujo).
"""

import flet as ft

# ---- Paleta de colores (tomada del CSS) ----
COLOR_NAVY = "#001845"             # rgba(0, 24, 69, 1)
COLOR_SIDEBAR = "#002060"          # rgba(0, 32, 96, 1) — usado en el degradado de marca
COLOR_TURQUOISE = "#40E0D0"
COLOR_GRAY_TEXT = "#6B7A99"        # rgba(107, 122, 153, 1)
COLOR_PLACEHOLDER = "#99A1AF"      # rgba(153, 161, 175, 1)
COLOR_INPUT_BG = "#F9FAFB"         # rgba(249, 250, 251, 1)
COLOR_BORDER = "#E5E7EB"           # rgba(229, 231, 235, 1)
COLOR_DIVIDER = "#F3F4F6"          # rgba(243, 244, 246, 1)

BRAND_PANEL_WEIGHT = 38   # ~38% del ancho total, como en el diseño
FORM_PANEL_WEIGHT = 62    # ~62% del ancho total


def screen_signin(page: ft.Page):
    page.title = "SignScan - Iniciar sesión"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    page.window.width = 1200
    page.window.height = 780
    page.window.min_width = 900
    page.window.min_height = 650
    page.window.resizable = True
    page.run_task(page.window.center)

    # ================================================================
    # PANEL IZQUIERDO — Marca
    # ================================================================
    brand_logo = ft.Container(
        content=ft.Text("🤟", size=40),
        width=90,
        height=90,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=25,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
    )

    brand_panel = ft.Container(
        content=ft.Column(
            controls=[
                brand_logo,
                ft.Text("SignScan", size=37.5, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                ft.Text("Comunicación accesible para todos", size=17.5, weight=ft.FontWeight.BOLD,
                        color=COLOR_TURQUOISE, text_align=ft.TextAlign.CENTER),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[COLOR_SIDEBAR, "#004A6B", COLOR_NAVY],
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    # ================================================================
    # PANEL DERECHO — Formulario
    # ================================================================
    def back_link(e):
        page.go("/")

    back_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ARROW_BACK, size=16, color=COLOR_GRAY_TEXT),
                ft.Text("Volver", size=17.5, weight=ft.FontWeight.BOLD, color=COLOR_GRAY_TEXT),
            ],
            spacing=5,
        ),
        on_click=back_link,
        ink=True,
        padding=ft.Padding.only(bottom=15),
    )

    def social_button(icon_char: str, icon_color: str, border_color: str = COLOR_BORDER):
        return ft.Container(
            content=ft.Text(icon_char, size=20, color=icon_color, weight=ft.FontWeight.BOLD),
            expand=True,
            height=55,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(0.9, border_color),
            border_radius=16.5,
            alignment=ft.Alignment.CENTER,
            ink=True,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                                 color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        )

    apple_button = ft.Container(
        content=ft.Icon(ft.Icons.APPLE, size=24, color=COLOR_NAVY),
        expand=True, height=55, bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(0.9, COLOR_BORDER), border_radius=16.5,
        alignment=ft.Alignment.CENTER, ink=True,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                             color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
    )

    social_row = ft.Row(
        controls=[
            social_button("G", "#4285F4"),
            apple_button,
            ft.Container(
                content=ft.Text("f", size=22, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                expand=True, height=55, bgcolor="#1877F2",
                border_radius=16.5, alignment=ft.Alignment.CENTER, ink=True,
            ),
        ],
        spacing=15,
    )

    divider_row = ft.Row(
        controls=[
            ft.Container(expand=True, height=1, bgcolor=COLOR_DIVIDER),
            ft.Text("O con email", size=15, color=COLOR_PLACEHOLDER),
            ft.Container(expand=True, height=1, bgcolor=COLOR_DIVIDER),
        ],
        spacing=15,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    email_field = ft.TextField(
        hint_text="Correo electrónico",
        hint_style=ft.TextStyle(color=COLOR_PLACEHOLDER, size=17.5),
        bgcolor=COLOR_INPUT_BG,
        border_color=COLOR_TURQUOISE,
        border_width=1.8,
        border_radius=16.5,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=17.5),
        text_size=17.5,
        cursor_color=COLOR_TURQUOISE,
    )

    password_field = ft.TextField(
        hint_text="Contraseña",
        hint_style=ft.TextStyle(color=COLOR_PLACEHOLDER, size=17.5),
        bgcolor=COLOR_INPUT_BG,
        border_color=COLOR_BORDER,
        border_width=0.9,
        border_radius=16.5,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=17.5),
        text_size=17.5,
        cursor_color=COLOR_TURQUOISE,
        password=True,
        can_reveal_password=True,
    )

    forgot_password = ft.Container(
        content=ft.Text("¿Olvidaste tu contraseña?", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TURQUOISE),
        alignment=ft.Alignment.CENTER_RIGHT,
        padding=ft.Padding.only(top=5),
        ink=True,
    )

    def handle_login(e):
        # TODO: conectar con la lógica real de autenticación
        print("Iniciar sesión:", email_field.value)

    login_button = ft.Container(
        content=ft.Text("Iniciar sesión", size=17.5, color=COLOR_NAVY, weight=ft.FontWeight.W_600),
        alignment=ft.Alignment.CENTER,
        bgcolor=COLOR_TURQUOISE,
        border_radius=16.5,
        padding=ft.Padding.symmetric(vertical=20),
        width=float("inf"),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
        on_click=handle_login,
        ink=True,
    )

    def go_to_signup(e):
        page.go("/crear-cuenta")

    signup_row = ft.Row(
        controls=[
            ft.Text("¿No tienes cuenta? ", size=17.5, color=COLOR_GRAY_TEXT),
            ft.Container(
                content=ft.Text("Crear cuenta", size=20, color=COLOR_NAVY, weight=ft.FontWeight.W_600),
                on_click=go_to_signup,
                ink=True,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    form_card = ft.Container(
        content=ft.Column(
            controls=[
                back_button,
                ft.Text("Bienvenido a SignScan", size=25, color=COLOR_NAVY),
                ft.Container(
                    content=ft.Text("Inicia sesión para continuar", size=17.5, color=COLOR_GRAY_TEXT),
                    padding=ft.Padding.only(top=2.5, bottom=25),
                ),
                ft.Container(content=social_row, padding=ft.Padding.only(bottom=20)),
                ft.Container(content=divider_row, padding=ft.Padding.only(bottom=20)),
                ft.Column(
                    controls=[
                        email_field,
                        password_field,
                        forgot_password,
                    ],
                    spacing=12.5,
                ),
                ft.Container(content=login_button, padding=ft.Padding.only(top=20)),
                ft.Container(content=signup_row, padding=ft.Padding.only(top=20)),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        width=480,
        padding=30,
    )

    form_panel = ft.Container(
        content=form_card,
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.WHITE,
        expand=True,
    )

    # ================================================================
    # LAYOUT PRINCIPAL
    # ================================================================
    root_row = ft.Row(
        controls=[
            ft.Container(content=brand_panel, expand=BRAND_PANEL_WEIGHT),
            ft.Container(content=form_panel, expand=FORM_PANEL_WEIGHT),
        ],
        spacing=0,
        expand=True,
    )

    page.add(
        ft.Container(
            content=root_row,
            expand=True,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=50, color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK)),
        )
    )


if __name__ == "__main__":
    ft.run(screen_signin)