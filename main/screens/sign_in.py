"""
Pantalla de inicio de sesión — screens/sign_in.py

Ruta "/login". Comprueba las credenciales contra la base de datos real
(database.authenticate_user), y si son correctas guarda al usuario en la
sesión y salta al dashboard.

Estructura: dos paneles.
    - Panel izquierdo (40%): marca de la app sobre un degradado azul.
    - Panel derecho (60%): tarjeta blanca con el formulario, con el
      mismo estilo que screens/sign_up.py para que las dos pantallas de
      autenticación se sientan iguales.

Los botones de redes sociales (Google, Apple, Facebook) son decorativos:
hoy no hacen nada, son cuadros sin evento de clic.
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database  # noqa: E402
import session  # noqa: E402

# ---- Colores (la misma paleta que screens/sign_up.py) ----
DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"

APP_GRAY = "#E5E7EB"
TEXT_GRAY = "#6B7A99"
LIGHT_GRAY = "#9BA8BF"
ERROR_RED = "#DC2626"

WHITE = "#FFFFFF"

LEFT_PANEL_WEIGHT = 4
RIGHT_PANEL_WEIGHT = 6

# Same rounded corners as the rest of the app's cards/inputs
# (14-20px radius), instead of Flet's default, squarer button shape.
PRIMARY_BUTTON_STYLE = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14))


def go_back_home(page):
    """Vuelve a la pantalla de bienvenida.

    La usa el enlace "< Back" de la esquina superior del formulario.

    Args:
        page: la página de Flet.
    """
    page.go("/")


def screen_signin(page: ft.Page):
    """Dibuja la pantalla de inicio de sesión sobre `page`.

    Además de montar el formulario, configura la tipografía (fuente
    Nunito descargada de Google Fonts) y el color de fondo de la página.

    Args:
        page: la página de Flet sobre la que se dibuja.

    Nota: la fuente se descarga de internet. Sin conexión, Flet usa la
    tipografía por defecto y la pantalla se ve igual de funcional.
    """
    page.title = "SignScan - Log in"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    # ================================================================
    # LEFT PANEL — Branding (kept distinct: navy gradient)
    # ================================================================
    brand_logo = ft.Container(
        content=ft.Image(
            src="logo.png",
            width=170,
        ),
        width=170,
        height=170,
        bgcolor=WHITE,
        border_radius=20,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=25,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 8)),
        )

    left_panel = ft.Container(
        expand=LEFT_PANEL_WEIGHT,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[MAIN_BLUE, "#004A6B", DARK_BLUE],
        ),
        padding=40,
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                brand_logo,
                ft.Container(height=15),
                ft.Text("SignScan", size=37.5, color=WHITE, weight=ft.FontWeight.W_600),
                ft.Container(height=10),
                ft.Text(
                    "Accessible communication for everyone",
                    size=17.5,
                    weight=ft.FontWeight.BOLD,
                    color=TURQUOISE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    # ================================================================
    # PANEL DERECHO — Formulario (misma tarjeta, campos y botones que
    # sign_up.py, para que las dos pantallas se sientan iguales)
    # ================================================================
    input_style = {
        "width": 420,
        "height": 52,
        "filled": True,
        "bgcolor": WHITE,
        "border_color": "#CBD5E1",
        "focused_border_color": TURQUOISE,
        "color": "#0F172A",
        "text_size": 15,
        "border_radius": 14,
    }

    email_field = ft.TextField(
        label="Email address",
        hint_text="example@email.com",
        **input_style,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        **input_style,
    )

    # A small alert box instead of bare colored text - reads more like
    # a real form error and less like text that just happens to be red.
    error_text = ft.Text("", size=13, color=ERROR_RED, text_align=ft.TextAlign.CENTER)
    error_box = ft.Container(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=16, color=ERROR_RED), error_text],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        bgcolor=ft.Colors.with_opacity(0.08, ERROR_RED),
        border_radius=10,
        visible=False,
    )

    forgot_password = ft.Container(
        content=ft.Text("Forgot your password?", size=14, weight=ft.FontWeight.BOLD, color=TURQUOISE),
        alignment=ft.Alignment.CENTER_RIGHT,
        padding=ft.Padding.only(top=5),
        ink=True,
    )

    def handle_login(e):
        """Valida las credenciales y entra a la app.

        Primero esconde el error anterior (para que no quede un mensaje
        viejo si el usuario reintenta), consulta la base de datos y:
            - si falla, muestra el mensaje que devuelve la consulta y se
              queda en la pantalla;
            - si acierta, guarda al usuario en la sesión y navega al
              dashboard.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        error_box.visible = False
        error_box.update()

        ok, message, user = database.authenticate_user(email_field.value, password_field.value)
        if not ok:
            error_text.value = message
            error_box.visible = True
            error_box.update()
            return

        session.set_current_user(user)
        page.go("/dashboard")

    def social_slot(content_text: str, text_size: int, text_color: str | None = None):
        """Construye uno de los botones cuadrados de redes sociales.

        Son decorativos: no tienen on_click, solo el marco con la letra
        o el emoji dentro.

        Args:
            content_text: texto o emoji a mostrar ("G", la manzana...).
            text_size: tamaño de fuente, para que los tres se vean
                ópticamente iguales pese a ser símbolos distintos.
            text_color: color del texto. None deja el color por defecto.

        Returns:
            El contenedor de Flet ya montado.
        """
        return ft.Container(
            width=65,
            height=65,
            border=ft.Border(
                left=ft.BorderSide(1, "#E2E8F0"),
                top=ft.BorderSide(1, "#E2E8F0"),
                right=ft.BorderSide(1, "#E2E8F0"),
                bottom=ft.BorderSide(1, "#E2E8F0"),
            ),
            border_radius=14,
            content=ft.Text(content_text, size=text_size, weight=ft.FontWeight.BOLD, color=text_color),
            alignment=ft.Alignment.CENTER,
            ink=True,
        )

    social_buttons = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
        controls=[
            social_slot("G", 24, "#4285F4"),
            social_slot("🍎", 22),
            social_slot("f", 26, "#1877F2"),
        ],
    )

    login_button = ft.ElevatedButton(
        "Log in",
        width=420,
        height=58,
        bgcolor=TURQUOISE,
        color=DARK_BLUE,
        style=PRIMARY_BUTTON_STYLE,
        on_click=handle_login,
    )

    def go_to_signup(e):
        """Lleva a la pantalla de crear cuenta.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        page.go("/create-account")

    form = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[ft.TextButton("< Back", on_click=lambda e: go_back_home(page))],
            ),
            ft.Text("Welcome back", size=32, weight=ft.FontWeight.BOLD, color="#0F172A"),
            ft.Text("Log in to continue learning", size=16, color=TEXT_GRAY),
            ft.Container(height=15),
            social_buttons,
            ft.Container(height=15),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=130, height=1, bgcolor="#E5E7EB"),
                    ft.Text("Or with email", size=13, color=LIGHT_GRAY),
                    ft.Container(width=130, height=1, bgcolor="#E5E7EB"),
                ],
            ),
            ft.Container(height=15),
            email_field,
            ft.Container(height=8),
            password_field,
            forgot_password,
            ft.Container(height=10),
            error_box,
            ft.Container(height=5),
            login_button,
            ft.Container(height=15),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("Don't have an account?", color=TEXT_GRAY),
                    ft.TextButton("Create account", on_click=go_to_signup),
                ],
            ),
        ],
    )

    right_panel = ft.Container(
        expand=RIGHT_PANEL_WEIGHT,
        bgcolor="#F1F5F9",
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=520,
                    padding=30,
                    bgcolor=WHITE,
                    border_radius=25,
                    shadow=ft.BoxShadow(blur_radius=25, color="#22000000"),
                    content=form,
                ),
            ],
        ),
    )

    # ================================================================
    # MAIN LAYOUT
    # ================================================================
    view = ft.Container(
        expand=True,
        bgcolor=APP_GRAY,
        padding=20,
        content=ft.Row(
            expand=True,
            spacing=0,
            controls=[left_panel, right_panel],
        ),
    )

    page.controls.clear()
    page.add(view)
    page.update()


if __name__ == "__main__":
    def _standalone(page: ft.Page):
        """Arranque suelto de esta pantalla, para trabajar su diseño.

        Ejecutar `python screens/sign_in.py` abre solo el login, con la
        ventana maximizada como en el resto de la app. Ojo: al no pasar
        por main.py no hay enrutador, así que los botones que navegan a
        otras pantallas no harán nada.

        Args:
            page: la página que crea Flet.
        """
        # Ventana maximizada, igual que el resto de pantallas de la app.
        page.window.maximized = True
        page.window.min_width = 1000
        page.window.min_height = 700
        page.update()
        screen_signin(page)

    ft.run(_standalone, assets_dir="assets")