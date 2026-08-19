"""
Pantalla de bienvenida — screens/welcome_screen.py

Es la primera pantalla de la app (ruta "/") y la puerta de entrada:
desde aquí se va a crear cuenta ("/create-account") o a iniciar sesión
("/login").

Estructura: dos paneles en una fila.
    - Panel izquierdo (40%): fondo azul con el logo, el nombre de la app
      y tres tarjetas de características.
    - Panel derecho (60%): fondo blanco con el texto principal y los
      botones de acción.

Como todas las pantallas del proyecto, es una función que recibe la
`page` de Flet y le añade controles; no devuelve nada. Quien decide
cuándo llamarla es el enrutador de main.py.
"""

import flet as ft

# =========================
# COLORES
# =========================

DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"

APP_GRAY = "#E5E7EB"
PANEL_GRAY = "#F1F5F9"

TEXT_GRAY = "#6B7A99"
LIGHT_GRAY = "#9BA8BF"

WHITE = "#FFFFFF"

# Shared button shapes so every button in this screen has the same
# rounded corners as the app's cards/inputs (14-20px radius elsewhere)
# instead of Flet's default, much squarer Material shape.
PRIMARY_BUTTON_STYLE = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14))
OUTLINED_BUTTON_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=14),
    side=ft.BorderSide(1, "#CBD5E1"),
    color=DARK_BLUE,
)


# =========================
# TARJETAS
# =========================

def _feature_card(icon, text):
    """Construye una de las tres tarjetas de características.

    Es un cuadrado azul con borde translúcido, un emoji grande dentro y
    una etiqueta debajo. Se usa para "Signs", "AI" y "Community".

    Args:
        icon: emoji que se muestra dentro del cuadrado.
        text: etiqueta corta que va debajo del cuadrado.

    Returns:
        La columna de Flet ya montada, lista para meter en una fila.
    """
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Container(
                width=90,
                height=90,
                bgcolor="#244080",
                border=ft.Border(
                    left=ft.BorderSide(1, "#4DFFFFFF"),
                    top=ft.BorderSide(1, "#4DFFFFFF"),
                    right=ft.BorderSide(1, "#4DFFFFFF"),
                    bottom=ft.BorderSide(1, "#4DFFFFFF"),
                ),
                border_radius=20,
                content=ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            icon,
                            size=35,
                            color=WHITE,
                        )
                    ],
                ),
            ),
            ft.Text(
                text,
                color=WHITE,
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
        ],
    )


# =========================
# NAVEGACIÓN
# =========================

def open_create_account(page):
    """Lleva a la pantalla de alta de cuenta.

    Args:
        page: la página de Flet, que es quien sabe cambiar de ruta.
    """
    page.go("/create-account")


# =========================
# SCREEN
# =========================

def screen_welcome(page):
    """Dibuja la pantalla de bienvenida completa sobre `page`.

    Monta los dos paneles (marca a la izquierda, acciones a la derecha)
    y los añade dentro de un contenedor con margen, que es lo que da el
    efecto de tarjeta flotando sobre el fondo.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    # Esto faltaba: sin ello la pantalla se queda con el relleno y la
    # tipografía por defecto de Flet en vez de los del resto de la app
    # (diseño de borde a borde, fuente Nunito, título y fondo iguales).
    page.title = "SignScan - Welcome"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    page.controls.clear()

    # ================================================================
    # LEFT PANEL — Branding
    # ================================================================
    logo_card = ft.Container(
        width=150,
        height=150,
        bgcolor=WHITE,
        border_radius=32,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=30,
            color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
            offset=ft.Offset(0, 12),
        ),
        content=ft.Image(
            src="logo.png",
            width=96,
            height=96,
            fit=ft.BoxFit.CONTAIN,
        ),
    )

    left_panel = ft.Container(
        expand=4,
        bgcolor=MAIN_BLUE,
        padding=40,

        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[
                logo_card,

                ft.Container(height=25),

                ft.Text(
                    "SignScan",
                    size=64,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),

                ft.Text(
                    "Breaking down communication barriers",
                    size=24,
                    color=TURQUOISE,
                ),

                ft.Container(height=40),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30,
                    controls=[
                        _feature_card("🤟", "Signs"),
                        _feature_card("🤖", "AI"),
                        _feature_card("👥", "Community"),
                    ],
                ),
            ],
        ),
    )

    # ================================================================
    # RIGHT PANEL — Card (same style as sign_up.py / sign_in.py)
    # ================================================================
    welcome_content = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "Accessible communication\nfor everyone",
                size=36,
                weight=ft.FontWeight.BOLD,
                color=DARK_BLUE,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Container(height=15),

            ft.Text(
                "Learn sign language with AI, connect with the community, "
                "and communicate without barriers.",
                size=17,
                color=TEXT_GRAY,
                text_align=ft.TextAlign.CENTER,
            ),

            ft.Container(height=35),

            ft.ElevatedButton(
                "Create free account",
                width=420,
                height=55,
                bgcolor=TURQUOISE,
                color=DARK_BLUE,
                style=PRIMARY_BUTTON_STYLE,
                on_click=lambda e: open_create_account(page),
            ),

            ft.Container(height=10),

            ft.OutlinedButton(
                "Log in",
                width=420,
                height=55,
                style=OUTLINED_BUTTON_STYLE,
                on_click=lambda e: page.go("/login"),
            ),

            ft.Container(height=25),

            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),

                    ft.Text(
                        "Or continue with",
                        size=13,
                        color=LIGHT_GRAY,
                    ),

                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),
                ],
            ),

            ft.Container(height=20),

            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.OutlinedButton("Google", width=127, style=OUTLINED_BUTTON_STYLE),
                    ft.OutlinedButton("Apple", width=127, style=OUTLINED_BUTTON_STYLE),
                    ft.OutlinedButton("Facebook", width=127, style=OUTLINED_BUTTON_STYLE),
                ],
            ),

            ft.Container(height=25),

            ft.Text(
                spans=[
                    ft.TextSpan(
                        "By continuing you agree to our ",
                        style=ft.TextStyle(
                            color=LIGHT_GRAY,
                            size=13,
                        ),
                    ),

                    ft.TextSpan(
                        "Terms of Service",
                        style=ft.TextStyle(
                            color=TURQUOISE,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ],
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )

    welcome_card = ft.Container(
        width=520,
        padding=40,
        bgcolor=WHITE,
        border_radius=25,
        shadow=ft.BoxShadow(
            blur_radius=25,
            color="#22000000",
        ),
        content=welcome_content,
    )

    right_panel = ft.Container(
        expand=6,
        bgcolor=PANEL_GRAY,

        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[welcome_card],
        ),
    )

    view = ft.Container(
        expand=True,
        bgcolor=APP_GRAY,
        padding=20,

        content=ft.Row(
            expand=True,
            spacing=0,
            controls=[
                left_panel,
                right_panel,
            ],
        ),
    )

    page.add(view)
    page.update()


if __name__ == "__main__":
    def _standalone(page: ft.Page):
        """Arranque suelto de esta pantalla, para trabajar su diseño.

        Con `python screens/welcome_screen.py` se abre solo la
        bienvenida. Los botones no llevarán a ningún sitio: el
        enrutador vive en main.py.

        Args:
            page: la página que crea Flet.
        """
        page.window.maximized = True
        page.window.min_width = 1000
        page.window.min_height = 700
        page.update()
        screen_welcome(page)

    ft.run(_standalone, assets_dir="assets")