# main.py

import flet as ft

from ui import SecretDiaryApp


def main(page: ft.Page):
    app = SecretDiaryApp(page)
    app.start()


if __name__ == "__main__":
    ft.run(main)