import flet as ft
from _ElementoTabla import ElementoTabla


class TablaPlanillas(ft.UserControl):
    def __init__(self, page: ft.Page, origen: str):
        self.app_page = page
        self.archivos = list()
        self.lista = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.add_button = ft.IconButton(
            icon=ft.icons.ADD_CIRCLE,
            on_click=self.seleccionar_archivo,
            icon_color=ft.colors.SURFACE_TINT,
            scale=1.25,
        )
        self.dialogo_archivo = ft.FilePicker(on_result=self.agregar_archivo)
        self.app_page.overlay.append(self.dialogo_archivo)
        self.origen = origen
        contenedor_lista = ft.Container(
            content=self.lista, margin=10, alignment=ft.alignment.top_left
        )
        self.lista_card = ft.Card(content=contenedor_lista)
        super().__init__()

    def build(self):
        contenedor_button = ft.Container(
            content=self.add_button,
            tooltip="Agregar tabla",
            alignment=ft.alignment.center_right,
        )
        return ft.Container(
            content=ft.Column(
                controls=[self.lista_card, contenedor_button],
                scroll=ft.ScrollMode.HIDDEN,
                expand=True,
            ),
            margin=20,
        )

    def eliminar_tabla(self, elemento_tabla: ElementoTabla):
        self.lista.controls.remove(elemento_tabla)
        self.archivos.remove(elemento_tabla.ruta_archivo)
        super().update()

    def agregar_archivo(self, e: ft.FilePickerResultEvent):
        try:
            archivo = e.files[0]
            self.lista.controls.append(
                ElementoTabla(archivo.name, archivo.path, self.eliminar_tabla)
            )
            self.archivos.append(archivo.path)
            super().update()
        except TypeError:
            print("No se selecciono archivo")
            pass

    def seleccionar_archivo(self, _e):
        self.dialogo_archivo.pick_files(
            dialog_title=f"Seleccionar tabla {self.origen}",
            allowed_extensions=["xlsx"],
        )
