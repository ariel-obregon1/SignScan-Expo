import flet as ft

from screens.welcome_screen import screen_welcome
from screens.sign_in import screen_signin
from screens.sign_up import screen_signup
from screens.dashboard import screen_dashboard
from screens.personalize_profile import screen_personalizeprofile
from screens.translator import screen_translator


def main(page: ft.Page):
    page.title = "SignScan"

    page.padding = 0
    page.spacing = 0
    page.assets_dir = "assets"

    page.window.full_screen = 1280
    def route_change(e):
        page.clean()

        if page.route == "/":
            screen_welcome(page)

        elif page.route == "/login":
            screen_signin(page)

        elif page.route == "/crear-cuenta":
            screen_signup(page)

        elif page.route == "/dashboard":
            screen_dashboard(page)

        elif page.route == "/perfil":
            screen_personalizeprofile(page)

        elif page.route == "/translator":
            screen_translator(page)

        else:
            screen_welcome(page)

        page.update()

    page.on_route_change = route_change

    page.go("/")


if __name__ == "__main__":
    ft.run(main)