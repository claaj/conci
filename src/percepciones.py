import os

from utils import *


def conciliar(
    ruta_afip: str, ruta_tango: str, ruta_acumulado: str
) -> (pl.DataFrame, pl.DataFrame, pl.DataFrame):
    """Función encargada de realizar las operaciones de percepciones con las tablas.

    Args:
        ruta_afip (str): Ruta donde se encuentra la tabla de AFIP.
        ruta_tango (str): Ruta donde se encuentra la tabla de Tango.
        ruta_acumulado (str): Ruta donde se encuenta la tabla de acumualados.

    Returns:
        polars.DataFrame, polars.DataFrame, polars.DataFrame: Tupla de 3 DataFrames donde el primer elemento pertenece
        al DataFrame de AFIP, el segundo al de Tango, y por ultimo el de acumulados.

    Raises:
        FileNotFoundError: Si ruta_afip o ruta_tango no existen.
        polars.ShapeError: Si ocurre un error al operar con las tablas.

    """

    if not os.path.exists(ruta_afip) or not os.path.exists(ruta_tango):
        raise FileNotFoundError

    df_afip = setup_tabla_afip(ruta_afip)
    df_tango = setup_tabla_tango(ruta_tango)

    acumulado = pl.DataFrame({})

    if ruta_acumulado != "":
        try:
            acumulado = pl.read_excel(ruta_acumulado)
            acumulado = castear_columnas(acumulado)
            acumulado_afip = acumulado.filter(pl.col("Origen") == "AFIP")
            acumulado_tango = acumulado.filter(pl.col("Origen") == "Tango")
            df_afip = df_afip.vstack(acumulado_afip)
            df_tango = df_tango.vstack(acumulado_tango)
        except:
            acumulado = pl.DataFrame(
                {
                    "CUIT": [],
                    "Razón Social": [],
                    "Importe": [],
                    "Número Comprobante": [],
                    "Fecha Comprobante": [],
                    "Origen": [],
                }
            )
    else:
        acumulado = pl.DataFrame(
            {
                "CUIT": [],
                "Razón Social": [],
                "Importe": [],
                "Número Comprobante": [],
                "Fecha Comprobante": [],
                "Origen": [],
            }
        )

    acumulado = castear_columnas(acumulado)
    cuits_unicos = cuits_unicos_afip_tango(df_afip, df_tango)

    for cuit in cuits_unicos:
        if not checkear_importe_total(cuit, df_afip, df_tango):
            importes = importes_por_cuit(df_tango, df_afip, cuit)
            for importe in importes:
                filtro_tango = df_tango.filter(
                    (pl.col("CUIT") == cuit) & (pl.col("Importe") == importe)
                )
                filtro_afip = df_afip.filter(
                    (pl.col("CUIT") == cuit) & (pl.col("Importe") == importe)
                )

                diferencia_cantidad = cantidad_filas(filtro_tango) - cantidad_filas(
                    filtro_afip
                )

                print(diferencia_cantidad)

                if diferencia_cantidad > 0:
                    acumulado = acumulado.vstack(
                        filtro_tango.with_row_count(name="num_fila")
                        .filter(pl.col("num_fila") < diferencia_cantidad)
                        .drop("num_fila")
                    )

                elif diferencia_cantidad < 0:
                    acumulado = acumulado.vstack(
                        filtro_afip.with_row_count(name="num_fila")
                        .filter(pl.col("num_fila") < abs(diferencia_cantidad))
                        .drop("num_fila")
                    )

    return df_afip, df_tango, acumulado
