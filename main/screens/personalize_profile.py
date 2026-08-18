"""
Profile setup screen (screens/personalize_profile.py).

White card centered over a navy background: avatar with a camera
button overlay, username field, selectable emoji avatar grid, and a
"Save and continue" button. Reads/writes session.current_user, and
persists to the database so the photo/avatar show up everywhere else
in the app (sidebar, community posts, etc. via
session.get_avatar_control()).
"""

import os
import shutil
import sys
import uuid

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
DIVIDER_COLOR = "#F0F2F5"

AVATAR_EMOJIS = [
    "🤟", "👋", "🙌", "👏", "🤲", "🌟", "🦋", "🌈", "🐬", "🦁",
    "🐧", "🦊", "🌺", "🍀", "⭐", "💎", "🚀", "🏆", "❤️", "🎵",
]

CARD_WIDTH = 500
AVATAR_OUTER_SIZE = 118
AVATAR_INNER_SIZE = 110

# main.py runs the app with ft.run(main, assets_dir="assets") - that's
# what lets screens reference "logo.png" as a plain relative src and
# have Flet serve it correctly. User-picked photos need to live under
# that same assets folder for the same reason: an absolute filesystem
# path from the file picker may not render (or may stop working the
# moment the original file is moved), while a path relative to
# assets_dir is exactly what Flet's asset server and ft.Image expect.
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
AVATARS_DIR = os.path.join(ASSETS_DIR, "avatars")


def _section_divider():
    return ft.Container(height=1, bgcolor=DIVIDER_COLOR, margin=ft.Margin.symmetric(vertical=22))


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
    # Tracks the avatar photo's path relative to assets_dir (e.g.
    # "avatars/user_3_ab12cd34.png"), if one was ever picked. When set,
    # it takes visual priority over the emoji avatar - same convention
    # session.get_avatar_control() uses everywhere else in the app.
    selected_photo = {"path": session.current_user.get("photo")}

    avatar_preview = ft.Text(selected_avatar["value"], size=48)
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
                width=AVATAR_INNER_SIZE,
                height=AVATAR_INNER_SIZE,
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
        if not files or not files[0].path:
            return

        source_path = files[0].path

        # Copy the picked file into assets/avatars instead of storing
        # the original OS path directly: this is what makes it show up
        # correctly through ft.Image(src=...) / session.get_avatar_control()
        # everywhere else in the app, and keeps working even if the
        # original file gets moved or deleted later.
        os.makedirs(AVATARS_DIR, exist_ok=True)
        ext = os.path.splitext(source_path)[1] or ".png"
        user_id = session.current_user.get("id") or "tmp"
        filename = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = os.path.join(AVATARS_DIR, filename)
        try:
            shutil.copyfile(source_path, dest_path)
        except OSError:
            return  # picked file unreadable - leave the previous photo in place

        selected_photo["path"] = f"avatars/{filename}"
        avatar_circle.content = build_avatar_content()
        avatar_circle.update()

    # ================================================================
    # Header (over navy background, outside the white card). The close
    # button sits in the top-right corner, aligned with the card's edge
    # below, instead of stacked under the subtitle.
    # ================================================================
    def close_setup(e):
        page.go("/dashboard")

    close_button = ft.Container(
        content=ft.Icon(ft.Icons.CLOSE, size=20, color=ft.Colors.WHITE),
        width=42,
        height=42,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
        border_radius=14,
        alignment=ft.Alignment.CENTER,
        on_click=close_setup,
        ink=True,
    )

    header_stack = ft.Stack(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Your profile", size=27, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Container(
                        content=ft.Text("Customize how others see you", size=15, color=WHITE_TEXT),
                        padding=ft.Padding.only(top=4),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            ft.Container(content=close_button, alignment=ft.Alignment.TOP_RIGHT),
        ],
        width=CARD_WIDTH,
    )
    header_container = ft.Container(content=header_stack, padding=ft.Padding.only(bottom=28))

    # ================================================================
    # Profile photo / large avatar + overlaid camera button.
    # The avatar sits inside a soft turquoise-to-gold gradient ring for
    # a slightly more premium look than a flat border.
    # ================================================================
    avatar_circle = ft.Container(
        content=build_avatar_content(),
        width=AVATAR_INNER_SIZE,
        height=AVATAR_INNER_SIZE,
        bgcolor=NAVY_BG,
        border_radius=999,
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    avatar_ring = ft.Container(
        content=avatar_circle,
        width=AVATAR_OUTER_SIZE,
        height=AVATAR_OUTER_SIZE,
        border_radius=999,
        padding=4,
        alignment=ft.Alignment.CENTER,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[TURQUOISE, GOLD],
        ),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=18,
                             color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 6)),
    )

    camera_button = ft.Container(
        content=ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=18, color=NAVY_TEXT),
        width=38,
        height=38,
        bgcolor=GOLD,
        border_radius=999,
        alignment=ft.Alignment.CENTER,
        border=ft.Border.all(3, ft.Colors.WHITE),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=6,
                             color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
        on_click=pick_photo,
        ink=True,
    )

    avatar_stack = ft.Stack(
        controls=[
            avatar_ring,
            ft.Container(content=camera_button, alignment=ft.Alignment.BOTTOM_RIGHT,
                         width=AVATAR_OUTER_SIZE, height=AVATAR_OUTER_SIZE),
        ],
        width=AVATAR_OUTER_SIZE,
        height=AVATAR_OUTER_SIZE,
    )

    photo_section = ft.Column(
        controls=[
            avatar_stack,
            ft.Container(
                content=ft.Text("Tap the camera icon to change your photo", size=11.5, color=TEXT_GRAY,
                                 text_align=ft.TextAlign.CENTER),
                padding=ft.Padding.only(top=12),
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
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
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
            ft.Container(content=username_field, padding=ft.Padding.only(top=8)),
        ],
        spacing=0,
    )

    # ================================================================
    # Emoji avatar grid
    # ================================================================
    def style_avatar_button(container: ft.Container, is_selected: bool):
        if is_selected:
            container.bgcolor = ft.Colors.with_opacity(0.12, TURQUOISE)
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
            ft.Container(
                content=ft.Text("Used when you don't have a photo set", size=12, color=TEXT_GRAY),
                padding=ft.Padding.only(top=2),
            ),
            ft.Container(content=avatar_grid, padding=ft.Padding.only(top=12)),
        ],
        spacing=0,
    )

    # ================================================================
    # "Save and continue" button
    # ================================================================
    def save_and_continue(e):
        user_id = session.current_user.get("id")
        if user_id is not None:
            # database.update_profile's photo column is confirmed to
            # exist (see database.py), so this persists name, avatar,
            # and photo in one call.
            database.update_profile(
                user_id,
                name=username_field.value,
                avatar=selected_avatar["value"],
                photo=selected_photo["path"],
            )
        session.current_user["name"] = username_field.value
        session.current_user["avatar"] = selected_avatar["value"]
        session.current_user["photo"] = selected_photo["path"]
        page.go("/dashboard")

    save_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=19, color=NAVY_TEXT),
                ft.Text("Save and continue", size=17.5, color=NAVY_TEXT, weight=ft.FontWeight.W_600),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment.CENTER,
        bgcolor=TURQUOISE,
        border_radius=16.5,
        padding=ft.Padding.symmetric(vertical=17),
        width=float("inf"),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10,
                             color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK), offset=ft.Offset(0, 3)),
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
                _section_divider(),
                username_section,
                _section_divider(),
                avatar_section,
                ft.Container(height=26),
                save_button,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=CARD_WIDTH,
        padding=ft.Padding.symmetric(horizontal=32, vertical=32),
        bgcolor=ft.Colors.WHITE,
        border_radius=28,
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

    ft.run(_standalone, assets_dir="assets")