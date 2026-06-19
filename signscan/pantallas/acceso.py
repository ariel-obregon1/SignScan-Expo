# pantallas/acceso.py

import flet as ft

from componentes.colores import (
    AZUL,
    AZUL_OSCURO,
    TURQUESA,
    BLANCO,
    FONDO_CLARO,
    GRIS,
    GRIS_BORDE,
    TEXTO_GRIS,
    TEXTO_SUAVE,
    ROJO,
)
from componentes.botones import boton_principal
from componentes.base_datos import (
    registrar_usuario,
    iniciar_sesion,
    guardar_historial,
)


def campo_texto(pista, password=False):
    return ft.TextField(
        hint_text=pista,
        width=390,
        height=58,
        bgcolor=GRIS,
        border_radius=18,
        border_color=GRIS,
        focused_border_color=TURQUESA,
        password=password,
        can_reveal_password=password,
        color="#1F2122",
        text_size=17,
        hint_style=ft.TextStyle(
            color=TEXTO_SUAVE,
            size=17,
        ),
    )


def panel_izquierdo():
    return ft.Container(
        width=595,
        gradient=ft.LinearGradient(
            colors=[AZUL_OSCURO, AZUL, TURQUESA],
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
        ),
        content=ft.Stack(
            controls=[
                ft.Container(
                    width=330,
                    height=330,
                    bgcolor="#FFFFFF10",
                    border_radius=170,
                    right=-120,
                    top=-140,
                ),
                ft.Container(
                    width=270,
                    height=270,
                    bgcolor="#FFFFFF10",
                    border_radius=140,
                    left=-120,
                    bottom=-110,
                ),
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(src="assets/logo.png", width=180),
                        ft.Container(height=35),
                        ft.Text(
                            "SignScan",
                            size=50,
                            color=BLANCO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "Comunicación accesible para todos",
                            size=22,
                            color=TURQUESA,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            ],
        ),
    )


def boton_social(contenido, color_texto):
    return ft.Container(
        width=95,
        height=55,
        bgcolor=GRIS,
        border_radius=16,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            contenido,
            size=22,
            color=color_texto,
            weight=ft.FontWeight.BOLD,
        ),
    )


def layout_acceso(titulo, subtitulo, campos, mensaje_error, boton_accion, link, ir):
    return ft.Row(
        expand=True,
        spacing=0,
        controls=[
            panel_izquierdo(),
            ft.Container(
                expand=True,
                bgcolor=FONDO_CLARO,
                content=ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.TextButton(
                            "←  Volver",
                            on_click=lambda e: ir("bienvenida"),
                            style=ft.ButtonStyle(color=AZUL),
                        ),
                        ft.Container(height=15),
                        ft.Container(
                            width=480,
                            padding=35,
                            bgcolor=BLANCO,
                            border_radius=28,
                            shadow=ft.BoxShadow(
                                blur_radius=35,
                                color="#00000018",
                                offset=ft.Offset(0, 10),
                            ),
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    ft.Text(
                                        titulo,
                                        size=32,
                                        color=AZUL,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        subtitulo,
                                        color=TEXTO_GRIS,
                                        size=16,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Container(height=16),
                                    *campos,
                                    mensaje_error,
                                    ft.Container(height=10),
                                    boton_accion,
                                    ft.Container(height=10),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                width=120,
                                                height=1,
                                                bgcolor=GRIS_BORDE,
                                            ),
                                            ft.Text(
                                                "O continúa con",
                                                color=TEXTO_SUAVE,
                                                size=13,
                                            ),
                                            ft.Container(
                                                width=120,
                                                height=1,
                                                bgcolor=GRIS_BORDE,
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=15,
                                        controls=[
                                            boton_social("G", "#EA4335"),
                                            boton_social("🍎", AZUL),
                                            boton_social("f", "#1877F2"),
                                        ],
                                    ),
                                    link,
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ],
    )


def pantalla_crear_cuenta(page, ir, usuario, estado, mensaje):
    nombre = campo_texto("Nombre completo")
    correo = campo_texto("Correo electrónico")
    password = campo_texto("Contraseña", True)
    confirmar = campo_texto("Confirmar contraseña", True)

    mensaje_error = ft.Text("", color=ROJO, size=12)

    def guardar_cuenta(e):
        if not nombre.value or not correo.value or not password.value or not confirmar.value:
            mensaje_error.value = "Rellena todos los campos."
        elif "@" not in correo.value:
            mensaje_error.value = "Correo electrónico no válido."
        elif password.value != confirmar.value:
            mensaje_error.value = "Las contraseñas no coinciden."
        else:
            ok, respuesta = registrar_usuario(
                nombre.value,
                correo.value,
                password.value,
            )

            if ok:
                usuario["nombre"] = nombre.value
                usuario["correo"] = correo.value.strip().lower()
                usuario["avatar"] = "👨"
                usuario["foto"] = ""

                guardar_historial(
                    usuario["correo"],
                    "Cuenta",
                    "Cuenta creada en SignScan",
                )

                ir("perfil_inicial")
                return

            mensaje_error.value = respuesta

        page.update()

    return layout_acceso(
        "Crear cuenta",
        "Únete a la comunidad SignScan",
        [nombre, correo, password, confirmar],
        mensaje_error,
        boton_principal(
            "Crear cuenta",
            guardar_cuenta,
            390,
            58,
            TURQUESA,
            AZUL,
        ),
        ft.TextButton(
            "¿Ya tienes cuenta? Iniciar sesión",
            on_click=lambda e: ir("iniciar_sesion"),
        ),
        ir,
    )


def pantalla_iniciar_sesion(page, ir, usuario, estado, mensaje):
    correo = campo_texto("Correo electrónico")
    password = campo_texto("Contraseña", True)

    mensaje_error = ft.Text("", color=ROJO, size=12)

    def validar_login(e):
        datos_usuario = iniciar_sesion(
            correo.value,
            password.value,
        )

        if datos_usuario:
            usuario["nombre"] = datos_usuario["nombre"]
            usuario["correo"] = datos_usuario["correo"]
            usuario["avatar"] = datos_usuario["avatar"]
            usuario["foto"] = datos_usuario["foto"]

            guardar_historial(
                usuario["correo"],
                "Inicio de sesión",
                "Acceso correcto a la app",
            )

            ir("inicio")
            return

        mensaje_error.value = "Correo o contraseña incorrectos."
        page.update()

    return layout_acceso(
        "Bienvenido a SignScan",
        "Inicia sesión para continuar",
        [
            correo,
            password,
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.TextButton(
                        "¿Olvidaste tu contraseña?",
                        on_click=lambda e: mensaje(
                            "Recuperación de contraseña próximamente."
                        ),
                    ),
                ],
            ),
        ],
        mensaje_error,
        boton_principal(
            "Iniciar sesión",
            validar_login,
            390,
            58,
            TURQUESA,
            AZUL,
        ),
        ft.TextButton(
            "¿No tienes cuenta? Crear cuenta",
            on_click=lambda e: ir("crear_cuenta"),
        ),
        ir,
    )