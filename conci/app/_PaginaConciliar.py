import flet as ft
from utils import acortar_string


class PaginaConciliar(ft.UserControl):
    def __init__(self, page: ft.Page, procesar):
        self.dialogo_archivo_xls = ft.FilePicker(on_result=self.agregar_planilla)
        self.dialogo_carpeta = ft.FilePicker(on_result=self.agregar_carpeta)
        self.app_page = page
        self.app_page.overlay.append(self.dialogo_archivo_xls)
        self.app_page.overlay.append(self.dialogo_carpeta)

        self.acumulado_ruta = ""
        self.carpeta_guardado_ruta = ""
        self.acumulado_etiqueta = ft.Text("")
        self.guardado_etiqueta = ft.Text("")

        self.conci_boton = ft.Container(
            content=ft.FilledButton(text="Procesar", on_click=self.conciliar),
            alignment=ft.alignment.bottom_right,
            expand=True,
        )
        self.acumulado_opcion = ft.Switch(
            label="Agregar acumulado", value=False, on_change=self.estado_switch
        )

        self.elegir_archivo = ft.ElevatedButton(
            text="Seleccionar acumulado",
            on_click=self.seleccionar_archivo,
            width=200,
            disabled=True,
        )

        self.elegir_carpeta = ft.ElevatedButton(
            text="Seleccionar carpeta", on_click=self.seleccionar_carpeta, width=200
        )

        self.archivo_acumulado = ft.Row(
            controls=[self.elegir_archivo, self.acumulado_etiqueta]
        )

        self.carpeta_guardado = ft.Row(
            controls=[self.elegir_carpeta, self.guardado_etiqueta]
        )

        self.procesar = procesar

        super().__init__()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.acumulado_opcion,
                    self.archivo_acumulado,
                    self.carpeta_guardado,
                    self.conci_boton,
                ]
            ),
            expand=True,
            margin=20,
        )

    def conciliar(self, _e):
        self.procesar()

    def seleccionar_carpeta(self, _e):
        self.dialogo_carpeta.get_directory_path(
            dialog_title="Seleccionar carpeta de guardados"
        )

    def agregar_carpeta(self, e: ft.FilePickerResultEvent):
        try:
            self.carpeta_guardado_ruta = e.path
            self.guardado_etiqueta.value = acortar_string(
                self.carpeta_guardado_ruta, 40
            )
            self.app_page.update()
            super().update()
        except TypeError:
            print("No se selecciono carpeta")
            pass

    def seleccionar_archivo(self, _e):
        self.dialogo_archivo_xls.pick_files(
            dialog_title="Seleccionar planilla de acumulados",
            allowed_extensions=["xlsx"],
        )

    def agregar_planilla(self, e: ft.FilePickerResultEvent):
        try:
            archivo = e.files[0]
            self.acumulado_etiqueta.value = archivo.name
            self.acumulado_ruta = archivo.path
            self.app_page.update()
            super().update()
        except TypeError:
            print("No se selecciono archivo")
            pass

    def estado_switch(self, _e):
        self.elegir_archivo.disabled = not self.acumulado_opcion.value
        self.elegir_archivo.update()
        self.app_page.update()
        super().update()
