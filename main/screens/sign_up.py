# screens/sign_up.py

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
    page.go("/")


# =========================
# SCREEN CREAR CUENTA
# =========================

def screen_signup(page):

    page.controls.clear()


    # =========================
    # INPUTS
    # =========================

    estilo_input = {
        "width": 420,
        "height": 52,
        "filled": True,
        "bgcolor": BLANCO,
        "border_color": "#CBD5E1",
        "focused_border_color": TURQUESA,
        "color": "#0F172A",
        "text_size": 15,
        "border_radius": 14,
    }


    nombre = ft.TextField(
        label="Nombre completo",
        hint_text="Ingresa tu nombre",
        **estilo_input
    )


    correo = ft.TextField(
        label="Correo electrónico",
        hint_text="ejemplo@email.com",
        **estilo_input
    )


    password = ft.TextField(
        label="Contraseña",
        hint_text="Mínimo 8 caracteres",
        password=True,
        can_reveal_password=True,
        **estilo_input
    )


    confirmar = ft.TextField(
        label="Confirmar contraseña",
        hint_text="Repite tu contraseña",
        password=True,
        can_reveal_password=True,
        **estilo_input
    )


    # =========================
    # PANEL IZQUIERDO
    # =========================

    panel_izquierdo = ft.Container(

        expand=4,
        bgcolor=AZUL_PRINCIPAL,
        padding=40,

        content=ft.Column(

            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[


                ft.Container(

                    bgcolor=BLANCO,
                    border_radius=25,
                    padding=20,

                    shadow=ft.BoxShadow(
                        blur_radius=20,
                        color="#30000000",
                    ),

                    content=ft.Image(
                        src="logo.png",
                        width=170,
                    ),
                ),



                ft.Container(height=15),



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
                    text_align="center",
                ),

            ]
        )
    )



    # =========================
    # BOTONES REDES
    # =========================

    redes = ft.Row(

        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,

        controls=[


            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1,"#E2E8F0"),
                border_radius=14,

                content=ft.Text(
                    "G",
                    size=24,
                ),

                alignment=ft.alignment.center,
            ),



            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1,"#E2E8F0"),
                border_radius=14,

                content=ft.Text(
                    "🍎",
                    size=22,
                ),

                alignment=ft.alignment.center,
            ),



            ft.Container(
                width=65,
                height=65,
                border=ft.border.all(1,"#E2E8F0"),
                border_radius=14,

                content=ft.Text(
                    "f",
                    size=26,
                ),

                alignment=ft.alignment.center,
            ),

        ]
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



            ft.Text(
                "Crear cuenta",
                size=32,
                weight="bold",
                color="#0F172A",
            ),



            ft.Text(
                "Únete a la comunidad SignScan",
                size=16,
                color=GRIS_TEXTO,
            ),



            ft.Container(height=15),



            redes,



            ft.Container(height=15),



            ft.Row(

                alignment=ft.MainAxisAlignment.CENTER,

                controls=[


                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),



                    ft.Text(
                        "O con email",
                        size=13,
                        color=GRIS_CLARO,
                    ),



                    ft.Container(
                        width=130,
                        height=1,
                        bgcolor="#E5E7EB",
                    ),

                ]
            ),



            ft.Container(height=15),



            nombre,


            ft.Container(height=8),


            correo,


            ft.Container(height=8),


            password,


            ft.Container(height=8),


            confirmar,


            ft.Container(height=15),



            ft.ElevatedButton(

                "Crear cuenta",

                width=420,
                height=58,

                bgcolor=TURQUESA,
                color=AZUL_OSCURO,

                on_click=lambda e: page.go("/perfil")

            ),



            ft.Container(height=15),



            ft.Row(

                alignment=ft.MainAxisAlignment.CENTER,

                controls=[


                    ft.Text(
                        "¿Ya tienes cuenta?",
                        color=GRIS_TEXTO,
                    ),



                    ft.TextButton(

                        "Iniciar sesión",

                        on_click=lambda e: page.go("/login")

                    ),

                ]
            ),

        ]
    )



    # =========================
    # PANEL DERECHO
    # =========================

    panel_derecho = ft.Container(

        expand=6,
        bgcolor="#F1F5F9",

        content=ft.Column(

            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[


                ft.Container(

                    width=520,
                    padding=30,

                    bgcolor=BLANCO,
                    border_radius=25,

                    shadow=ft.BoxShadow(
                        blur_radius=25,
                        color="#22000000",
                    ),

                    content=formulario,

                )

            ]
        )
    )



    # =========================
    # VISTA FINAL
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

            ]

        )
    )



    page.add(vista)
    page.update()
if __name__ == "__main__":
    ft.run(screen_signup)