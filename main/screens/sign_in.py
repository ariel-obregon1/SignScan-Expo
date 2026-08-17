"""
Login screen (screens/sign_in.py).

Two-panel layout: left panel keeps its own navy-gradient branding,
right panel is styled to match screens/sign_up.py (same white card,
inputs, buttons, and back-link) so both auth screens feel consistent.
Wired to the real database (database.authenticate_user).
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database  # noqa: E402
import session  # noqa: E402

# ---- Colors (matches screens/sign_up.py palette) ----
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


def go_back_home(page):
    page.go("/")


def screen_signin(page: ft.Page):
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
        content=ft.Text("🤟", size=40),
        width=90,
        height=90,
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
    # RIGHT PANEL — Form (same card/input/button style as sign_up.py)
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

    error_text = ft.Text("", size=13, color=ERROR_RED, visible=False, text_align=ft.TextAlign.CENTER)

    forgot_password = ft.Container(
        content=ft.Text("Forgot your password?", size=14, weight=ft.FontWeight.BOLD, color=TURQUOISE),
        alignment=ft.Alignment.CENTER_RIGHT,
        padding=ft.Padding.only(top=5),
        ink=True,
    )

    def handle_login(e):
        error_text.visible = False
        error_text.update()

        ok, message, user = database.authenticate_user(email_field.value, password_field.value)
        if not ok:
            error_text.value = message
            error_text.visible = True
            error_text.update()
            return

        session.set_current_user(user)
        page.go("/dashboard")

    def social_slot(content_text: str, text_size: int):
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
            content=ft.Text(content_text, size=text_size),
            alignment=ft.Alignment.CENTER,
        )

    social_buttons = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
        controls=[
            social_slot("G", 24),
            social_slot("🍎", 22),
            social_slot("f", 26),
        ],
    )

    login_button = ft.ElevatedButton(
        "Log in",
        width=420,
        height=58,
        bgcolor=TURQUOISE,
        color=DARK_BLUE,
        on_click=handle_login,
    )

    def go_to_signup(e):
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
            error_text,
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
        # Make the window occupy the full computer screen, matching the
        # rest of the app's screens.
        page.window.maximized = True
        page.window.min_width = 1000
        page.window.min_height = 700
        page.update()
        screen_signin(page)

    ft.run(_standalone)