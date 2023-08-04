import os.path

from utils import *


def conciliador(ruta_afip: str, ruta_tango: str, ruta_acumulado: str) -> (pl.DataFrame, pl.DataFrame, pl.DataFrame):
    if not os.path.exists(ruta_afip) or not os.path.exists(ruta_tango):
        raise FileNotFoundError

    df_afip = setup_tabla_afip(ruta_afip)
    df_tango = setup_tabla_tango(ruta_tango)

    acumulado = pl.DataFrame({})

    try:
        acumulado = pl.read_excel(ruta_acumulado)
        acumulado = castear_columnas(acumulado)
        acumulado_afip = acumulado.filter(pl.col("Origen") == "AFIP")
        acumulado_tango = acumulado.filter(pl.col("Origen") == "Tango")
        df_afip = df_afip.vstack(acumulado_afip)
        df_tango = df_tango.vstack(acumulado_tango)
    except:
        acumulado = pl.DataFrame({
            "CUIT": [],
            "Razón Social": [],
            "Importe": [],
            "Número Comprobante": [],
            "Fecha Comprobante": [],
            "Origen": [],
        })
    finally:
        acumulado = castear_columnas(acumulado)

    cuits_unicos = cuits_unicos_afip_tango(df_afip, df_tango)

    for cuit in cuits_unicos:
        importes = importes_por_cuit(df_tango, df_afip, cuit)
        for importe in importes:
            filtro_tango = df_tango.filter((pl.col("CUIT") == cuit) & (pl.col("Importe") == importe))
            filtro_afip = df_afip.filter((pl.col("CUIT") == cuit) & (pl.col("Importe") == importe))

            diferencia_cantidad = cantidad_filas(filtro_tango) - cantidad_filas(filtro_afip)
            print(diferencia_cantidad)

            if diferencia_cantidad > 0:
                acumulado = acumulado.vstack(
                    filtro_tango.with_row_count(name="num_fila").filter(
                        pl.col("num_fila") < diferencia_cantidad).drop("num_fila"))

            elif diferencia_cantidad < 0:
                acumulado = acumulado.vstack(
                    filtro_afip.with_row_count(name="num_fila").filter(
                        pl.col("num_fila") < abs(diferencia_cantidad)).drop("num_fila"))

    return df_afip, df_tango, acumulado
