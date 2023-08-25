import flet as ft


class PaginaAjustes(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        return ft.Container(
            content=ft.Text(value="En desarrollo"),
            alignment=ft.alignment.center,
            expand=True,
        )
