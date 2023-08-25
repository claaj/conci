import os
import flet as ft
import polars as pl
from conci.app._PaginaAcercaDe import PaginaAcercaDe
from conci.app._PaginaAjustes import PaginaAjustes
from conci.app._PaginaConciliar import PaginaConciliar
from conci.app._TablaPlanillas import TablaPlanillas
from conci.conciliar.utils import obtener_fecha_mas_reciente
from conci.conciliar.conciliar import procesar


def main(page: ft.Page):
    def post_proceso(
        df_afip: pl.DataFrame,
        df_tango: pl.DataFrame,
        df_acumulado: pl.DataFrame,
        nombre_carpeta: str,
        carpeta_guardado: str,
    ):
        carpeta_guardado_conci = (
            f"{carpeta_guardado}/{nombre_carpeta}/{obtener_fecha_mas_reciente(df_afip)}"
        )

        try:
            os.makedirs(carpeta_guardado_conci)
        except FileExistsError:
            pass

        df_afip.write_excel(f"{carpeta_guardado_conci}/afip.xlsx")
        df_tango.write_excel(f"{carpeta_guardado_conci}/tango.xlsx")
        df_acumulado.write_excel(f"{carpeta_guardado_conci}/acumulado.xlsx")

        texto_banner.value = f"{nombre_carpeta} Procesadas"
        page.banner.open = True
        page.update()

    def banner_mensaje(mensaje: str, bg_color: ft.colors, leading: ft.Icon = None):
        texto_banner.value = mensaje
        texto_banner.color = ft.colors.BLACK
        page.banner.leading = leading
        page.banner.bgcolor = bg_color
        page.banner.open = True
        page.update()

    def proceso_exitoso():
        banner_mensaje(
            "Se procesaron correctamente las planillas.",
            ft.colors.GREEN_200,
            ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN_600, size=35),
        )

    def proceso_shape_error():
        banner_mensaje(
            "Fallo el procesamiento de las planillas.",
            ft.colors.RED_200,
            ft.Icon(
                ft.icons.ERROR_SHARP,
                color=ft.colors.RED_600,
                size=35,
            ),
        )

    def proceso_file_error():
        banner_mensaje(
            "Archivo/s invalido/s. Vuelva a cargar los archivos e intente nuevamente.",
            ft.colors.RED_200,
            ft.Icon(
                ft.icons.ERROR_SHARP,
                color=ft.colors.RED_600,
                size=35,
            ),
        )

    def proceso_no_arranca():
        banner_mensaje(
            "Debe completar todos los campos para poder operar.",
            ft.colors.AMBER_200,
            ft.Icon(
                ft.icons.WARNING_AMBER_ROUNDED,
                color=ft.colors.AMBER_600,
                size=35,
            ),
        )

    def conciliar_percepciones():
        if (
            len(percep_afip.archivos) > 0
            and len(percep_tango.archivos) > 0
            and percep_conci.carpeta_guardado_ruta != ""
            and (
                not percep_conci.acumulado_opcion.value
                or percep_conci.acumulado_ruta != ""
            )
        ):
            try:
                (df_afip, df_tango, df_acumulado) = procesar(
                    percep_afip.archivos,
                    percep_tango.archivos,
                    percep_conci.acumulado_ruta,
                )

                post_proceso(
                    df_afip,
                    df_tango,
                    df_acumulado,
                    "Percepciones",
                    percep_conci.carpeta_guardado_ruta,
                )
                proceso_exitoso()

            except pl.ShapeError:
                proceso_shape_error()

            except FileNotFoundError:
                proceso_file_error()

        else:
            proceso_no_arranca()

    def conciliar_retenciones():
        print("conciliar retenciones")
        if (
            len(reten_afip.archivos) > 0
            and len(reten_tango.archivos) > 0
            and reten_conci.carpeta_guardado_ruta != ""
            and (
                not reten_conci.acumulado_opcion.value
                or reten_conci.acumulado_ruta != ""
            )
        ):
            try:
                (df_afip, df_tango, df_acumulado) = procesar(
                    reten_afip.archivos,
                    reten_tango.archivos,
                    reten_conci.acumulado_ruta,
                )

                post_proceso(
                    df_afip,
                    df_tango,
                    df_acumulado,
                    "Retenciones",
                    reten_conci.carpeta_guardado_ruta,
                )
                proceso_exitoso()

            except pl.ShapeError:
                proceso_shape_error()

            except FileNotFoundError:
                proceso_file_error()
        else:
            proceso_no_arranca()

    def esconder_elemento(elemento):
        if elemento.visible:
            elemento.visible = False
            page.update()

    def cerrar_banner(_e):
        page.banner.open = False
        page.update()

    def cambiar_navbar(e):
        index_navbar = e.control.selected_index
        match index_navbar:
            case 0:
                esconder_elemento(reten_tabs)
                esconder_elemento(ajustes)
                esconder_elemento(acerca_de)
                percep_tabs.visible = True
                page.update()
            case 1:
                esconder_elemento(percep_tabs)
                esconder_elemento(ajustes)
                esconder_elemento(acerca_de)
                reten_tabs.visible = True
                page.update()
            case 2:
                esconder_elemento(percep_tabs)
                esconder_elemento(reten_tabs)
                esconder_elemento(acerca_de)
                ajustes.visible = True
                page.update()
            case _:
                esconder_elemento(percep_tabs)
                esconder_elemento(reten_tabs)
                esconder_elemento(ajustes)
                acerca_de.visible = True
                page.update()

    page.title = "Conci AFIP - Tango"
    page.horizontal_alignment = "center"
    page.window_width = 550
    page.theme = ft.Theme(color_scheme_seed="200")
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.TABLE_ROWS, label="Percepciones"),
            ft.NavigationDestination(icon=ft.icons.TABLE_ROWS, label="Retenciones"),
            ft.NavigationDestination(icon=ft.icons.SETTINGS, label="Ajustes"),
            ft.NavigationDestination(icon=ft.icons.INFO, label="Acerca de"),
        ],
        on_change=cambiar_navbar,
    )

    texto_banner = ft.Text("")
    page.banner = ft.Banner(
        content=texto_banner,
        actions=[
            ft.IconButton(
                ft.icons.EXPAND_LESS_OUTLINED,
                on_click=cerrar_banner,
                icon_color=ft.colors.BLUE_GREY_500,
            )
        ],
    )

    ajustes = ft.Container(content=PaginaAjustes(), expand=True)
    acerca_de = ft.Container(content=PaginaAcercaDe(), expand=True)

    percep_afip = TablaPlanillas(page, "AFIP")
    percep_tango = TablaPlanillas(page, "Tango")
    percep_conci = PaginaConciliar(page, conciliar_percepciones)

    percep_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="AFIP",
                content=ft.Container(
                    content=percep_afip,
                ),
            ),
            ft.Tab(
                text="Tango",
                content=ft.Container(
                    content=percep_tango,
                ),
            ),
            ft.Tab(
                text="Conciliar",
                content=percep_conci,
            ),
        ],
        expand=True,
    )

    reten_afip = TablaPlanillas(page, "AFIP")
    reten_tango = TablaPlanillas(page, "Tango")
    reten_conci = PaginaConciliar(page, conciliar_retenciones)

    reten_tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="AFIP",
                content=ft.Container(
                    content=reten_afip,
                ),
            ),
            ft.Tab(
                text="Tango",
                content=ft.Container(
                    content=reten_tango,
                ),
            ),
            ft.Tab(
                text="Conciliar",
                content=reten_conci,
            ),
        ],
        expand=1,
    )

    reten_tabs.visible = False
    ajustes.visible = False
    acerca_de.visible = False

    page.add(percep_tabs)
    page.add(reten_tabs)
    page.add(ajustes)
    page.add(acerca_de)
    page.update()
