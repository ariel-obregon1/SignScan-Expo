"""
Pantalla de comunidad — screens/community.py

Ruta "/community". Un muro donde el usuario escribe publicaciones y
puede dar "me gusta" y responder a las de los demás.

Estructura: la misma que el dashboard.
    - Menú lateral fijo (260 px), idéntico al de dashboard.py pero con
      "Community" marcado como sección activa.
    - Contenido: banner dorado, caja para escribir y el muro de
      publicaciones.

Lo que SÍ funciona: publicar, dar y quitar "me gusta", desplegar el
cuadro de respuesta, responder, el contador de caracteres y el botón de
publicar que se activa solo cuando hay texto.

Lo que hay que tener claro antes de enseñarlo: **nada de esto se
guarda**. No existe tabla de publicaciones en la base de datos, así que
todo vive en memoria y desaparece al cambiar de pantalla o cerrar la
app. Las tres publicaciones de Maria, Carlos y Ana están escritas a
mano al final del archivo (`seed_posts`) para que el muro no se vea
vacío. Tampoco hay usuarios de verdad detrás: solo el que tiene la
sesión iniciada.

Cómo se distingue quién publica: las funciones que construyen tarjetas
reciben `use_session_avatar`. Si es True, el avatar sale de
session.get_avatar_control() (o sea, la foto o el emoji del usuario
logueado); si es False, se pinta el emoji fijo que se le pase, que es
lo que se usa para las publicaciones de ejemplo.
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import session  # noqa: E402

# ---- Colores ----
COLOR_SIDEBAR = "#002060"
COLOR_SIDEBAR_DARKER = "#001845"
COLOR_BG_MAIN = "#EEF2F7"
COLOR_TURQUOISE = "#40E0D0"
COLOR_GOLD = "#FFD700"
COLOR_LIKE_RED = "#EF4444"
COLOR_NAVY_TEXT = "#002060"
COLOR_GRAY_TEXT = "#6B7A99"
COLOR_LIGHT_GRAY_TEXT = "#9BA8BF"
COLOR_CARD_BORDER = "#F3F4F6"
COLOR_TEXTAREA_BG = "#F8FAFB"
COLOR_AVATAR_BG = "#EEF2F7"
COLOR_REPLY_AVATAR_BG = ft.Colors.with_opacity(0.15, COLOR_TURQUOISE)
COLOR_REPLY_BORDER = ft.Colors.with_opacity(0.20, COLOR_TURQUOISE)

SIDEBAR_WIDTH = 260
MAX_POST_LENGTH = 280
MAX_REPLY_LENGTH = 200


def screen_community(page: ft.Page):
    """Dibuja la pantalla de comunidad completa sobre `page`.

    Monta el menú lateral, la caja de publicar y el muro, y lo rellena
    con las publicaciones de ejemplo.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    page.title = "SignScan - Community"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    user_name = session.current_user.get("name") or "User"
    user_email = session.current_user.get("email") or ""

    # ================================================================
    # MENÚ LATERAL (misma estructura que dashboard.py)
    # ================================================================
    def nav_button(icon_name: str, label: str, active: bool = False, route: str | None = None):
        """Construye un botón del menú lateral.

        Args:
            icon_name: icono de Flet (ft.Icons.ALGO).
            label: texto del botón.
            active: True para pintarlo como la sección actual. Aquí lo
                lleva "Community".
            route: ruta a la que navega. Si es None, queda decorativo.

        Returns:
            El contenedor de Flet ya montado.
        """
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
                    content=session.get_avatar_control(size=16, container_size=44),
                    width=44,
                    height=44,
                    bgcolor=COLOR_SIDEBAR_DARKER,
                    border=ft.Border.all(1.8, COLOR_TURQUOISE),
                    border_radius=999,
                    alignment=ft.Alignment.CENTER,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
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
            nav_button(ft.Icons.HOME_ROUNDED, "Home", route="/dashboard"),
            nav_button(ft.Icons.MENU_BOOK_ROUNDED, "Learn", route="/learn"),
            nav_button(ft.Icons.CAMERA_ALT_ROUNDED, "Scan", route="/scan"),
            nav_button(ft.Icons.GROUPS_ROUNDED, "Community", active=True),
            nav_button(ft.Icons.VIDEOCAM_ROUNDED, "Video", route="/video"),
            nav_button(ft.Icons.PERSON_ROUNDED, "Profile", route="/profile"),
        ],
        spacing=0,
    )
    nav_container = ft.Container(content=nav_column, padding=ft.Padding.symmetric(horizontal=15, vertical=20))

    def handle_logout(e):
        """Cierra la sesión y vuelve a la pantalla de bienvenida.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        session.clear_current_user()
        page.go("/")

    logout_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=ft.Colors.WHITE),
                ft.Text("Log out", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
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
            scroll=ft.ScrollMode.AUTO,
        ),
        width=SIDEBAR_WIDTH,
        bgcolor=COLOR_SIDEBAR,
    )

    # ================================================================
    # Header
    # ================================================================
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(width=5, height=30, bgcolor=COLOR_TURQUOISE, border_radius=999),
                ft.Column(
                    controls=[
                        ft.Text("Community 👥", size=26, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
                        ft.Text("Connect with the deaf community", size=16, color=COLOR_GRAY_TEXT),
                    ],
                    spacing=2,
                ),
            ],
            spacing=15,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(left=25, right=25, top=40, bottom=20),
        bgcolor=ft.Colors.WHITE,
        border=ft.Border(bottom=ft.BorderSide(0.9, COLOR_CARD_BORDER)),
    )

    # ================================================================
    # Banner dorado de la parte de arriba
    # ================================================================
    gold_banner = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("👥 SignScan Community", size=20, weight=ft.FontWeight.W_900,
                        color=COLOR_NAVY_TEXT, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Text("Connect with the deaf community", size=15,
                                     color=COLOR_NAVY_TEXT,
                                     text_align=ft.TextAlign.CENTER),
                    padding=ft.Padding.only(top=5),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        bgcolor=COLOR_GOLD,
        border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                             color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
    )

    # ================================================================
    # Caja para escribir una publicación
    # ================================================================
    post_input = ft.TextField(
        hint_text="What are you learning today?",
        hint_style=ft.TextStyle(color=COLOR_LIGHT_GRAY_TEXT, size=17.5),
        bgcolor=COLOR_TEXTAREA_BG,
        border_color=COLOR_CARD_BORDER,
        border_width=0.9,
        border_radius=16.5,
        content_padding=ft.Padding.symmetric(horizontal=15, vertical=10),
        text_size=17.5,
        cursor_color=COLOR_TURQUOISE,
        multiline=True,
        min_lines=3,
        max_lines=5,
        max_length=MAX_POST_LENGTH,
    )

    char_counter = ft.Text(f"0/{MAX_POST_LENGTH}", size=15, color=COLOR_LIGHT_GRAY_TEXT)

    post_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEND_ROUNDED, size=12, color=ft.Colors.WHITE),
                ft.Text("Post", size=15, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE,
                        text_align=ft.TextAlign.CENTER),
            ],
            spacing=7.5,
        ),
        padding=ft.Padding.symmetric(horizontal=20, vertical=7.5),
        bgcolor=COLOR_NAVY_TEXT,
        border_radius=16.5,
        opacity=0.3,
        disabled=True,
    )

    feed_column = ft.Column(spacing=15)

    def handle_input_change(e):
        """Actualiza el contador y activa o desactiva el botón Post.

        Se dispara con cada tecla. El botón solo se habilita si hay
        texto y no se pasa del límite de caracteres; cuando está
        deshabilitado se pinta translúcido para que se note.

        Args:
            e: evento de cambio de Flet. No se usa.
        """
        length = len(post_input.value or "")
        char_counter.value = f"{length}/{MAX_POST_LENGTH}"
        char_counter.update()
        can_post = 0 < length <= MAX_POST_LENGTH
        post_button.opacity = 1 if can_post else 0.3
        post_button.disabled = not can_post
        post_button.update()

    post_input.on_change = handle_input_change

    def handle_post_click(e):
        """Publica lo escrito: lo mete arriba del muro y limpia la caja.

        La publicación se inserta en la posición 0 para que salga la
        primera, con la etiqueta de tiempo "now".

        Recordatorio: esto NO se guarda en ningún sitio. Al salir de la
        pantalla, la publicación desaparece.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        text = (post_input.value or "").strip()
        if not text:
            return
        # use_session_avatar=True: esta publicación es del usuario que
        # tiene la sesión abierta, así que debe salir su foto si puso
        # alguna.
        new_post = build_post_card(None, user_name, "now", text, likes=0, replies=[],
                                    use_session_avatar=True)
        feed_column.controls.insert(0, new_post)
        feed_column.update()
        post_input.value = ""
        char_counter.value = f"0/{MAX_POST_LENGTH}"
        post_button.opacity = 0.3
        post_button.disabled = True
        post_input.update()
        char_counter.update()
        post_button.update()

    post_button.on_click = handle_post_click

    composer_header = ft.Row(
        controls=[
            ft.Container(
                content=session.get_avatar_control(size=22.5, container_size=45),
                width=45,
                height=45,
                bgcolor=COLOR_AVATAR_BG,
                border_radius=999,
                alignment=ft.Alignment.CENTER,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            ft.Text(user_name, size=17.5, weight=ft.FontWeight.W_900, color=COLOR_NAVY_TEXT),
        ],
        spacing=15,
    )

    composer_footer = ft.Row(
        controls=[char_counter, post_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    composer_card = ft.Container(
        content=ft.Column(
            controls=[
                composer_header,
                ft.Container(content=post_input, padding=ft.Padding.only(top=15)),
                ft.Container(content=composer_footer, padding=ft.Padding.only(top=10)),
            ],
            spacing=0,
        ),
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(0.9, COLOR_CARD_BORDER),
        border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                             color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
    )

    # ================================================================
    # Tarjetas del muro
    # ================================================================
    def _circle_avatar(avatar_emoji, use_session_avatar, size, bgcolor):
        """Construye un avatar redondo, de foto o de emoji.

        Args:
            avatar_emoji: emoji a usar cuando la publicación no es del
                usuario logueado.
            use_session_avatar: True para usar la foto o el emoji del
                usuario que tiene la sesión iniciada.
            size: diámetro del círculo en píxeles.
            bgcolor: color de fondo, que se ve cuando el contenido es
                un emoji.

        Returns:
            El contenedor de Flet, con el recorte activado para que una
            foto salga redonda y no cuadrada.
        """
        content = (
            session.get_avatar_control(size=size * 0.65, container_size=size)
            if use_session_avatar
            else ft.Text(avatar_emoji, size=size * 0.65)
        )
        return ft.Container(
            content=content,
            width=size,
            height=size,
            bgcolor=bgcolor,
            border_radius=999,
            alignment=ft.Alignment.CENTER,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    def build_reply(avatar: str, name: str, text: str, use_session_avatar: bool = False):
        """Construye una respuesta dentro de una publicación.

        Se distingue visualmente por la línea turquesa de la izquierda y
        por ser más pequeña que la publicación que la contiene.

        Args:
            avatar: emoji de quien responde.
            name: nombre de quien responde.
            text: contenido de la respuesta.
            use_session_avatar: True si responde el usuario logueado.

        Returns:
            El contenedor de Flet ya montado.
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    _circle_avatar(avatar, use_session_avatar, 27, ft.Colors.TRANSPARENT),
                    ft.Column(
                        controls=[
                            ft.Text(name, size=15, weight=ft.FontWeight.W_900, color=COLOR_NAVY_TEXT),
                            ft.Container(
                                content=ft.Text(text, size=15, color=COLOR_GRAY_TEXT),
                                padding=ft.Padding.only(top=2.5),
                            ),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.only(left=15),
            border=ft.Border(left=ft.BorderSide(1.8, COLOR_REPLY_BORDER)),
            margin=ft.Margin.only(top=15),
        )

    def build_post_card(avatar: str, name: str, time_label: str, text: str, likes: int, replies: list,
                         use_session_avatar: bool = False):
        """Construye una tarjeta de publicación entera y funcional.

        Cada tarjeta se lleva su propio estado (si está marcada con "me
        gusta", cuántos lleva, sus respuestas y si el cuadro de
        responder está abierto). Por eso los manejadores se definen aquí
        dentro: así cada publicación toca solo sus propios controles y
        no los de las demás.

        Args:
            avatar: emoji de quien publica.
            name: nombre de quien publica.
            time_label: texto de tiempo ("2h", "now"...). Es una
                etiqueta suelta, no una fecha de verdad.
            text: contenido de la publicación.
            likes: número inicial de "me gusta".
            replies: lista de diccionarios con las respuestas iniciales,
                cada uno con "avatar", "name" y "text".
            use_session_avatar: True si publica el usuario logueado.

        Returns:
            El contenedor de Flet ya montado.
        """
        # ---- Me gusta: corazón rojo relleno si está marcado, gris con
        # solo el contorno si no ----
        like_state = {"liked": False, "count": likes}
        like_icon = ft.Icon(ft.Icons.FAVORITE_BORDER_ROUNDED, size=14, color=COLOR_LIGHT_GRAY_TEXT)
        like_count_text = ft.Text(str(likes), size=15, weight=ft.FontWeight.BOLD, color=COLOR_LIGHT_GRAY_TEXT)

        def toggle_like(e):
            """Marca o desmarca el "me gusta" de ESTA publicación.

            Cambia el icono, el color y el contador de una vez. El
            estado va en el diccionario like_state porque las funciones
            anidadas no pueden reasignar variables del ámbito exterior
            sin `nonlocal`.

            Args:
                e: evento de clic de Flet. No se usa.
            """
            like_state["liked"] = not like_state["liked"]
            like_state["count"] += 1 if like_state["liked"] else -1
            like_count_text.value = str(like_state["count"])
            if like_state["liked"]:
                like_icon.name = ft.Icons.FAVORITE_ROUNDED
                like_icon.color = COLOR_LIKE_RED
                like_count_text.color = COLOR_LIKE_RED
            else:
                like_icon.name = ft.Icons.FAVORITE_BORDER_ROUNDED
                like_icon.color = COLOR_LIGHT_GRAY_TEXT
                like_count_text.color = COLOR_LIGHT_GRAY_TEXT
            like_count_text.update()
            like_icon.update()

        like_button = ft.Container(
            content=ft.Row(controls=[like_icon, like_count_text], spacing=7.5),
            on_click=toggle_like,
            ink=True,
        )

        # ---- Respuestas: una columna que crece en vivo, más el cuadro
        # de responder que se muestra y se oculta ----
        reply_controls = [
            build_reply(r["avatar"], r["name"], r["text"], r.get("use_session_avatar", False))
            for r in replies
        ]
        replies_column = ft.Column(controls=reply_controls, spacing=0)

        reply_count_text = ft.Text(
            f"Reply ({len(reply_controls)})" if reply_controls else "Reply",
            size=15, weight=ft.FontWeight.W_600, color=COLOR_LIGHT_GRAY_TEXT,
        )

        reply_input = ft.TextField(
            hint_text="Write a reply...",
            hint_style=ft.TextStyle(color=COLOR_LIGHT_GRAY_TEXT, size=15),
            bgcolor=COLOR_TEXTAREA_BG,
            border_color=COLOR_CARD_BORDER,
            border_width=0.9,
            border_radius=14,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            text_size=15,
            cursor_color=COLOR_TURQUOISE,
            max_length=MAX_REPLY_LENGTH,
            expand=True,
        )

        def send_reply(e):
            """Añade una respuesta a ESTA publicación.

            La respuesta se pinta al final de la lista, se limpia el
            campo y se actualiza el contador del botón. Igual que las
            publicaciones, no se guarda en ningún sitio.

            Args:
                e: evento de clic de Flet. No se usa.
            """
            reply_text = (reply_input.value or "").strip()
            if not reply_text:
                return
            # La respuesta siempre es del usuario que tiene la sesión
            # abierta, así que debe salir su foto si puso alguna.
            replies_column.controls.append(build_reply(None, user_name, reply_text, use_session_avatar=True))
            replies_column.update()
            reply_input.value = ""
            reply_input.update()
            reply_count_text.value = f"Reply ({len(replies_column.controls)})"
            reply_count_text.update()

        reply_send_button = ft.Container(
            content=ft.Icon(ft.Icons.SEND_ROUNDED, size=16, color=ft.Colors.WHITE),
            width=36,
            height=36,
            bgcolor=COLOR_NAVY_TEXT,
            border_radius=999,
            alignment=ft.Alignment.CENTER,
            on_click=send_reply,
            ink=True,
        )

        reply_composer = ft.Container(
            content=ft.Row(controls=[reply_input, reply_send_button], spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.only(top=12),
            visible=False,
        )

        def toggle_reply_composer(e):
            """Muestra u oculta el cuadro para responder.

            Args:
                e: evento de clic de Flet. No se usa.
            """
            reply_composer.visible = not reply_composer.visible
            reply_composer.update()

        reply_button = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE_ROUNDED, size=14, color=COLOR_LIGHT_GRAY_TEXT),
                    reply_count_text,
                ],
                spacing=7.5,
            ),
            on_click=toggle_reply_composer,
            ink=True,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    _circle_avatar(avatar, use_session_avatar, 45, COLOR_REPLY_AVATAR_BG),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(name, size=17.5, weight=ft.FontWeight.W_900, color=COLOR_NAVY_TEXT),
                                    ft.Text(time_label, size=15, color=COLOR_LIGHT_GRAY_TEXT),
                                ],
                                spacing=10,
                            ),
                            ft.Container(
                                content=ft.Text(text, size=17.5, color=COLOR_GRAY_TEXT),
                                padding=ft.Padding.only(top=5),
                            ),
                            ft.Container(
                                content=ft.Row(controls=[like_button, reply_button], spacing=25),
                                padding=ft.Padding.only(top=15),
                            ),
                            ft.Container(content=replies_column, padding=ft.Padding.only(top=15)),
                            reply_composer,
                        ],
                        spacing=0,
                        expand=True,
                    ),
                ],
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(0.9, COLOR_CARD_BORDER),
            border_radius=20,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3,
                                 color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK), offset=ft.Offset(0, 1)),
        )

    seed_posts = [
        build_post_card(
            "👩", "Maria Garcia", "2h",
            "I just learned the whole alphabet! 🤟 Any tips for memorizing the tricky letters?",
            likes=2,
            replies=[{"avatar": "👨", "name": "Carlos R.",
                      "text": "Awesome! I practice in front of the mirror every morning. Works really well 😊"}],
        ),
        build_post_card(
            "👨", "Carlos Ruiz", "4h",
            "First week using SignScan and I already recognize basic greetings. Amazing app! 🌟",
            likes=1,
            replies=[],
        ),
        build_post_card(
            "👩‍🦱", "Ana Lopez", "1d",
            "Does anyone know how to sign \"birthday\"? I can't find it in the lessons.",
            likes=0,
            replies=[],
        ),
    ]
    feed_column.controls = seed_posts

    body_content = ft.Container(
        content=ft.Column(
            controls=[gold_banner, composer_card, feed_column],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=ft.Padding.only(left=20, right=20, top=20, bottom=40),
        expand=True,
    )

    main_content = ft.Container(
        content=ft.Column(
            controls=[header, body_content],
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
        """Arranque suelto de esta pantalla, para trabajar su diseño.

        Con `python screens/community.py` se abre solo la comunidad. Al
        no haber sesión iniciada saldrá como "User", y los botones de
        navegación no llevarán a ningún sitio.

        Args:
            page: la página que crea Flet.
        """
        page.window.maximized = True
        page.window.min_width = 1100
        page.window.min_height = 700
        page.update()
        screen_community(page)

    ft.run(_standalone)