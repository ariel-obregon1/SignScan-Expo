import flet as ft

import database

from screens.welcome_screen import screen_welcome
from screens.sign_up import screen_signup
from screens.sign_in import screen_signin
from screens.personalize_profile import screen_personalizeprofile
from screens.dashboard import screen_dashboard

DEFAULT_ROUTE = "/"

# ---- Colors (same palette as the screens) ----
DARK_BLUE = "#001845"
MAIN_BLUE = "#002060"
TURQUOISE = "#40E0D0"
WHITE = "#FFFFFF"


# ------------------------------------------------------------------
# Translator (imported on demand)
#
# screens/translator.py pulls in OpenCV + MediaPipe (and Keras on the
# first prediction). Importing it here at start-up would slow the app
# down, and would crash it on a machine where those packages are not
# installed. So it is imported the first time /scan is opened, and the
# rest of the app keeps working either way.
# ------------------------------------------------------------------
_translator = {"screen": None, "stop": None, "error": None}


def _load_translator():
    """Imports screens/translator.py on demand. Returns the cache dict;
    ["error"] holds the exception when the import failed."""
    if _translator["screen"] is None and _translator["error"] is None:
        try:
            from screens.translator import screen_translator, stop_active_translator

            _translator["screen"] = screen_translator
            _translator["stop"] = stop_active_translator
        except Exception as ex:  # camera/AI packages missing, model not found...
            _translator["error"] = ex
    return _translator


def stop_active_translator():
    """Turns the camera off if the translator left it running. It's a
    no-op when the translator was never opened, so it's safe to call on
    every route change."""
    stop = _translator["stop"]
    if stop is not None:
        try:
            stop()
        except Exception:
            pass


# ------------------------------------------------------------------
# Placeholder screen (sections without a screen of their own yet)
# ------------------------------------------------------------------

def _screen_notice(page: ft.Page, title: str, message: str, detail: str | None = None):
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
    """/scan — the sign translator. Falls back to an explanatory screen
    when the camera/AI packages are not available."""
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
    _screen_notice(
        page,
        "🚧  Coming soon",
        "This section is still under construction.",
    )


ROUTES = {
    "/": screen_welcome,
    "/create-account": screen_signup,
    "/login": screen_signin,
    "/profile": screen_personalizeprofile,
    "/dashboard": screen_dashboard,
    "/scan": screen_scan,
    # Sidebar entries of the dashboard that don't have their own screen
    # yet. They are listed so they show a placeholder instead of
    # silently sending the user back to the welcome screen.
    "/learn": screen_coming_soon,
    "/community": screen_coming_soon,
    "/video": screen_coming_soon,
}


def main(page: ft.Page):
    database.init_db()

    page.title = "SignScan"
    page.padding = 0
    page.spacing = 0
    page.window.full_screen = True

    def render_route(route: str):
        # In case we were on the translation screen: turn off the
        # camera before switching screens. It's a no-op if nothing was
        # running, so it's safe to call on every route change.
        stop_active_translator()

        page.controls.clear()
        handler = ROUTES.get(route, screen_welcome)
        handler(page)
        page.update()

    def route_change(e: ft.RouteChangeEvent):
        render_route(page.route or DEFAULT_ROUTE)

    def window_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.CLOSE:
            stop_active_translator()
            page.run_task(page.window.destroy)

    page.window.prevent_close = True
    page.window.on_event = window_event

    page.on_route_change = route_change

    # First screen.
    #
    # It is drawn directly instead of with page.go(): navigation only
    # fires on_route_change when the route actually *changes*, and the
    # app already starts on "/". page.go("/") therefore changed nothing
    # and no screen was ever built — that was the black window. From
    # here on, on_route_change takes care of every page.go() in the app.
    render_route(page.route or DEFAULT_ROUTE)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
