import flet as ft

from componentes.base_datos import crear_base_datos

from pantallas.splash import pantalla_splash
from pantallas.bienvenida import pantalla_bienvenida
from pantallas.acceso import pantalla_crear_cuenta, pantalla_iniciar_sesion
from pantallas.perfil_inicial import pantalla_perfil_inicial
from pantallas.inicio import pantalla_inicio
from pantallas.aprender import pantalla_aprender
from pantallas.leccion import pantalla_leccion
from pantallas.comunidad import pantalla_comunidad
from pantallas.escanear import pantalla_escanear
from pantallas.video import pantalla_video
from pantallas.ia import pantalla_ia
from pantallas.historial import pantalla_historial
from pantallas.perfil import pantalla_perfil

from pantallas.ajustes import (
    pantalla_notificaciones,
    pantalla_idioma,
    pantalla_apariencia,
    pantalla_privacidad,
    pantalla_soporte,
)


def main(page: ft.Page):
    crear_base_datos()

    page.title = "SignScan"
    page.window_width = 1450
    page.window_height = 860
    page.window_maximized = True
    page.padding = 0
    page.spacing = 0

    usuario = {
        "nombre": "",
        "correo": "",
        "avatar": "👨",
        "foto": "",
    }

    estado = {
        "vista": "splash",
        "leccion_actual": "abecedario",
        "carta_actual": 0,
        "carta_volteada": False,
    }

    def mensaje(texto):
        page.snack_bar = ft.SnackBar(content=ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    def ir(vista):
        page.controls.clear()
        estado["vista"] = vista

        rutas = {
            "splash": pantalla_splash,
            "bienvenida": pantalla_bienvenida,
            "crear_cuenta": pantalla_crear_cuenta,
            "iniciar_sesion": pantalla_iniciar_sesion,
            "perfil_inicial": pantalla_perfil_inicial,
            "inicio": pantalla_inicio,
            "aprender": pantalla_aprender,
            "leccion": pantalla_leccion,
            "comunidad": pantalla_comunidad,
            "escanear": pantalla_escanear,
            "video": pantalla_video,
            "ia": pantalla_ia,
            "historial": pantalla_historial,
            "perfil": pantalla_perfil,
            "notificaciones": pantalla_notificaciones,
            "idioma": pantalla_idioma,
            "apariencia": pantalla_apariencia,
            "privacidad": pantalla_privacidad,
            "soporte": pantalla_soporte,
        }

        pantalla = rutas.get(vista, pantalla_splash)
        page.add(pantalla(page, ir, usuario, estado, mensaje))
        page.update()

    ir("splash")


ft.app(target=main, assets_dir=".")