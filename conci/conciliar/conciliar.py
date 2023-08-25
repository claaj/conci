from conci.conciliar.utils import *
import polars as pl


def conciliar(
    df_afip: pl.DataFrame, df_tango: pl.DataFrame, ruta_acumulado: str
) -> (pl.DataFrame, pl.DataFrame, pl.DataFrame):
    """Función encargada de conciliar las tablas.

    Args:
        df_afip (pl.DataFrame): Tabla de AFIP.
        df_tango (pl.DataFrame): Tabla de Tango.
        ruta_acumulado (str): Ruta donde se encuenta la tabla de acumualados.

    Returns:
        polars.DataFrame, polars.DataFrame, polars.DataFrame: Tupla de 3 DataFrames donde el primer elemento pertenece
        al DataFrame de AFIP, el segundo al de Tango, y por ultimo el de acumulados.

    Raises:
        FileNotFoundError: Si ruta_afip o ruta_tango no existen.
        polars.ShapeError: Si ocurre un error al operar con las tablas.
    """

    if ruta_acumulado != "":
        try:
            df_acumulado = pl.read_excel(ruta_acumulado)
            df_acumulado = castear_columnas(df_acumulado)
            acumulado_afip = df_acumulado.filter(pl.col("Origen") == "AFIP")
            acumulado_tango = df_acumulado.filter(pl.col("Origen") == "Tango")
            df_afip = df_afip.vstack(acumulado_afip)
            df_tango = df_tango.vstack(acumulado_tango)
        except:
            df_acumulado = pl.DataFrame(
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
        df_acumulado = pl.DataFrame(
            {
                "CUIT": [],
                "Razón Social": [],
                "Importe": [],
                "Número Comprobante": [],
                "Fecha Comprobante": [],
                "Origen": [],
            }
        )

    df_acumulado = castear_columnas(df_acumulado)
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
                    df_acumulado = df_acumulado.vstack(
                        filtro_tango.with_row_count(name="num_fila")
                        .filter(pl.col("num_fila") < diferencia_cantidad)
                        .drop("num_fila")
                    )

                elif diferencia_cantidad < 0:
                    df_acumulado = df_acumulado.vstack(
                        filtro_afip.with_row_count(name="num_fila")
                        .filter(pl.col("num_fila") < abs(diferencia_cantidad))
                        .drop("num_fila")
                    )

    return df_afip, df_tango, df_acumulado


def concatenar_tablas_afip(tablas: list) -> pl.DataFrame:
    """Funcion que concatena los tablas dadas en una lista que tenga

    Args:
        tablas (list): Lista con las rutas de las planillas de AFIP.

    Returns:
        pl.DataFrame: Tabla con todos los contenidos de las planillas concatenadas.

    Raises:
        FileNotFoundError: Si alguna de las ruta no es valida.
        pl.ShapeError: Si ocurre un error al operar con las tablas.
    """
    if not checkear_archivos(tablas):
        raise FileNotFoundError

    df_afip = pl.DataFrame(
        {
            "CUIT": [],
            "Razón Social": [],
            "Importe": [],
            "Número Comprobante": [],
            "Fecha Comprobante": [],
            "Origen": [],
        }
    )

    df_afip = castear_columnas(df_afip)

    for tabla in tablas:
        df_agregar = setup_tabla_afip(tabla)
        df_afip = df_afip.vstack(df_agregar)

    return df_afip


def concatenar_tablas_tango(tablas: list) -> pl.DataFrame:
    """Funcion que concatena los tablas dadas en una lista que tenga

    Args:
        tablas (list): Lista con las rutas de las planillas de AFIP.

    Returns:
        pl.DataFrame: Tabla con todos los contenidos de las planillas concatenadas.

    Raises:
        FileNotFoundError: Si alguna de las ruta no es valida.
        pl.ShapeError: Si ocurre un error al operar con las tablas.
    """
    if not checkear_archivos(tablas):
        raise FileNotFoundError

    df_tango = pl.DataFrame(
        {
            "CUIT": [],
            "Razón Social": [],
            "Importe": [],
            "Número Comprobante": [],
            "Fecha Comprobante": [],
            "Origen": [],
        }
    )

    df_tango = castear_columnas(df_tango)

    for tabla in tablas:
        df_agregar = castear_columnas(setup_tabla_tango(tabla))
        df_tango = df_tango.vstack(df_agregar)

    return df_tango


def setup_tabla_afip(ruta: str) -> pl.DataFrame:
    """Funcion que elimina las columnas que no se utilizan y formatea una tabla AFIP a partir de una ruta.

    Args:
        ruta (str): Ruta donde se encuentra la tabla de AFIP.

    Returns:
        pl.DataFrame: Tabla de AFIP formateada lista para realizar las operaciones.

    """
    df_afip = pl.read_excel(
        source=ruta,
        read_csv_options={
            "infer_schema_length": 10000,
            "dtypes": {"Número Certificado": pl.Utf8},
        },
    )

    df_afip = df_afip.drop(
        [
            "Impuesto",
            "Descripción Impuesto",
            "Régimen",
            "Descripción Régimen",
            "Fecha Ret./Perc.",
            "Número Certificado",
            "Descripción Operación",
            "Descripción Comprobante",
            "Fecha Registración DJ Ag.Ret.",
        ]
    )

    df_afip = df_afip.rename(
        {
            "CUIT Agente Ret./Perc.": "CUIT",
            "Denominación o Razón Social": "Razón Social",
            "Importe Ret./Perc.": "Importe",
            "Número Comprobante": "Número Comprobante",
            "Fecha Comprobante": "Fecha Comprobante",
        }
    )

    df_afip = df_afip.select(sorted(df_afip.columns))

    df_afip = df_afip.with_columns(pl.lit("AFIP").alias("Origen"))

    df_afip = castear_columnas(df_afip)

    return df_afip


def setup_tabla_tango(ruta: str) -> pl.DataFrame:
    """Funcion que elimina las columnas que no se utilizan y formatea una tabla Tango a partir de una ruta.

    Args:
        ruta (str): Ruta donde se encuentra la tabla de Tango.

    Returns:
        polars.DataFrame: Tabla de Tango formateada lista para realizar las operaciones.

    """
    df_tango = pl.read_excel(
        source=ruta, read_csv_options={"infer_schema_length": 1000}
    )

    df_tango = df_tango.drop(
        [
            "COD_IMPUES",
            "DESCRIP",
            "FECH_CONT",
            "COD_PROVE",
            "T_COMP",
            "IMP_TOTAL",
            "JURISDIC",
        ]
    )

    df_tango = df_tango.rename(
        {
            "CUIT": "CUIT",
            "FECH_COMP": "Fecha Comprobante",
            "RAZON_SOC": "Razón Social",
            "N_COMP": "Número Comprobante",
            "IMPORTE": "Importe",
        }
    )

    df_tango = df_tango.select(sorted(df_tango.columns))

    df_tango = df_tango.with_columns(pl.lit("Tango").alias("Origen"))

    df_tango = castear_columnas(df_tango)
    df_tango = eliminar_guiones_tango(df_tango)

    return df_tango


def procesar(
    rutas_afip: list, rutas_tango: list, ruta_acumulado: str
) -> (pl.DataFrame, pl.DataFrame, pl.DataFrame):
    """Función encargada de realizar las operaciones de percepciones con las tablas.

    Args:
        rutas_afip (list): Rutas donde se encuentra la tabla de AFIP.
        rutas_tango (list): Rutas donde se encuentra la tabla de Tango.
        ruta_acumulado (str): Ruta donde se encuenta la tabla de acumualados.

    Returns:
        polars.DataFrame, polars.DataFrame, polars.DataFrame: Tupla de 3 DataFrames donde el primer elemento pertenece
        al DataFrame de AFIP, el segundo al de Tango, y por ultimo el de acumulados.

    Raises:
        FileNotFoundError: Si ruta_afip o ruta_tango no existen.
        polars.ShapeError: Si ocurre un error al operar con las tablas.
    """
    df_afip = concatenar_tablas_afip(rutas_afip)
    df_tango = concatenar_tablas_tango(rutas_tango)

    return conciliar(df_afip, df_tango, ruta_acumulado)
