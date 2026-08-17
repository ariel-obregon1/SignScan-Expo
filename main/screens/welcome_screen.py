import flet as ft

# =========================
# COLORS
# =========================

DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"

APP_GRAY = "#E5E7EB"

TEXT_GRAY = "#6B7A99"
LIGHT_GRAY = "#9BA8BF"

WHITE = "#FFFFFF"


# =========================
# CARDS
# =========================

def _feature_card(icon, text):
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
# NAVIGATION
# =========================

def open_create_account(page):
    page.go("/create-account")


# =========================
# SCREEN
# =========================

def screen_welcome(page):

    page.clean()

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
                    border_radius=30,
                    padding=20,

                    content=ft.Image(
                        src="logo.png",
                        width=180,
                    ),
                ),

                ft.Container(height=20),

                ft.Text(
                    "SignScan",
                    size=42,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                ),

                ft.Text(
                    "Breaking down communication barriers",
                    size=18,
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

    right_panel = ft.Container(
        expand=6,
        bgcolor=WHITE,
        padding=60,

        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[
                ft.Text(
                    "Accessible communication\nfor everyone",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=DARK_BLUE,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=15),

                ft.Text(
                    "Learn sign language with AI, connect with the community, and communicate without barriers.",
                    size=18,
                    color=TEXT_GRAY,
                    width=500,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=40),

                ft.ElevatedButton(
                    "Create free account",
                    width=350,
                    height=55,
                    bgcolor=TURQUOISE,
                    color=DARK_BLUE,
                    on_click=lambda e: open_create_account(page),
                ),

                ft.Container(height=10),

                ft.OutlinedButton(
                    "Log in",
                    width=350,
                    height=55,
                    on_click=lambda e: page.go("/login"),
                ),

                ft.Container(height=30),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=100,
                            height=1,
                            bgcolor="#D9DDE5",
                        ),

                        ft.Text(
                            "Or continue with",
                            color=LIGHT_GRAY,
                        ),

                        ft.Container(
                            width=100,
                            height=1,
                            bgcolor="#D9DDE5",
                        ),
                    ],
                ),

                ft.Container(height=20),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                    controls=[
                        ft.OutlinedButton("Google"),
                        ft.OutlinedButton("Apple"),
                        ft.OutlinedButton("Facebook"),
                    ],
                ),

                ft.Container(height=30),

                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "By continuing you agree to our ",
                            style=ft.TextStyle(
                                color=LIGHT_GRAY,
                            ),
                        ),

                        ft.TextSpan(
                            "Terms of Service",
                            style=ft.TextStyle(
                                color=TURQUOISE,
                            ),
                        ),
                    ],
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
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


if __name__ == "__main__":
    ft.run(screen_welcome)