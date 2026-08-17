"""
Profile setup screen (screens/personalize_profile.py).

White card centered over a navy background: avatar with a camera
button overlay, username field, selectable emoji avatar grid, and a
"Save and continue" button. Reads/writes session.current_user.
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database  # noqa: E402
import session  # noqa: E402

# ---- Colors ----
NAVY_BG = "#002060"
TURQUOISE = "#40E0D0"
GOLD = "#FFD700"
NAVY_TEXT = "#002060"
TEXT_GRAY = "#6B7A99"
WHITE_TEXT = ft.Colors.with_opacity(0.6, ft.Colors.WHITE)
INPUT_BORDER = "#E5E7EB"
AVATAR_BG = "#F9FAFB"

AVATAR_EMOJIS = [
    "🤟", "👋", "🙌", "👏", "🤲", "🌟", "🦋", "🌈", "🐬", "🦁",
    "🐧", "🦊", "🌺", "🍀", "⭐", "💎", "🚀", "🏆", "❤️", "🎵",
]


def screen_personalizeprofile(page: ft.Page):
    page.title = "SignScan - Your profile"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    current_name = session.current_user.get("name") or ""
    selected_avatar = {"value": session.current_user.get("avatar") or "🌟"}
    # Tracks a locally-picked photo path, if any. When set, it takes
    # visual priority over the emoji avatar.
    selected_photo = {"path": session.current_user.get("photo")}

    avatar_preview = ft.Text(selected_avatar["value"], size=50)
    avatar_buttons = {}

    # ================================================================
    # File picker (profile photo)
    # ================================================================
    def build_avatar_content():
        """Returns the control that should sit inside avatar_circle:
        the chosen photo if one was picked, otherwise the emoji."""
        if selected_photo["path"]:
            return ft.Image(
                src=selected_photo["path"],
                width=110,
                height=110,
                fit=ft.BoxFit.COVER,
                border_radius=999,
            )
        return avatar_preview

    async def pick_photo(e):
        # In current Flet, FilePicker.pick_files() is awaited directly and
        # returns the picked files - no page.overlay registration and no
        # on_result callback needed.
        files = await ft.FilePicker().pick_files(
            dialog_title="Choose a profile photo",
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        if not files:
            return
        selected_photo["path"] = files[0].path
        avatar_circle.content = build_avatar_content()
        avatar_circle.update()

    # ================================================================
    # Header (over navy background, outside the white card)
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
            ft.Text("Your profile", size=25, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Text("Customize how others see you", size=15, color=WHITE_TEXT),
                padding=ft.Padding.only(top=2.5),
            ),
            ft.Container(content=close_button, padding=ft.Padding.only(top=15)),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )
    header_container = ft.Container(content=header, padding=ft.Padding.only(bottom=25))

    # ================================================================
    # Profile photo / large avatar + overlaid camera button
    # ================================================================
    avatar_circle = ft.Container(
        content=build_avatar_content(),
        width=110,
        height=110,
        bgcolor=NAVY_BG,
        border=ft.Border.all(3.5, TURQUOISE),
        border_radius=999,
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    camera_button = ft.Container(
        content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=18, color=NAVY_TEXT),
        width=38,
        height=38,
        bgcolor=GOLD,
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
                         width=110, height=110),
        ],
        width=110,
        height=110,
    )

    photo_section = ft.Column(
        controls=[
            avatar_stack,
            ft.Container(
                content=ft.Text("Tap the camera icon to change your photo", size=11, color=TEXT_GRAY,
                                 text_align=ft.TextAlign.CENTER),
                padding=ft.Padding.only(top=10),
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # ================================================================
    # Field: Username
    # ================================================================
    username_field = ft.TextField(
        value=current_name,
        text_style=ft.TextStyle(size=17.5, color=NAVY_TEXT),
        border_color=INPUT_BORDER,
        border_width=0.9,
        border_radius=16.5,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=15),
        cursor_color=TURQUOISE,
        focused_border_color=TURQUOISE,
    )

    username_section = ft.Column(
        controls=[
            ft.Text("Username", size=15, weight=ft.FontWeight.BOLD, color=NAVY_TEXT),
            username_field,
        ],
        spacing=7.5,
    )

    # ================================================================
    # Emoji avatar grid
    # ================================================================
    def style_avatar_button(container: ft.Container, is_selected: bool):
        if is_selected:
            container.bgcolor = ft.Colors.with_opacity(0.1, TURQUOISE)
            container.border = ft.Border.all(2, TURQUOISE)
        else:
            container.bgcolor = AVATAR_BG
            container.border = ft.Border.all(1.8, ft.Colors.TRANSPARENT)

    def select_avatar(emoji: str):
        def handler(e):
            # Picking an emoji clears any previously chosen photo so the
            # emoji is what actually shows in the big avatar circle.
            selected_avatar["value"] = emoji
            selected_photo["path"] = None
            avatar_preview.value = emoji
            avatar_circle.content = build_avatar_content()
            avatar_circle.update()
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
            ft.Text("Choose your avatar", size=15, weight=ft.FontWeight.BOLD, color=NAVY_TEXT),
            ft.Container(content=avatar_grid, padding=ft.Padding.only(top=10)),
        ],
        spacing=0,
    )

    # ================================================================
    # "Save and continue" button
    # ================================================================
    def save_and_continue(e):
        user_id = session.current_user.get("id")
        if user_id is not None:
            try:
                # If your database.update_profile supports a photo/avatar
                # path column, this will persist it too. Falls back to
                # name/avatar only if the extra kwarg isn't accepted.
                database.update_profile(
                    user_id,
                    name=username_field.value,
                    avatar=selected_avatar["value"],
                    photo=selected_photo["path"],
                )
            except TypeError:
                database.update_profile(user_id, name=username_field.value, avatar=selected_avatar["value"])
        session.current_user["name"] = username_field.value
        session.current_user["avatar"] = selected_avatar["value"]
        session.current_user["photo"] = selected_photo["path"]
        page.go("/dashboard")

    save_button = ft.Container(
        content=ft.Text("Save and continue 🤟", size=17.5, color=NAVY_TEXT, weight=ft.FontWeight.W_600),
        alignment=ft.Alignment.CENTER,
        bgcolor=TURQUOISE,
        border_radius=16.5,
        padding=ft.Padding.symmetric(vertical=17),
        width=float("inf"),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                             color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        on_click=save_and_continue,
        ink=True,
    )

    # ================================================================
    # White card
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

    # The outer container fills the whole page (expand=True) and the
    # navy background stretches with it, so maximizing/full-screening
    # the window is enough to make this occupy the whole computer
    # screen while the white card keeps its original centered size.
    screen = ft.Container(
        content=ft.Column(
            controls=[header_container, card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        bgcolor=NAVY_BG,
        padding=ft.Padding.symmetric(horizontal=30, vertical=50),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    page.add(
        ft.Row(controls=[screen], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    )


if __name__ == "__main__":
    def _standalone(page: ft.Page):
        # Make the window occupy the full computer screen.
        page.window.maximized = True
        # If you prefer true edge-to-edge full screen (no title bar/
        # window controls), use this instead:
        # page.window.full_screen = True
        page.window.min_width = 900
        page.window.min_height = 700
        page.update()
        screen_personalizeprofile(page)

    ft.run(_standalone)