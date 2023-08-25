import flet as ft


class ElementoTabla(ft.UserControl):
    def __init__(self, nombre_archivo: str, ruta_archivo: str, eliminar_elemento):
        super().__init__()
        self.nombre_archivo = nombre_archivo
        self.ruta_archivo = ruta_archivo
        self.eliminar_elemento = eliminar_elemento

    def build(self):
        nombre_etiqueta = ft.Container(
            width=300,
            content=ft.Text(
                value=self.nombre_archivo, style=ft.TextThemeStyle.LABEL_LARGE
            ),
        )
        borrar_ruta_button = ft.IconButton(
            icon=ft.icons.DELETE, tooltip="Eliminar tabla", on_click=self.click_eliminar
        )
        elemento = ft.ListTile(
            title=nombre_etiqueta, trailing=borrar_ruta_button, expand=True
        )
        return elemento

    def click_eliminar(self, _e):
        self.eliminar_elemento(self)
