# screens/crear_cuenta.py

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
# NAVEGACIÓN
# =========================

def volver_inicio(page):
    from screens.bienvenida import pantalla_bienvenida
    pantalla_bienvenida(page)


# =========================
# PANTALLA
# =========================

def pantalla_crear_cuenta(page):

    page.clean()

    # =========================
    # INPUTS
    # =========================

    ESTILO_INPUT = {
        "width": 420,
        "height": 60,
        "border_radius": 14,
        "filled": True,
        "bgcolor": "#FFFFFF",
        "border_color": "#CBD5E1",
        "focused_border_color": TURQUESA,
        "color": "#0F172A",
        "text_size": 15,
    }

    nombre = ft.TextField(
        label="Nombre completo",
        hint_text="Ingresa tu nombre",
        **ESTILO_INPUT
    )

    correo = ft.TextField(
        label="Correo electrónico",
        hint_text="ejemplo@email.com",
        **ESTILO_INPUT
    )

    password = ft.TextField(
        label="Contraseña",
        hint_text="Mínimo 8 caracteres",
        password=True,
        can_reveal_password=True,
        **ESTILO_INPUT
    )

    confirmar = ft.TextField(
        label="Confirmar contraseña",
        hint_text="Repite tu contraseña",
        password=True,
        can_reveal_password=True,
        **ESTILO_INPUT
    )

    # =========================
    # PANEL IZQUIERDO
    # =========================

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
                    border_radius=25,
                    padding=20,
                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        spread_radius=1,
                        color="#30000000",
                    ),
                    content=ft.Image(
                        src="logo.png",
                        width=170,
                    ),
                ),

                ft.Container(height=25),

                ft.Text(
                    "SignScan",
                    size=42,
                    weight="bold",
                    color=BLANCO,
                ),

                ft.Container(height=10),

                ft.Text(
                    "Comunicación accesible para todos",
                    size=18,
                    color=TURQUESA,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )

    # =========================
    # REDES
    # =========================

    redes = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
        controls=[

            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=14,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("G", size=24),
                    ],
                ),
            ),

            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=14,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("🍎", size=22),
                    ],
                ),
            ),

            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1, "#E2E8F0"),
                border_radius=14,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("f", size=26),
                    ],
                ),
            ),
        ],
    )

    # =========================
    # FORMULARIO
    # =========================

    formulario = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[

            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.TextButton(
                        "< Volver",
                        on_click=lambda e: volver_inicio(page)
                    )
                ]
            ),

            ft.Container(height=5),

            ft.Text(
                "Crear cuenta",
                size=38,
                weight="bold",
                color="#0F172A",
            ),

            ft.Container(height=5),

            ft.Text(
                "Únete a la comunidad SignScan",
                size=16,
                color=GRIS_TEXTO,
            ),

            ft.Container(height=25),

            redes,

            ft.Container(height=25),

            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[

                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),

                    ft.Container(width=10),

                    ft.Text(
                        "O con email",
                        size=13,
                        color=GRIS_CLARO,
                    ),

                    ft.Container(width=10),

                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),
                ],
            ),

            ft.Container(height=25),

            nombre,

            ft.Container(height=12),

            correo,

            ft.Container(height=12),

            password,

            ft.Container(height=12),

            confirmar,

            ft.Container(height=25),

            ft.ElevatedButton(
                "Crear cuenta",
                width=420,
                height=58,
                bgcolor=TURQUESA,
                color=AZUL_OSCURO,
            ),

            ft.Container(height=20),

            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "¿Ya tienes cuenta?",
                        color=GRIS_TEXTO,
                    ),

                    ft.TextButton(
                        "Iniciar sesión",
                    ),
                ],
            ),
        ],
    )

    # =========================
    # PANEL DERECHO
    # =========================

    panel_derecho = ft.Container(
        expand=6,
        bgcolor="#F1F5F9",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=560,
                    padding=40,
                    bgcolor=BLANCO,
                    border_radius=25,
                    shadow=ft.BoxShadow(
                        blur_radius=30,
                        spread_radius=1,
                        color="#22000000",
                    ),
                    content=formulario,
                )
            ],
        ),
    )

    # =========================
    # VISTA
    # =========================

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
    page.update()