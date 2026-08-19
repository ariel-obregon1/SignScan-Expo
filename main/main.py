"""
Punto de entrada de la aplicación SignScan — main.py

Este archivo es el que hay que ejecutar para abrir la app completa:

    python main.py

Su única responsabilidad es el ENRUTADO: decidir qué pantalla de la
carpeta screens/ se dibuja según la ruta actual (page.route), y limpiar
lo anterior antes de dibujar lo siguiente. Las pantallas no se conocen
entre ellas: solo llaman a page.go("/otra-ruta") y este módulo se
encarga del resto.

Cómo funciona el enrutado en Flet 0.80+ (importante):

    page.go(ruta) NO llama directamente al manejador on_route_change.
    Le pide al cliente que empuje la ruta, y el cliente solo devuelve el
    evento route_change si la ruta CAMBIA de verdad. Como la app arranca
    ya en "/", llamar a page.go("/") al inicio no cambiaba nada, no se
    disparaba ningún evento y no se dibujaba ninguna pantalla: la
    ventana se quedaba en negro. Por eso la primera pantalla se dibuja
    llamando a render_route() directamente (ver el final de main()).

Mapa de rutas -> pantallas: ver el diccionario ROUTES más abajo.

Requisitos: flet >= 0.80. Con flet 0.28 este archivo ni siquiera
arranca, porque ft.run() no existe en esa versión.
"""

import flet as ft

import database

from screens.welcome_screen import screen_welcome
from screens.sign_up import screen_signup
from screens.sign_in import screen_signin
from screens.personalize_profile import screen_personalizeprofile
from screens.dashboard import screen_dashboard
from screens.community import screen_community

# Ruta que se abre al arrancar y a la que se cae si page.route viene
# vacío por lo que sea.
DEFAULT_ROUTE = "/"

# ---- Colores (la misma paleta que usan las pantallas) ----
DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"
WHITE = "#FFFFFF"


# ------------------------------------------------------------------
# Traductor (se importa solo cuando hace falta)
#
# screens/translator.py arrastra OpenCV y MediaPipe (y Keras en la
# primera predicción). Importarlo aquí al arrancar haría lenta la app y
# la rompería entera en una máquina donde falten esos paquetes. Por eso
# se importa la primera vez que se abre /scan, y el resto de la app
# funciona igual aunque el traductor no se pueda cargar.
# ------------------------------------------------------------------
_translator = {"screen": None, "stop": None, "error": None}


def _load_translator():
    """Importa screens/translator.py bajo demanda, una sola vez.

    El resultado (haya funcionado o no) se guarda en el diccionario
    _translator, así que el import pesado ocurre como mucho una vez por
    ejecución: si falló, tampoco se reintenta en cada visita a /scan.

    Returns:
        El diccionario _translator, con:
            "screen" -> la función screen_translator, o None si falló.
            "stop"   -> la función stop_active_translator, o None.
            "error"  -> la excepción del import fallido, o None.
    """
    if _translator["screen"] is None and _translator["error"] is None:
        try:
            from screens.translator import screen_translator, stop_active_translator

            _translator["screen"] = screen_translator
            _translator["stop"] = stop_active_translator
        except Exception as ex:  # faltan paquetes de cámara/IA, modelo...
            _translator["error"] = ex
    return _translator


def stop_active_translator():
    """Apaga la cámara si el traductor se quedó encendido.

    No hace nada si el traductor nunca llegó a importarse, así que es
    seguro llamarla en cada cambio de ruta y al cerrar la ventana. Es lo
    que evita que la ventana de OpenCV siga abierta (y la webcam
    encendida) después de salir de /scan.

    Los errores se ignoran a propósito: apagar la cámara nunca debe
    impedir que el usuario cambie de pantalla o cierre la app.
    """
    stop = _translator["stop"]
    if stop is not None:
        try:
            stop()
        except Exception:
            pass


# ------------------------------------------------------------------
# Pantalla de aviso (para secciones que aún no tienen pantalla propia)
# ------------------------------------------------------------------

def _screen_notice(page: ft.Page, title: str, message: str, detail: str | None = None):
    """Dibuja una pantalla simple con un título, un mensaje y un botón.

    Se usa para dos cosas distintas: avisar de que una sección todavía
    no existe, y explicar por qué no se pudo cargar el traductor. Sigue
    la paleta del resto de la app para que no parezca un error del
    sistema.

    Args:
        page: la página de Flet sobre la que se dibuja.
        title: título grande, en blanco (admite emojis).
        message: explicación en turquesa, centrada.
        detail: texto pequeño y gris opcional, pensado para el mensaje
            técnico de una excepción. Si es None, no se muestra.
    """
    page.title = "SignScan"
    page.bgcolor = ft.Colors.GREY_300
    page.padding = 0

    controls = [
        ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=WHITE,
                text_align=ft.TextAlign.CENTER),
        ft.Container(height=10),
        ft.Text(message, size=16, color=TURQUOISE, width=520,
                text_align=ft.TextAlign.CENTER),
    ]

    if detail:
        controls += [
            ft.Container(height=10),
            ft.Text(detail, size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                    width=520, text_align=ft.TextAlign.CENTER),
        ]

    controls += [
        ft.Container(height=30),
        ft.ElevatedButton(
            "Back to home",
            width=280,
            height=50,
            bgcolor=TURQUOISE,
            color=DARK_BLUE,
            on_click=lambda e: page.go("/dashboard"),
        ),
    ]

    page.controls.clear()
    page.add(
        ft.Container(
            expand=True,
            bgcolor=MAIN_BLUE,
            padding=40,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
            ),
        )
    )


def screen_scan(page: ft.Page):
    """Pantalla de la ruta /scan: el traductor de señas.

    Intenta cargar screens/translator.py y dibujarlo. Si el import falló
    (falta OpenCV, MediaPipe, etc.), en su lugar muestra una pantalla
    explicando qué instalar, en vez de dejar la app rota o devolver al
    usuario a la pantalla de bienvenida sin explicación.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    translator = _load_translator()

    if translator["screen"] is not None:
        translator["screen"](page)
        return

    _screen_notice(
        page,
        "📷  Scan Signs",
        "The translator needs the camera and AI packages.\n"
        "Install them with:  pip install -r requirements.txt",
        detail=str(translator["error"]),
    )


def screen_coming_soon(page: ft.Page):
    """Marcador para las secciones que todavía no están hechas.

    Lo usan /learn, /community y /video, que tienen botón en el menú del
    dashboard pero aún no tienen pantalla. Antes esas rutas caían en la
    pantalla de bienvenida, y parecía que la app había cerrado la sesión
    sola.

    Args:
        page: la página de Flet sobre la que se dibuja.
    """
    _screen_notice(
        page,
        "🚧  Coming soon",
        "This section is still under construction.",
    )


# Mapa de rutas -> función que dibuja esa pantalla. Toda la navegación
# de la app pasa por aquí: las pantallas solo llaman a page.go(ruta).
ROUTES = {
    "/": screen_welcome,
    "/create-account": screen_signup,
    "/login": screen_signin,
    "/profile": screen_personalizeprofile,
    "/dashboard": screen_dashboard,
    "/scan": screen_scan,
    "/community": screen_community,
    # Entradas del menú lateral del dashboard que todavía no tienen
    # pantalla propia. Se listan para que muestren un aviso en lugar de
    # devolver al usuario a la bienvenida sin decir nada.
    "/learn": screen_coming_soon,
    "/video": screen_coming_soon,
}


def main(page: ft.Page):
    """Arranca la aplicación: la llama Flet una vez por cada ventana.

    Se encarga, por este orden, de:
        1. crear la base de datos si no existía (database.init_db),
        2. configurar la ventana (título, sin márgenes, pantalla
           completa y aviso antes de cerrar),
        3. registrar el manejador de cambios de ruta,
        4. dibujar la PRIMERA pantalla a mano, sin esperar al evento.

    Args:
        page: la página que crea Flet. Todo el estado de la interfaz
            cuelga de ella.
    """
    database.init_db()

    page.title = "SignScan"
    page.padding = 0
    page.spacing = 0
    page.window.full_screen = True

    def render_route(route: str):
        """Borra lo que hay en pantalla y dibuja la ruta indicada.

        Es el único sitio de la app donde se cambia de pantalla. El
        orden importa: primero apagar la cámara, luego limpiar los
        controles y solo entonces dejar que la pantalla nueva se pinte.

        Args:
            route: ruta a dibujar. Si no está en ROUTES se cae a la
                pantalla de bienvenida, para que una ruta inventada
                nunca deje la ventana vacía.
        """
        # Por si veníamos de la pantalla de traducción: apagar la cámara
        # antes de cambiar. Si no había nada corriendo no hace nada, así
        # que es seguro llamarlo en cada cambio de ruta.
        stop_active_translator()

        page.controls.clear()
        handler = ROUTES.get(route, screen_welcome)
        handler(page)
        page.update()

    def route_change(e: ft.RouteChangeEvent):
        """Responde al evento de cambio de ruta que envía el cliente.

        Se dispara con cada page.go() que hace cualquier pantalla, y
        también cuando el usuario usa el botón "atrás" del navegador en
        la versión web.

        Args:
            e: evento de Flet. No se usa: la ruta buena está siempre en
                page.route.
        """
        render_route(page.route or DEFAULT_ROUTE)

    def window_event(e: ft.WindowEvent):
        """Atiende los eventos de la ventana del sistema operativo.

        Solo interesa el cierre: como page.window.prevent_close está
        activo, la ventana no se cierra sola y hay que destruirla a
        mano, aprovechando para apagar antes la cámara.

        Args:
            e: evento de ventana de Flet (mover, redimensionar,
                cerrar...).
        """
        if e.type == ft.WindowEventType.CLOSE:
            stop_active_translator()
            page.run_task(page.window.destroy)

    page.window.prevent_close = True
    page.window.on_event = window_event

    page.on_route_change = route_change

    # Primera pantalla.
    #
    # Se dibuja directamente en vez de con page.go(): la navegación solo
    # dispara on_route_change cuando la ruta CAMBIA de verdad, y la app
    # ya arranca en "/". Así que page.go("/") no cambiaba nada y nunca
    # se construía ninguna pantalla: esa era la ventana en negro. A
    # partir de aquí, on_route_change se ocupa de cada page.go().
    render_route(page.route or DEFAULT_ROUTE)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")