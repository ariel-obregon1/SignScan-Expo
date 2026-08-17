# screens/sign_up.py

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database  # noqa: E402
import session  # noqa: E402


# =========================
# COLORS
# =========================

DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"

APP_GRAY = "#E5E7EB"
TEXT_GRAY = "#6B7A99"
LIGHT_GRAY = "#9BA8BF"
ERROR_RED = "#DC2626"

WHITE = "#FFFFFF"


# =========================
# NAVIGATION
# =========================

def go_back_home(page):
    page.go("/")


# =========================
# CREATE ACCOUNT SCREEN
# =========================

def screen_signup(page):

    page.title = "SignScan - Create account"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    page.controls.clear()

    # =========================
    # INPUTS
    # =========================

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

    full_name = ft.TextField(
        label="Full name",
        hint_text="Enter your name",
        **input_style
    )

    email = ft.TextField(
        label="Email address",
        hint_text="example@email.com",
        **input_style
    )

    password = ft.TextField(
        label="Password",
        hint_text="At least 8 characters",
        password=True,
        can_reveal_password=True,
        **input_style
    )

    confirm_password = ft.TextField(
        label="Confirm password",
        hint_text="Repeat your password",
        password=True,
        can_reveal_password=True,
        **input_style
    )

    error_text = ft.Text("", size=13, color=ERROR_RED, visible=False, text_align=ft.TextAlign.CENTER)

    # =========================
    # VALIDATION + REGISTRATION
    # =========================

    def show_error(message: str):
        error_text.value = message
        error_text.visible = True
        error_text.update()

    def handle_signup(e):
        error_text.visible = False
        error_text.update()

        if password.value != confirm_password.value:
            show_error("Passwords do not match")
            return

        ok, message, user = database.create_user(full_name.value, email.value, password.value)
        if not ok:
            show_error(message)
            return

        session.set_current_user(user)
        page.go("/profile")

    # =========================
    # LEFT PANEL
    # =========================

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

                ft.Container(

                    bgcolor=WHITE,
                    border_radius=25,
                    padding=20,

                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        color="#30000000",
                    ),

                    content=ft.Image(
                        src="logo.png",
                        width=170,
                    ),
                ),

                ft.Container(height=15),

                ft.Text(
                    "SignScan",
                    size=42,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),

                ft.Container(height=10),

                ft.Text(
                    "Accessible communication for everyone",
                    size=18,
                    color=TURQUOISE,
                    text_align=ft.TextAlign.CENTER,
                ),

            ]
        )
    )

    # =========================
    # SOCIAL BUTTONS
    # =========================

    social_buttons = ft.Row(

        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,

        controls=[

            ft.Container(
                width=65,
                height=65,
                border=ft.Border(
                    left=ft.BorderSide(1, "#E2E8F0"),
                    top=ft.BorderSide(1, "#E2E8F0"),
                    right=ft.BorderSide(1, "#E2E8F0"),
                    bottom=ft.BorderSide(1, "#E2E8F0"),
                ),
                border_radius=14,

                content=ft.Text(
                    "G",
                    size=24,
                ),

                alignment=ft.Alignment.CENTER,
            ),

            ft.Container(
                width=65,
                height=65,
                border=ft.Border(
                    left=ft.BorderSide(1, "#E2E8F0"),
                    top=ft.BorderSide(1, "#E2E8F0"),
                    right=ft.BorderSide(1, "#E2E8F0"),
                    bottom=ft.BorderSide(1, "#E2E8F0"),
                ),
                border_radius=14,

                content=ft.Text(
                    "🍎",
                    size=22,
                ),

                alignment=ft.Alignment.CENTER,
            ),

            ft.Container(
                width=65,
                height=65,
                border=ft.Border(
                    left=ft.BorderSide(1, "#E2E8F0"),
                    top=ft.BorderSide(1, "#E2E8F0"),
                    right=ft.BorderSide(1, "#E2E8F0"),
                    bottom=ft.BorderSide(1, "#E2E8F0"),
                ),
                border_radius=14,

                content=ft.Text(
                    "f",
                    size=26,
                ),

                alignment=ft.Alignment.CENTER,
            ),

        ]
    )

    # =========================
    # FORM
    # =========================

    form = ft.Column(

        horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        controls=[

            ft.Row(

                alignment=ft.MainAxisAlignment.START,

                controls=[

                    ft.TextButton(
                        "< Back",
                        on_click=lambda e: go_back_home(page)
                    )

                ]
            ),

            ft.Text(
                "Create account",
                size=32,
                weight=ft.FontWeight.BOLD,
                color="#0F172A",
            ),

            ft.Text(
                "Join the SignScan community",
                size=16,
                color=TEXT_GRAY,
            ),

            ft.Container(height=15),

            social_buttons,

            ft.Container(height=15),

            ft.Row(

                alignment=ft.MainAxisAlignment.CENTER,

                controls=[

                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),

                    ft.Text(
                        "Or with email",
                        size=13,
                        color=LIGHT_GRAY,
                    ),

                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),

                ]
            ),

            ft.Container(height=15),

            full_name,

            ft.Container(height=8),

            email,

            ft.Container(height=8),

            password,

            ft.Container(height=8),

            confirm_password,

            ft.Container(height=10),

            error_text,

            ft.Container(height=5),

            ft.ElevatedButton(

                "Create account",

                width=420,
                height=58,

                bgcolor=TURQUOISE,
                color=DARK_BLUE,

                on_click=handle_signup,

            ),

            ft.Container(height=15),

            ft.Row(

                alignment=ft.MainAxisAlignment.CENTER,

                controls=[

                    ft.Text(
                        "Already have an account?",
                        color=TEXT_GRAY,
                    ),

                    ft.TextButton(

                        "Log in",

                        on_click=lambda e: page.go("/login"),

                    ),

                ]
            ),

        ]
    )

    # =========================
    # RIGHT PANEL
    # =========================

    right_panel = ft.Container(

        expand=6,
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

                    shadow=ft.BoxShadow(
                        blur_radius=25,
                        color="#22000000",
                    ),

                    content=form,

                )

            ]
        )
    )

    # =========================
    # FINAL VIEW
    # =========================

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

            ]

        )
    )

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
        screen_signup(page)

    ft.run(_standalone)