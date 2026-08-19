"""
Pantalla principal / dashboard — screens/dashboard.py

Ruta "/dashboard". Es la pantalla a la que se llega después de iniciar
sesión y el centro de navegación de la app.

Estructura: dos zonas en una fila.
    - Menú lateral fijo (260 px): logo, ficha del usuario, botones de
      navegación y botón de cerrar sesión.
    - Contenido principal: saludo con la racha, tres tarjetas de
      estadísticas, el progreso por temas y la rejilla de módulos.

Los datos del usuario (nombre, correo y avatar) salen de
session.current_user, no de la base de datos: la sesión ya los tiene
cargados desde el login.

Aviso importante para quien siga esto: TODAS las cifras de progreso
están escritas a mano (racha de 3 días, 0/259 señas, 0% en cada tema).
Son maqueta; todavía no hay nada que las calcule ni tabla donde
guardarlas. Los botones "Video Chat", "Learn Signs" y "Community" de la
rejilla de módulos tampoco navegan a ningún sitio, a propósito: se les
pasa route=None.
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
COLOR_AMBER = "#F59E0B"
COLOR_PURPLE = "#8B5CF6"
COLOR_RED = "#DC2626"
COLOR_LOGOUT_ICON = "#F87171"
COLOR_NAVY_TEXT = "#002060"
COLOR_GRAY_TEXT = "#6B7A99"
COLOR_LIGHT_GRAY_TEXT = "#9BA8BF"
COLOR_CARD_BORDER = "#F3F4F6"
COLOR_ROW_BG = "#F8FAFB"
COLOR_PROGRESS_TRACK = "#E5E7EB"

SIDEBAR_WIDTH = 260

# Sombra suave que comparten todas las tarjetas blancas de esta
# pantalla. Es la misma que ya usan las tarjetas de login/alta y las
# publicaciones de la comunidad, para que todo se vea del mismo juego.
CARD_SHADOW = ft.BoxShadow(
    spread_radius=1, blur_radius=10,
    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
    offset=ft.Offset(0, 3),
)


def screen_dashboard(page: ft.Page):
    """Dibuja el dashboard completo sobre `page`.

    Lee de la sesión el nombre, el correo y el avatar del usuario. Si no
    hay nadie con la sesión iniciada (por ejemplo al abrir esta pantalla
    suelta), usa valores por defecto en vez de fallar.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    page.title = "SignScan - Home"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0
    page.fonts = {
        "Nunito": "https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Nunito")

    user_name = session.current_user.get("name") or "User"
    user_email = session.current_user.get("email") or ""

    # ================================================================
    # MENÚ LATERAL
    # ================================================================
    def nav_button(icon_name: str, label: str, active: bool = False, route: str | None = None):
        """Construye un botón del menú lateral.

        Args:
            icon_name: icono de Flet (ft.Icons.ALGO).
            label: texto del botón.
            active: True para pintarlo como la sección actual (fondo
                turquesa y texto azul). Solo "Home" lo lleva puesto.
            route: ruta a la que navega al pulsarlo. Si es None, el
                botón queda sin evento de clic, es decir, decorativo.

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
            nav_button(ft.Icons.HOME_ROUNDED, "Home", active=True),
            nav_button(ft.Icons.MENU_BOOK_ROUNDED, "Learn", route="/learn"),
            nav_button(ft.Icons.CAMERA_ALT_ROUNDED, "Scan", route="/scan"),
            nav_button(ft.Icons.GROUPS_ROUNDED, "Community", route="/community"),
            nav_button(ft.Icons.VIDEOCAM_ROUNDED, "Video", route="/video"),
            nav_button(ft.Icons.PERSON_ROUNDED, "Profile", route="/profile"),
        ],
        spacing=0,
    )
    nav_container = ft.Container(content=nav_column, padding=ft.Padding.symmetric(horizontal=15, vertical=20))

    def handle_logout(e):
        """Cierra la sesión y vuelve a la pantalla de bienvenida.

        Borra los datos del usuario de la sesión en memoria; la cuenta
        sigue existiendo en la base de datos.

        Args:
            e: evento de clic de Flet. No se usa.
        """
        session.clear_current_user()
        page.go("/")

    logout_button = ft.Container(
        content=ft.Row(
            controls=[
                # Un icono con un tono cálido (en vez de blanco a
                # secas) es una pista visual habitual de que esto es una
                # acción de "salir", sin necesidad de un botón rojo.
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=COLOR_LOGOUT_ICON),
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
    # CONTENIDO PRINCIPAL — Cabecera (saludo + racha)
    # ================================================================
    greeting_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(f"Hi, {user_name}! 👋", size=30, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
                        ft.Text("Keep learning today", size=17.5, color=COLOR_GRAY_TEXT),
                    ],
                    spacing=3,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, size=16, color="#92400E"),
                            ft.Text("3", size=12, weight=ft.FontWeight.BOLD, color="#92400E"),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                    bgcolor=COLOR_GOLD,
                    border_radius=999,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=8,
                                         color=ft.Colors.with_opacity(0.25, COLOR_GOLD), offset=ft.Offset(0, 2)),
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
    # Stat cards
    # ================================================================
    def stat_card(emoji: str, value: str, label: str, accent_color: str):
        """Construye una de las tres tarjetas blancas de estadísticas.

        Args:
            emoji: icono de arriba, dentro de un círculo de color.
            value: cifra o texto destacado del centro.
            label: descripción pequeña de abajo.
            accent_color: color del círculo del icono. Se aplica con
                opacidad baja para que quede como un fondo suave.

        Returns:
            El contenedor de Flet ya montado, con expand=True para que
            las tres se repartan el ancho por igual.
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(emoji, size=22),
                        width=52,
                        height=52,
                        bgcolor=ft.Colors.with_opacity(0.14, accent_color),
                        border_radius=999,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
                    ft.Text(label, size=14, color=COLOR_GRAY_TEXT),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=22),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(0.9, COLOR_CARD_BORDER),
            border_radius=20,
            expand=True,
            alignment=ft.Alignment.CENTER,
            shadow=CARD_SHADOW,
        )

    stats_row = ft.Row(
        controls=[
            stat_card("🔥", "1", "day streak", COLOR_AMBER),
            stat_card("🤟", "0", "signs learned", COLOR_TURQUOISE),
            stat_card("⭐", "Basic", "level", COLOR_PURPLE),
        ],
        spacing=20,
    )

    # ================================================================
    # Barras de progreso
    # ================================================================
    def simple_progress_bar(percent: int, color: str, height: int = 8):
        """Dibuja una barra de progreso a mano, sin ft.ProgressBar.

        El truco: dos contenedores dentro de una fila, uno con
        expand=porcentaje_lleno y otro con expand=porcentaje_vacío. Flet
        reparte el ancho en esa proporción, así que se ve como una barra
        que se llena, y de paso se puede redondear como se quiera.

        Args:
            percent: porcentaje completado, de 0 a 100.
            color: color de la parte llena.
            height: alto de la barra en píxeles.

        Returns:
            El contenedor de Flet ya montado. Con percent=0 devuelve
            solo el carril gris de fondo.
        """
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

    scoreboard_card = ft.Container(
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
                                ft.Text("Scoreboard", size=17.5, color=COLOR_NAVY_TEXT),
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
        shadow=CARD_SHADOW,
    )

    def category_label(text: str):
        """Devuelve el título pequeño de una categoría (BASIC, etc.).

        Args:
            text: texto de la etiqueta, normalmente con su emoji.

        Returns:
            El ft.Text ya formateado.
        """
        # El weight=BOLD le da a estas etiquetas pequeñas en mayúsculas
        # ("BASIC / INTERMEDIATE / ADVANCED") la presencia que se espera
        # de un encabezado de sección; sin él se leen como texto fino y
        # pasan desapercibidas.
        return ft.Text(text, size=10.5, weight=ft.FontWeight.BOLD, color=COLOR_GRAY_TEXT)

    def topic_row(emoji: str, name: str, percent: int, percent_color: str):
        """Construye una fila de tema con su barra de progreso.

        Formato horizontal: emoji, nombre con la barra debajo y el
        porcentaje a la derecha. Se usa en las categorías básica e
        intermedia.

        Args:
            emoji: icono del tema.
            name: nombre del tema (Alphabet, Greetings...).
            percent: porcentaje completado, de 0 a 100.
            percent_color: color de la barra y del porcentaje, que
                cambia según la dificultad de la categoría.

        Returns:
            El contenedor de Flet ya montado.
        """
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
        """Igual que topic_row, pero en vertical y más estrecha.

        Se usa en la categoría avanzada, donde tres temas van uno al
        lado del otro en la misma fila y no cabe el formato horizontal.

        Args:
            emoji: icono del tema.
            name: nombre del tema.
            percent: porcentaje completado, de 0 a 100.
            percent_color: color de la barra y del porcentaje.

        Returns:
            El contenedor de Flet ya montado, con expand=True para
            repartirse el ancho con sus hermanos.
        """
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

    def category_card(label: str, content):
        """Envuelve una categoría de temas en una tarjeta blanca.

        Args:
            label: título de la categoría, con su emoji.
            content: el control con los temas de esa categoría (una
                columna de filas, o una fila de tarjetas verticales).

        Returns:
            El contenedor de Flet ya montado.
        """
        return ft.Container(
            content=ft.Column(
                controls=[
                    category_label(label),
                    ft.Container(content=content, padding=ft.Padding.only(top=10)),
                ],
                spacing=0,
            ),
            padding=ft.Padding.symmetric(horizontal=18, vertical=16),
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(0.9, COLOR_CARD_BORDER),
            border_radius=20,
            shadow=CARD_SHADOW,
        )

    basic_section = category_card(
        "🌱 BASIC",
        ft.Column(
            controls=[
                topic_row("🔤", "Alphabet", 0, COLOR_TURQUOISE),
                topic_row("👋", "Greetings", 0, COLOR_TURQUOISE),
                topic_row("🔢", "Numbers", 0, COLOR_TURQUOISE),
                topic_row("🎨", "Colors", 0, COLOR_TURQUOISE),
            ],
            spacing=10,
        ),
    )

    intermediate_section = category_card(
        "🚀 INTERMEDIATE",
        ft.Column(
            controls=[
                topic_row("👨‍👩‍👧", "Family", 0, COLOR_PURPLE),
                topic_row("🍎", "Food", 0, COLOR_PURPLE),
            ],
            spacing=10,
        ),
    )

    advanced_section = category_card(
        "🔥 ADVANCED",
        ft.Row(
            controls=[
                topic_row_stacked("😊", "Emotions", 0, COLOR_RED),
                topic_row_stacked("🐾", "Animals", 0, COLOR_RED),
                topic_row_stacked("🏅", "Sports", 0, COLOR_RED),
            ],
            spacing=15,
        ),
    )

    progress_card = ft.Container(
        content=ft.Column(
            controls=[scoreboard_card, basic_section, intermediate_section, advanced_section],
            spacing=20,
        ),
        padding=ft.Padding.only(top=25),
    )

    # ================================================================
    # Módulos
    # ================================================================
    def module_card(emoji: str, title: str, subtitle: str, bgcolor, text_color, route: str | None = None):
        """Construye una de las tarjetas grandes de módulo.

        Args:
            emoji: icono dentro del cuadrado translúcido.
            title: título del módulo.
            subtitle: descripción de una línea.
            bgcolor: color de fondo de la tarjeta.
            text_color: color del texto, que cambia según lo oscuro que
                sea el fondo.
            route: ruta a la que navega. Si es None, la tarjeta es
                decorativa (hoy solo "Scan Signs" navega, a "/scan").

        Returns:
            El contenedor de Flet ya montado.
        """
        body = ft.Column(
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
        )
        arrow = ft.Container(
            content=ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=18, color=text_color),
            alignment=ft.Alignment.TOP_RIGHT,
            opacity=0.55,
        )
        return ft.Container(
            content=ft.Stack(controls=[body, arrow]),
            padding=25,
            bgcolor=bgcolor,
            border_radius=20,
            expand=1,
            ink=True,
            shadow=CARD_SHADOW,
            on_click=(lambda e: page.go(route)) if route else None,
        )

    modules_grid = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    module_card("📷", "Scan Signs", "Detect signs in real time with AI",
                                COLOR_TURQUOISE, COLOR_NAVY_TEXT, route="/scan"),
                    module_card("📹", "Video Chat", "Video calls with interpretation",
                                COLOR_SIDEBAR, ft.Colors.WHITE),
                ],
                spacing=15,
            ),
            ft.Row(
                controls=[
                    module_card("📖", "Learn Signs", "Interactive sign language lessons",
                                COLOR_GOLD, COLOR_NAVY_TEXT, route="/learn"),
                    module_card("👥", "Community", "Connect with deaf people",
                                ft.Colors.WHITE, COLOR_NAVY_TEXT, route="/community"),
                ],
                spacing=15,
            ),
        ],
        spacing=15,
    )

    modules_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Modules", size=22.5, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_TEXT),
                ft.Container(content=modules_grid, padding=ft.Padding.only(top=15)),
            ],
            spacing=0,
        ),
        padding=ft.Padding.only(top=25),
    )

    body_content = ft.Container(
        content=ft.Column(
            controls=[stats_row, progress_card, modules_section],
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
        """Arranque suelto de esta pantalla, para trabajar su diseño.

        Con `python screens/dashboard.py` se abre solo el dashboard. Al
        no haber sesión iniciada saldrá como "User" y sin correo, y los
        botones de navegación no llevarán a ningún sitio.

        Args:
            page: la página que crea Flet.
        """
        page.window.maximized = True
        page.window.min_width = 1100
        page.window.min_height = 700
        page.update()
        screen_dashboard(page)

    ft.run(_standalone, assets_dir="assets")