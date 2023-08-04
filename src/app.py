import os
import tkinter
import customtkinter as ct
import polars as pl
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from conciliador import conciliador
from utils import acortar_string


class App(ct.CTk):
    ruta_afip = ""
    ruta_tango = ""
    ruta_acumulado = ""
    ruta_procesados = ""
    ruta_guardado = ""

    def __init__(self):
        super().__init__()
        ct.set_appearance_mode("Dark")
        self.title("Percepciones AFIP - Tango")
        self.geometry("450x320")

        self.switch_acumulado_var = ct.BooleanVar(value=False)

        self.label_afip = ct.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_tango = ct.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_guardado = ct.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_acumulado = ct.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.button_afip = ct.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla AFIP",
            command=self.set_ruta_afip
        )

        self.button_tango = ct.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla Tango",
            command=self.set_ruta_tango
        )

        self.button_guardado = ct.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir carpeta de guardado",
            command=self.set_ruta_guardado
        )

        self.button_acumulado = ct.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla de acumulados",
            state="disabled",
            command=self.set_ruta_acumulado
        )

        self.switch_acumulado = ct.CTkSwitch(
            master=self,
            text="Agregar tabla de acumulados",
            command=self.switch_acumulado,
            variable=self.switch_acumulado_var,
            onvalue=True,
            offvalue=False,
        )

        self.button_conciliar = ct.CTkButton(
            self,
            height=32,
            text="Conciliar",
            command=self.conciliar
        )

        self.button_afip.grid(row=1, column=1, padx=(20, 5), pady=(10, 10))
        self.label_afip.grid(row=1, column=2, padx=(5, 10), pady=(10, 10))

        self.button_tango.grid(row=2, column=1, padx=(20, 5), pady=(10, 10))
        self.label_tango.grid(row=2, column=2, padx=(5, 10), pady=(10, 10))

        self.button_guardado.grid(row=3, column=1, padx=(20, 5), pady=(10, 10))
        self.label_guardado.grid(row=3, column=2, padx=(5, 10), pady=(10, 10))

        self.button_acumulado.grid(row=4, column=1, padx=(20, 5), pady=(10, 10))
        self.label_acumulado.grid(row=4, column=2, padx=(5, 10), pady=(10, 10))
        self.switch_acumulado.grid(row=5, column=1, padx=(20, 10), pady=(10, 10))

        self.button_conciliar.grid(row=6, column=2, padx=(50, 5), pady=(10, 10))

    def set_ruta_afip(self):
        self.ruta_afip = self._buscar_archivos()
        self.label_afip.configure(text=acortar_string(self.ruta_afip))
        print(self.ruta_afip)

    def set_ruta_tango(self):
        self.ruta_tango = self._buscar_archivos()
        self.label_tango.configure(text=acortar_string(self.ruta_tango))
        print(self.ruta_tango)

    def set_ruta_acumulado(self):
        self.ruta_acumulado = self._buscar_archivos()
        self.label_acumulado.configure(text=acortar_string(self.ruta_acumulado))
        print(self.ruta_acumulado)

    def set_ruta_guardado(self):
        self.ruta_guardado = tkinter.filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Seleccione carpeta de guardado"
        )
        self.label_guardado.configure(text=acortar_string(self.ruta_guardado))
        print(self.ruta_guardado)

    @staticmethod
    def _buscar_archivos() -> str:
        return tkinter.filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Seleccionar archivo",
            filetypes=(
                ("Excel 2007-365", "*.xlsx*"),
                ("Todos", "*.*")))

    def switch_acumulado(self):
        if self.switch_acumulado_var.get():
            self.button_acumulado.configure(state="enabled")
        else:
            self.ruta_acumulado = ""
            self.button_acumulado.configure(state="disabled")

    def conciliar(self):
        if self.ruta_afip != "" and self.ruta_tango != "" and self.ruta_guardado != "" and (
                not self.switch_acumulado_var.get() or self.ruta_acumulado != ""):
            try:
                (tabla_afip, tabla_tango, tabla_acumulado) = conciliador(
                    self.ruta_afip, self.ruta_tango, self.ruta_acumulado)
                tabla_afip.write_excel(self.ruta_guardado + "/afip.xlsx")
                tabla_tango.write_excel(self.ruta_guardado + "/tango.xlsx")
                tabla_acumulado.write_excel(self.ruta_guardado + "/acumulado.xlsx")
                print("Procesado")
                CTkMessagebox(
                    title="Operación exitosa",
                    message="Las planillas fueron procesadas con éxito.",
                    icon="check"
                )
            except pl.ShapeError:
                print("Fallo la operación.")
                CTkMessagebox(
                    title="Fallo la operación",
                    message="No se pudo procesar correctamente las planillas.",
                    icon="cancel",
                )
            except FileNotFoundError:
                print("No existe el archivo.")
                CTkMessagebox(
                    title="Error",
                    message="No existe el archivo o carpeta indicado.",
                    icon="cancel"
                )
        else:
            print("No se pasaron todas las planillas necesarias.")
            CTkMessagebox(
                title="Cuidado!",
                icon="warning",
                message="Debe pasar las planillas necesarias para poder operar.",
            )
