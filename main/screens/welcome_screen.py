import flet as ft

# =========================
# COLORES
# =========================

AZUL_OSCURO = "#001845"
AZUL_PRINCIPAL = "#002060"
TURQUESA = "#40E0D0"

GRIS_APP = "#E5E7EB"

GRIS_TEXTO = "#6B7A99"
GRIS_CLARO = "#9BA8BF"

BLANCO = "#FFFFFF"


# =========================
# TARJETAS
# =========================

def _feature_card(icono, texto):
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8,
        controls=[
            ft.Container(
                width=90,
                height=90,
                bgcolor="#244080",

                # Si Border también da error, elimina estas 6 líneas
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
                            icono,
                            size=35,
                            color=BLANCO,
                        )
                    ],
                ),
            ),

            ft.Text(
                texto,
                color=BLANCO,
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
        ],
    )


# =========================
# NAVEGACIÓN
# =========================

def abrir_crear_cuenta(page):
    page.go("/crear-cuenta")


# =========================
# PANTALLA
# =========================

def screen_welcome(page):

    page.clean()

    panel_izquierdo = ft.Container(
        expand=4,
        bgcolor=AZUL_PRINCIPAL,
        padding=40,

        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[
                ft.Container(
                    bgcolor=BLANCO,
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
                    color=BLANCO,
                ),

                ft.Text(
                    "Rompiendo barreras de comunicación",
                    size=18,
                    color=TURQUESA,
                ),

                ft.Container(height=40),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=30,
                    controls=[
                        _feature_card("🤟", "Señas"),
                        _feature_card("🤖", "IA"),
                        _feature_card("👥", "Comunidad"),
                    ],
                ),
            ],
        ),
    )

    panel_derecho = ft.Container(
        expand=6,
        bgcolor=BLANCO,
        padding=60,

        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[
                ft.Text(
                    "Comunicación\naccesible para todos",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=AZUL_OSCURO,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=15),

                ft.Text(
                    "Aprende señas con IA, conecta con la comunidad y comunícate sin barreras.",
                    size=18,
                    color=GRIS_TEXTO,
                    width=500,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(height=40),

                ft.ElevatedButton(
                    "Crear cuenta gratis",
                    width=350,
                    height=55,
                    bgcolor=TURQUESA,
                    color=AZUL_OSCURO,
                    on_click=lambda e: abrir_crear_cuenta(page),
                ),

                ft.Container(height=10),

                ft.OutlinedButton(
                    "Iniciar sesión",
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
                            "O continúa con",
                            color=GRIS_CLARO,
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
                            "Al continuar aceptas nuestros ",
                            style=ft.TextStyle(
                                color=GRIS_CLARO,
                            ),
                        ),

                        ft.TextSpan(
                            "Términos de servicio",
                            style=ft.TextStyle(
                                color=TURQUESA,
                            ),
                        ),
                    ],
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    vista = ft.Container(
        expand=True,
        bgcolor=GRIS_APP,
        padding=20,

        content=ft.Row(
            expand=True,
            spacing=0,
            controls=[
                panel_izquierdo,
                panel_derecho,
            ],
        ),
    )

    page.add(vista)

if __name__ == "__main__":
    ft.run(screen_welcome)