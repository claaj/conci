import os
import customtkinter as ctk
import polars as pl
import CTkMessagebox as ctkMsg
import tkinter as tk
import percepciones as percep
from utils import acortar_string


class App(ctk.CTk):
    """Clase que controla la interfaz grafica de la aplicación.

    Attributes:
        ruta_afip (str): Ruta donde se buscara la tabla de AFIP.
        ruta_tango (str): Ruta donde se buscara la tabla de Tango.
        ruta_acumulado (str): Ruta donde se buscara la tabla de acumulados.
        ruta_guardado (str): Ruta donde se guardaran las planillas procesados.

    """
    ruta_afip = ""
    ruta_tango = ""
    ruta_acumulado = ""
    ruta_guardado = ""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        self.title("Conci AFIP - Tango")
        self.geometry("450x320")

        self.switch_acumulado_var = ctk.BooleanVar(value=False)

        self.label_afip = ctk.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_tango = ctk.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_guardado = ctk.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.label_acumulado = ctk.CTkLabel(
            self,
            height=32,
            text="",
            justify="left",
        )

        self.button_afip = ctk.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla AFIP",
            command=self.set_ruta_afip
        )

        self.button_tango = ctk.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla Tango",
            command=self.set_ruta_tango
        )

        self.button_guardado = ctk.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir carpeta de guardado",
            command=self.set_ruta_guardado
        )

        self.button_acumulado = ctk.CTkButton(
            self,
            fg_color="transparent",
            border_width=1,
            width=200,
            height=32,
            text="Elegir tabla de acumulados",
            state="disabled",
            command=self.set_ruta_acumulado
        )

        self.switch_acumulado = ctk.CTkSwitch(
            master=self,
            text="Agregar tabla de acumulados",
            command=self.switch_acumulado,
            variable=self.switch_acumulado_var,
            onvalue=True,
            offvalue=False,
        )

        self.button_conciliar = ctk.CTkButton(
            self,
            height=32,
            text="Conciliar",
            command=self.conciliar_percepciones
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
        """Funcion que modifica ruta_afip a partir de una ventana de dialogo."""
        self.ruta_afip = self._buscar_archivos()
        self.label_afip.configure(text=acortar_string(self.ruta_afip))
        print(self.ruta_afip)

    def set_ruta_tango(self):
        """Funcion que modifica ruta_tango a partir de una ventana de dialogo."""
        self.ruta_tango = self._buscar_archivos()
        self.label_tango.configure(text=acortar_string(self.ruta_tango))
        print(self.ruta_tango)

    def set_ruta_acumulado(self):
        """Funcion que modifica ruta_acumulado a partir de una ventana de dialogo."""
        self.ruta_acumulado = self._buscar_archivos()
        self.label_acumulado.configure(text=acortar_string(self.ruta_acumulado))
        print(self.ruta_acumulado)

    def set_ruta_guardado(self):
        """Funcion que modifica ruta_guardado a partir de una ventana de dialogo."""
        self.ruta_guardado = tk.filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Seleccione carpeta de guardado"
        )
        self.label_guardado.configure(text=acortar_string(self.ruta_guardado))
        print(self.ruta_guardado)

    @staticmethod
    def _buscar_archivos() -> str:
        """Funcion que controla una ventana de dialogo para elegir un archivo.

        Returns:
            (str): Una cadena de texto que es igual a la ruta del archivo elegido en la ventana.
        """
        return tk.filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Seleccionar archivo",
            filetypes=(
                ("Excel 2007-365", "*.xlsx*"),
                ("Todos", "*.*")))

    def switch_acumulado(self):
        """Funcion que controla el switch de la app."""
        if self.switch_acumulado_var.get():
            self.button_acumulado.configure(state="enabled")
        else:
            self.ruta_acumulado = ""
            self.button_acumulado.configure(state="disabled")

    def conciliar_percepciones(self):
        """Funcion que ejecuta las operaciones para conciliar las percepciones."""
        if self.ruta_afip != "" and self.ruta_tango != "" and self.ruta_guardado != "" and (
                not self.switch_acumulado_var.get() or self.ruta_acumulado != ""):
            try:
                (tabla_afip, tabla_tango, tabla_acumulado) = percep.conciliar(
                    self.ruta_afip, self.ruta_tango, self.ruta_acumulado)
                tabla_afip.write_excel(self.ruta_guardado + "/afip.xlsx")
                tabla_tango.write_excel(self.ruta_guardado + "/tango.xlsx")
                tabla_acumulado.write_excel(self.ruta_guardado + "/acumulado.xlsx")
                print("Procesado")
                ctkMsg.CTkMessagebox(
                    title="Operación exitosa",
                    message="Las planillas fueron procesadas con éxito.",
                    icon="check"
                )
            except pl.ShapeError:
                print("Fallo la operación.")
                ctkMsg.CTkMessagebox(
                    title="Fallo la operación",
                    message="No se pudo procesar correctamente las planillas.",
                    icon="cancel",
                )
            except FileNotFoundError:
                print("No existe el archivo.")
                ctkMsg.CTkMessagebox(
                    title="Error",
                    message="No existe el archivo o carpeta indicado.",
                    icon="cancel"
                )
        else:
            print("No se pasaron todas las planillas necesarias.")
            ctkMsg.CTkMessagebox(
                title="Cuidado!",
                icon="warning",
                message="Debe pasar las planillas necesarias para poder operar.",
            )
