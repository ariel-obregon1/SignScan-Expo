import flet as ft

# =========================
# COLORS
# =========================

DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"

APP_GRAY = "#E5E7EB"
PANEL_GRAY = "#F1F5F9"

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
                on_click=lambda e: open_create_account(page),
            ),

            ft.Container(height=10),

            ft.OutlinedButton(
                "Log in",
                width=420,
                height=55,
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
                    ft.OutlinedButton("Google", width=127),
                    ft.OutlinedButton("Apple", width=127),
                    ft.OutlinedButton("Facebook", width=127),
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


if __name__ == "__main__":
    ft.run(screen_welcome)