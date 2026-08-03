"""
Pantalla de configuración de perfil (screens/profile_setup_screen.py).

Tarjeta blanca centrada sobre fondo navy: foto/avatar con botón de
cámara superpuesto, campo de nombre de usuario, grilla de avatares de
emoji seleccionables, y botón "Guardar y continuar".
"""

import flet as ft

# ---- Paleta de colores (tomada del CSS) ----
COLOR_BG_NAVY = "#002060"          # rgba(0, 32, 96, 1)
COLOR_TURQUOISE = "#40E0D0"
COLOR_GOLD = "#FFD700"
COLOR_NAVY_TEXT = "#002060"
COLOR_GRAY_TEXT = "#6B7A99"        # rgba(107, 122, 153, 1)
COLOR_WHITE_TEXT = ft.Colors.with_opacity(0.6, ft.Colors.WHITE)
COLOR_INPUT_BORDER = "#E5E7EB"     # rgba(229, 231, 235, 1)
COLOR_AVATAR_BG = "#F9FAFB"        # rgba(249, 250, 251, 1)

AVATAR_EMOJIS = [
    "🤟", "👋", "🙌", "👏", "🤲", "🌟", "🦋", "🌈", "🐬", "🦁",
    "🐧", "🦊", "🌺", "🍀", "⭐", "💎", "🚀", "🏆", "❤️", "🎵",
]


def screen_personalizeprofile(page: ft.Page):
    page.title = "SignScan - Tu perfil"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    page.window.width = 900
    page.window.height = 900
    page.window.min_width = 700
    page.window.min_height = 750
    page.window.resizable = True
    page.run_task(page.window.center)

    selected_avatar = {"value": "🌟"}
    avatar_preview = ft.Text(selected_avatar["value"], size=50)
    avatar_buttons = {}

    # ================================================================
    # Header (sobre fondo navy, fuera de la tarjeta blanca)
    # ================================================================
    def close_setup(e):
        page.go("/dashboard")

    close_button = ft.Container(
        content=ft.Icon(ft.Icons.CLOSE, size=20, color=ft.Colors.WHITE),
        width=45,
        height=45,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
        border_radius=16.5,
        alignment=ft.Alignment.CENTER,
        on_click=close_setup,
        ink=True,
    )

    header = ft.Column(
        controls=[
            ft.Text("Tu perfil", size=25, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Text("Personaliza cómo te verán", size=15, color=COLOR_WHITE_TEXT),
                padding=ft.Padding.only(top=2.5),
            ),
            ft.Container(content=close_button, padding=ft.Padding.only(top=15)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )
    header_container = ft.Container(content=header, padding=ft.Padding.only(bottom=25))

    # ================================================================
    # Foto de perfil / avatar grande + botón de cámara superpuesto
    # ================================================================
    def pick_photo(e):
        # TODO: conectar selector de archivo / cámara real
        print("Cambiar foto")

    avatar_circle = ft.Container(
        content=avatar_preview,
        width=110,
        height=110,
        bgcolor=COLOR_BG_NAVY,
        border=ft.Border.all(3.5, COLOR_TURQUOISE),
        border_radius=999,
        alignment=ft.Alignment.CENTER,
    )

    camera_button = ft.Container(
        content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=18, color=COLOR_NAVY_TEXT),
        width=38,
        height=38,
        bgcolor=COLOR_GOLD,
        border_radius=999,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                             color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
        on_click=pick_photo,
        ink=True,
    )

    avatar_stack = ft.Stack(
        controls=[
            avatar_circle,
            ft.Container(content=camera_button, alignment=ft.Alignment.BOTTOM_RIGHT,
                         margin=ft.Margin.only(top=110 - 38, left=110 - 38)),
        ],
        width=110,
        height=110,
    )

    photo_section = ft.Column(
        controls=[
            avatar_stack,
            ft.Container(
                content=ft.Text("Toca la cámara para cambiar foto", size=11, color=COLOR_GRAY_TEXT,
                                 text_align=ft.TextAlign.CENTER),
                padding=ft.Padding.only(top=10),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # ================================================================
    # Campo: Nombre de usuario
    # ================================================================
    username_field = ft.TextField(
        value="Usuario Google",
        text_style=ft.TextStyle(size=17.5, color=COLOR_NAVY_TEXT),
        border_color=COLOR_INPUT_BORDER,
        border_width=0.9,
        border_radius=16.5,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=15),
        cursor_color=COLOR_TURQUOISE,
        focused_border_color=COLOR_TURQUOISE,
    )

    username_section = ft.Column(
        controls=[
            ft.Text("Nombre de usuario", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
            username_field,
        ],
        spacing=7.5,
    )

    # ================================================================
    # Grilla de avatares de emoji
    # ================================================================
    def style_avatar_button(container: ft.Container, is_selected: bool):
        if is_selected:
            container.bgcolor = ft.Colors.with_opacity(0.1, COLOR_TURQUOISE)
            container.border = ft.Border.all(2, COLOR_TURQUOISE)
        else:
            container.bgcolor = COLOR_AVATAR_BG
            container.border = ft.Border.all(1.8, ft.Colors.TRANSPARENT)

    def select_avatar(emoji: str):
        def handler(e):
            selected_avatar["value"] = emoji
            avatar_preview.value = emoji
            avatar_preview.update()
            for em, btn in avatar_buttons.items():
                style_avatar_button(btn, em == emoji)
                btn.update()
        return handler

    avatar_grid_controls = []
    for emoji in AVATAR_EMOJIS:
        btn = ft.Container(
            content=ft.Text(emoji, size=25),
            width=52,
            height=52,
            border_radius=999,
            alignment=ft.Alignment.CENTER,
            ink=True,
            on_click=select_avatar(emoji),
        )
        style_avatar_button(btn, emoji == selected_avatar["value"])
        avatar_buttons[emoji] = btn
        avatar_grid_controls.append(btn)

    avatar_grid = ft.Row(
        controls=avatar_grid_controls,
        wrap=True,
        spacing=10,
        run_spacing=10,
    )

    avatar_section = ft.Column(
        controls=[
            ft.Text("Elige tu avatar", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
            ft.Container(content=avatar_grid, padding=ft.Padding.only(top=10)),
        ],
        spacing=0,
    )

    # ================================================================
    # Botón "Guardar y continuar"
    # ================================================================
    def save_and_continue(e):
        # TODO: persistir username_field.value y selected_avatar["value"]
        print("Guardando perfil:", username_field.value, selected_avatar["value"])
        page.go("/inicio")

    save_button = ft.Container(
        content=ft.Text("Guardar y continuar 🤟", size=17.5, color=COLOR_NAVY_TEXT, weight=ft.FontWeight.W_600),
        alignment=ft.Alignment.CENTER,
        bgcolor=COLOR_TURQUOISE,
        border_radius=16.5,
        padding=ft.Padding.symmetric(vertical=17),
        width=float("inf"),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                             color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        on_click=save_and_continue,
        ink=True,
    )

    # ================================================================
    # Tarjeta blanca
    # ================================================================
    card = ft.Container(
        content=ft.Column(
            controls=[
                photo_section,
                ft.Container(content=username_section, padding=ft.Padding.only(top=25)),
                ft.Container(content=avatar_section, padding=ft.Padding.symmetric(vertical=20)),
                save_button,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=480,
        padding=30,
        bgcolor=ft.Colors.WHITE,
        border_radius=30,
        shadow=ft.BoxShadow(spread_radius=2, blur_radius=50,
                             color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK), offset=ft.Offset(0, 25)),
    )

    screen = ft.Container(
        content=ft.Column(
            controls=[header_container, card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        bgcolor=COLOR_BG_NAVY,
        padding=ft.Padding.symmetric(horizontal=30, vertical=50),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    page.add(
        ft.Row(controls=[screen], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )


if __name__ == "__main__":
    ft.run(screen_personalizeprofile)