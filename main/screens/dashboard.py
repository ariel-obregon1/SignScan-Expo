"""
Pantalla de inicio / dashboard (screens/dashboard.py).

Sidebar de navegación + saludo + tarjetas de racha/progreso + grid de
módulos. Muestra el nombre/correo/avatar del usuario logueado
(session.current_user) en vez de datos de ejemplo.
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import session  # noqa: E402

# ---- Paleta de colores ----
COLOR_SIDEBAR = "#002060"
COLOR_SIDEBAR_DARKER = "#001845"
COLOR_BG_MAIN = "#EEF2F7"
COLOR_TURQUOISE = "#40E0D0"
COLOR_GOLD = "#FFD700"
COLOR_PURPLE = "#8B5CF6"
COLOR_RED = "#DC2626"
COLOR_NAVY_TEXT = "#002060"
COLOR_GRAY_TEXT = "#6B7A99"
COLOR_LIGHT_GRAY_TEXT = "#9BA8BF"
COLOR_CARD_BORDER = "#F3F4F6"
COLOR_ROW_BG = "#F8FAFB"
COLOR_PROGRESS_TRACK = "#E5E7EB"

SIDEBAR_WIDTH = 260


def screen_dashboard(page: ft.Page):
    page.title = "SignScan - Inicio"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    user_name = session.current_user.get("name") or "Usuario"
    user_email = session.current_user.get("email") or ""
    user_avatar = session.current_user.get("avatar") or "🌟"

    # ================================================================
    # SIDEBAR
    # ================================================================
    def nav_button(icon_name: str, label: str, active: bool = False, route: str | None = None):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icon_name,
                        size=20,
                        color=COLOR_NAVY_TEXT if active else ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    ),
                    ft.Text(
                        label,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_NAVY_TEXT if active else ft.Colors.WHITE,
                    ),
                ],
                spacing=15,
            ),
            padding=ft.Padding.symmetric(horizontal=20, vertical=13),
            bgcolor=COLOR_TURQUOISE if active else None,
            border_radius=20,
            margin=ft.Margin.only(top=5),
            ink=True,
            on_click=(lambda e: page.go(route)) if route else None,
        )

    logo_row = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("🤟", size=20),
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=16.5,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text("SignScan", size=20, color=ft.Colors.WHITE),
            ],
            spacing=12,
        ),
        padding=20,
        border=ft.Border(bottom=ft.BorderSide(0.9, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
    )

    user_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(user_avatar, size=16),
                    width=44,
                    height=44,
                    bgcolor=COLOR_SIDEBAR_DARKER,
                    border=ft.Border.all(1.8, COLOR_TURQUOISE),
                    border_radius=999,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    controls=[
                        ft.Text(user_name, size=14, color=ft.Colors.WHITE),
                        ft.Text(user_email, size=11, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                    ],
                    spacing=2,
                ),
            ],
            spacing=12,
        ),
        padding=12,
        margin=ft.Margin.only(left=15, right=15, top=20),
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_radius=20,
    )

    nav_column = ft.Column(
        controls=[
            nav_button(ft.Icons.HOME_ROUNDED, "Inicio", active=True),
            nav_button(ft.Icons.MENU_BOOK_ROUNDED, "Aprender", route="/aprender"),
            nav_button(ft.Icons.CAMERA_ALT_ROUNDED, "Escanear", route="/escanear"),
            nav_button(ft.Icons.GROUPS_ROUNDED, "Comunidad", route="/comunidad"),
            nav_button(ft.Icons.VIDEOCAM_ROUNDED, "Video", route="/video"),
            nav_button(ft.Icons.PERSON_ROUNDED, "Perfil", route="/perfil"),
        ],
        spacing=0,
    )
    nav_container = ft.Container(content=nav_column, padding=ft.Padding.symmetric(horizontal=15, vertical=20))

    def handle_logout(e):
        session.clear_current_user()
        page.go("/")

    logout_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=ft.Colors.WHITE),
                ft.Text("Cerrar sesión", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            spacing=15,
        ),
        padding=ft.Padding.symmetric(horizontal=20, vertical=13),
        border_radius=20,
        ink=True,
        on_click=handle_logout,
    )
    logout_container = ft.Container(content=logout_button, padding=ft.Padding.only(left=15, right=15, bottom=30))

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                logo_row,
                user_card,
                nav_container,
                ft.Container(expand=True),
                logout_container,
            ],
            spacing=0,
            expand=True,
        ),
        width=SIDEBAR_WIDTH,
        bgcolor=COLOR_SIDEBAR,
    )

    # ================================================================
    # MAIN CONTENT — Header (saludo + racha)
    # ================================================================
    greeting_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(f"Hola, {user_name}! 👋", size=30, color=COLOR_NAVY_TEXT),
                        ft.Text("Continúa aprendiendo hoy", size=17.5, color=COLOR_GRAY_TEXT),
                    ],
                    spacing=3,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=16, color=COLOR_NAVY_TEXT),
                            ft.Text("3", size=12, color=COLOR_NAVY_TEXT),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                    bgcolor=COLOR_GOLD,
                    border_radius=999,
                    border=ft.Border.all(0.9, COLOR_CARD_BORDER),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=ft.Padding.only(left=30, right=30, top=40, bottom=25),
        bgcolor=ft.Colors.WHITE,
        border=ft.Border(bottom=ft.BorderSide(0.9, COLOR_CARD_BORDER)),
    )

    # ================================================================
    # Tarjetas de estadísticas
    # ================================================================
    def stat_card(emoji: str, value: str, label: str):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(emoji, size=30),
                    ft.Text(value, size=30, color=COLOR_NAVY_TEXT),
                    ft.Text(label, size=15, color=COLOR_GRAY_TEXT),
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=25),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(0.9, COLOR_CARD_BORDER),
            border_radius=20,
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

    stats_row = ft.Row(
        controls=[
            stat_card("🔥", "1", "días activo"),
            stat_card("🤟", "0", "aprendidas"),
            stat_card("⭐", "Básico", "nivel"),
        ],
        spacing=20,
    )

    # ================================================================
    # Marcador general (barra de progreso grande)
    # ================================================================
    def simple_progress_bar(percent: int, color: str, height: int = 8):
        filled = max(percent, 0)
        empty = max(100 - filled, 0)
        bar_controls = []
        if filled > 0:
            bar_controls.append(ft.Container(bgcolor=color, border_radius=999, expand=filled))
        if empty > 0:
            bar_controls.append(ft.Container(expand=empty))
        return ft.Container(
            content=ft.Row(controls=bar_controls, spacing=0, expand=True) if bar_controls else None,
            bgcolor=COLOR_PROGRESS_TRACK,
            border_radius=999,
            height=height,
        )

    marcador_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text("🌟", size=17.5),
                                    width=40,
                                    height=40,
                                    bgcolor=COLOR_GOLD,
                                    border_radius=999,
                                    alignment=ft.Alignment.CENTER,
                                ),
                                ft.Text("Marcador", size=17.5, color=COLOR_NAVY_TEXT),
                            ],
                            spacing=15,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("0/259", size=15, color=COLOR_LIGHT_GRAY_TEXT),
                                ft.Text("0%", size=10, color=COLOR_TURQUOISE),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                simple_progress_bar(0, COLOR_TURQUOISE),
            ],
            spacing=15,
        ),
        padding=ft.Padding.symmetric(horizontal=20, vertical=17.5),
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(0.9, COLOR_CARD_BORDER),
        border_radius=20,
    )

    def category_label(text: str):
        return ft.Text(text, size=10, color=COLOR_GRAY_TEXT)

    def topic_row(emoji: str, name: str, percent: int, percent_color: str):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(emoji, size=20),
                    ft.Column(
                        controls=[
                            ft.Text(name, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
                            simple_progress_bar(percent, percent_color, height=6),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Text(f"{percent}%", size=10, color=percent_color),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=15, vertical=12.5),
            bgcolor=COLOR_ROW_BG,
            border_radius=16.5,
        )

    def topic_row_stacked(emoji: str, name: str, percent: int, percent_color: str):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(emoji, size=25),
                    ft.Text(name, size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT,
                            text_align=ft.TextAlign.CENTER),
                    simple_progress_bar(percent, percent_color, height=6),
                    ft.Text(f"{percent}%", size=10, color=percent_color),
                ],
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=12.5),
            bgcolor=COLOR_ROW_BG,
            border_radius=16.5,
            expand=True,
        )

    basico_section = ft.Column(
        controls=[
            category_label("🌱 BÁSICO"),
            ft.Column(
                controls=[
                    topic_row("🔤", "Abecedario", 0, COLOR_TURQUOISE),
                    topic_row("👋", "Saludos", 0, COLOR_TURQUOISE),
                    topic_row("🔢", "Números", 0, COLOR_TURQUOISE),
                    topic_row("🎨", "Colores", 0, COLOR_TURQUOISE),
                ],
                spacing=10,
            ),
        ],
        spacing=10,
    )

    intermedio_section = ft.Column(
        controls=[
            category_label("🚀 INTERMEDIO"),
            ft.Column(
                controls=[
                    topic_row("👨‍👩‍👧", "Familia", 0, COLOR_PURPLE),
                    topic_row("🍎", "Comida", 0, COLOR_PURPLE),
                ],
                spacing=10,
            ),
        ],
        spacing=10,
    )

    dificil_section = ft.Column(
        controls=[
            category_label("🔥 DIFÍCIL"),
            ft.Row(
                controls=[
                    topic_row_stacked("😊", "Emociones", 0, COLOR_RED),
                    topic_row_stacked("🐾", "Animales", 0, COLOR_RED),
                    topic_row_stacked("🏅", "Deportes", 0, COLOR_RED),
                ],
                spacing=15,
            ),
        ],
        spacing=10,
    )

    progress_card = ft.Container(
        content=ft.Column(
            controls=[marcador_card, basico_section, intermedio_section, dificil_section],
            spacing=25,
        ),
        padding=ft.Padding.only(top=25),
    )

    # ================================================================
    # Módulos
    # ================================================================
    def module_card(emoji: str, title: str, subtitle: str, bgcolor, text_color, route: str | None = None):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(emoji, size=25),
                        width=44,
                        height=44,
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=16.5,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(title, size=17.5, color=text_color),
                    ft.Text(subtitle, size=11, weight=ft.FontWeight.BOLD, color=text_color,
                            opacity=0.7),
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=25,
            bgcolor=bgcolor,
            border_radius=20,
            expand=1,
            ink=True,
            on_click=(lambda e: page.go(route)) if route else None,
        )

    modulos_grid = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    module_card("📷", "Escanear Señas", "Detecta señas en tiempo real con IA",
                                COLOR_TURQUOISE, COLOR_NAVY_TEXT, route="/escanear"),
                    module_card("📹", "Video Chat", "Videollamadas con interpretación",
                                COLOR_SIDEBAR, ft.Colors.WHITE),
                ],
                spacing=15,
            ),
            ft.Row(
                controls=[
                    module_card("📖", "Aprender Señas", "Lecciones interactivas de señas",
                                COLOR_GOLD, COLOR_NAVY_TEXT),
                    module_card("👥", "Comunidad", "Conecta con personas sordas",
                                ft.Colors.WHITE, COLOR_NAVY_TEXT),
                ],
                spacing=15,
            ),
        ],
        spacing=15,
    )

    modulos_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Módulos", size=22.5, color=COLOR_NAVY_TEXT),
                ft.Container(content=modulos_grid, padding=ft.Padding.only(top=15)),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(top=25),
    )

    body_content = ft.Container(
        content=ft.Column(
            controls=[stats_row, progress_card, modulos_section],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding.only(left=30, right=30, top=30, bottom=50),
        expand=True,
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[greeting_header, body_content],
            spacing=0,
            expand=True,
        ),
        bgcolor=COLOR_BG_MAIN,
        expand=True,
    )

    page.add(
        ft.Row(
            controls=[sidebar, main_content],
            spacing=0,
            expand=True,
        )
    )


if __name__ == "__main__":
    def _standalone(page: ft.Page):
        page.window.width = 1440
        page.window.height = 900
        page.run_task(page.window.center)
        screen_dashboard(page)

    ft.run(_standalone)