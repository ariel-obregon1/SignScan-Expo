"""
Pantalla de personalizar perfil — screens/personalize_profile.py

Ruta "/profile". Es el paso siguiente al alta de cuenta: aquí el
usuario elige cómo se le va a ver en la app.

Estructura: una tarjeta blanca centrada sobre fondo azul marino, con
    - el avatar grande y un botón de cámara encima para poner una foto,
    - el campo de nombre de usuario,
    - una rejilla de 20 emojis para elegir avatar,
    - el botón "Save and continue", que guarda y va al dashboard.

Estado de la pantalla: se lleva en dos diccionarios de una sola clave
(selected_avatar y selected_photo) en vez de variables sueltas, porque
las funciones anidadas necesitan MODIFICARLOS y en Python no se puede
reasignar una variable del ámbito exterior sin `nonlocal`; con un
diccionario basta con cambiar su contenido.

Limitación conocida: la foto elegida NO se guarda en la base de datos
(database.update_profile no tiene columna para ella), solo vive en la
sesión hasta que se cierra la app. El nombre y el emoji sí se guardan.
"""

import os
import sys

import flet as ft

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database  # noqa: E402
import session  # noqa: E402

# ---- Colores ----
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
    """Dibuja la pantalla de personalizar perfil sobre `page`.

    Arranca leyendo lo que ya haya en la sesión (nombre y avatar
    actuales), de forma que si el usuario vuelve a entrar se encuentre
    sus datos ya puestos en vez de los valores por defecto.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    page.title = "SignScan - Your profile"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    current_name = session.current_user.get("name") or ""
    selected_avatar = {"value": session.current_user.get("avatar") or "🌟"}
    # Guarda la ruta de la foto elegida del disco, si hay alguna.
    # Cuando tiene valor, manda sobre el emoji en el avatar grande.
    selected_photo = {"path": session.current_user.get("photo")}

    avatar_preview = ft.Text(selected_avatar["value"], size=50)
    avatar_buttons = {}

    # ================================================================
    # Selector de archivos (foto de perfil)
    # ================================================================
    def build_avatar_content():
        """Decide qué va dentro del círculo grande del avatar.

        Si el usuario eligió una foto, manda la foto; si no, el emoji.
        Se llama cada vez que cambia una de las dos cosas para redibujar
        el círculo.

        Returns:
            Un ft.Image con la foto recortada en redondo, o el ft.Text
            con el emoji.
        """
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
        """Abre el diálogo del sistema para elegir una foto de perfil.

        Es asíncrona porque el selector de archivos de Flet se espera
        con `await`: la app no se bloquea mientras el usuario busca la
        imagen. Si cierra el diálogo sin elegir nada, no se toca nada.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        # En las versiones actuales de Flet, FilePicker.pick_files() se
        # espera directamente y devuelve los archivos elegidos: no hace
        # falta registrarlo en page.overlay ni usar un callback
        # on_result como en versiones antiguas.
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
    # Cabecera (sobre el fondo azul, fuera de la tarjeta blanca)
    # ================================================================
    def close_setup(e):
        """Cierra la personalización sin guardar y va al dashboard.

        Es la X de arriba: los cambios que el usuario haya tocado en
        esta pantalla se pierden a propósito.

        Args:
            e: evento de clic de Flet. No se usa.
        """
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
    # Foto de perfil / avatar grande con el botón de cámara encima
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
    # Campo: nombre de usuario
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
    # Rejilla de avatares (emojis)
    # ================================================================
    def style_avatar_button(container: ft.Container, is_selected: bool):
        """Pinta un botón de emoji como seleccionado o normal.

        Modifica el contenedor que recibe (no crea uno nuevo): el
        seleccionado lleva fondo turquesa suave y borde turquesa; los
        demás, fondo gris claro y borde transparente (transparente y no
        "sin borde" para que todos ocupen exactamente lo mismo y la
        rejilla no baile al cambiar de selección).

        Args:
            container: el botón a repintar.
            is_selected: True si es el emoji elegido ahora mismo.
        """
        if is_selected:
            container.bgcolor = ft.Colors.with_opacity(0.1, TURQUOISE)
            container.border = ft.Border.all(2, TURQUOISE)
        else:
            container.bgcolor = AVATAR_BG
            container.border = ft.Border.all(1.8, ft.Colors.TRANSPARENT)

    def select_avatar(emoji: str):
        """Fabrica el manejador de clic para un emoji concreto.

        Devuelve una función en vez de ser el manejador directamente
        porque los 20 botones se crean en un bucle: así cada uno se
        queda con SU emoji. Si se usara el mismo manejador para todos,
        los 20 acabarían apuntando al último emoji del bucle.

        Args:
            emoji: el emoji que representa este botón.

        Returns:
            La función que Flet llamará al pulsar ese botón.
        """
        def handler(e):
            """Aplica la selección de este emoji.

            Actualiza el estado, redibuja el círculo grande y repinta
            los 20 botones para que solo uno quede resaltado.

            Args:
                e: evento de clic de Flet. No se usa.
            """
            # Elegir un emoji borra la foto que hubiera puesta, para
            # que sea el emoji lo que se vea en el círculo grande.
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
    # Botón "Save and continue"
    # ================================================================
    def save_and_continue(e):
        """Guarda el perfil y sigue al dashboard.

        Escribe en dos sitios: en la base de datos (para que el cambio
        sobreviva al cierre de la app) y en la sesión en memoria (para
        que el dashboard lo vea al instante, sin volver a consultar).

        Si no hay usuario en sesión (por ejemplo, abriendo esta pantalla
        suelta para probar el diseño), se salta la parte de la base de
        datos y solo actualiza la sesión.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        user_id = session.current_user.get("id")
        if user_id is not None:
            try:
                # Si algún día database.update_profile acepta una
                # columna para la ruta de la foto, esta llamada la
                # guardará también. Mientras no la acepte, lanza
                # TypeError y se reintenta abajo solo con nombre y
                # avatar (que es lo que pasa hoy).
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
    # Tarjeta blanca (el formulario en sí)
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

    # El contenedor exterior ocupa toda la página (expand=True) y el
    # fondo azul se estira con él, así que basta con maximizar o poner
    # la ventana a pantalla completa para llenar el monitor entero,
    # mientras la tarjeta blanca conserva su tamaño y sigue centrada.
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
        """Arranque suelto de esta pantalla, para trabajar su diseño.

        Con `python screens/personalize_profile.py` se abre solo el
        perfil. Al no haber sesión iniciada, los campos salen vacíos y
        el guardado solo afecta a la sesión en memoria.

        Args:
            page: la página que crea Flet.
        """
        # Ventana maximizada para ocupar todo el monitor.
        page.window.maximized = True
        # Si se prefiere pantalla completa de verdad (sin barra de
        # título ni controles de ventana), usar esto otro:
        # page.window.full_screen = True
        page.window.min_width = 900
        page.window.min_height = 700
        page.update()
        screen_personalizeprofile(page)

    ft.run(_standalone)