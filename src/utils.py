import polars as pl


def setup_tabla_afip(ruta: str) -> pl.DataFrame:
    """Funcion que elimina las columnas que no se utilizan y formatea una tabla AFIP a partir de una ruta.

    Args:
        ruta (str): Ruta donde se encuentra la tabla de AFIP.

    Returns:
        pl.DataFrame: Tabla de AFIP formateada lista para realizar las operaciones.

    """
    df_afip = pl.read_excel(source=ruta, read_csv_options={"infer_schema_length": 1000})

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


def castear_columnas(tabla: pl.DataFrame) -> pl.DataFrame:
    """Funcion encargada de indicar el tipo de data de cada columna de las tablas.

    Args:
        tabla (polars.DataFrame): Tabla a castear los valores de las columnas.

    Returns:
        polars.DataFrame: La tabla con los tipos de datos en las columnas correctos.

    """
    return tabla.select(
        pl.col("CUIT").cast(pl.Utf8),
        pl.col("Razón Social").cast(pl.Utf8),
        pl.col("Importe").cast(pl.Float64),
        pl.col("Número Comprobante").cast(pl.Utf8),
        pl.col("Fecha Comprobante").cast(pl.Utf8),
        pl.col("Origen").cast(pl.Utf8),
    )


def eliminar_guiones_tango(tabla: pl.DataFrame) -> pl.DataFrame:
    """Funcion encargada de eliminar los dos guiones de la columna cuit.

    Args:
        tabla (polars.DataFrame): Tabla a eliminar los guiones.

    Returns:
        (polars.DataFrame): La tabla con los guiones eliminados.

    """
    tabla = _eliminar_guion_tango(tabla)
    return _eliminar_guion_tango(tabla)


def importes_por_cuit(
    tabla_afip: pl.DataFrame, tabla_tango: pl.DataFrame, cuit: str
) -> list:
    """Funcion encargada de juntar todos los importes, sin repetir, presentes en ambas tablas para un cuit dado.

    Args:
        tabla_afip (polars.DataFrame): Tabla de AFIP.
        tabla_tango (polars.DataFrame): Tabla de Tango.
        cuit (str): Número de CUIT.

    Returns:
        (list): Lista con todos los importes sin repetir presentes en las tablas de AFIP y Tango asociados a un CUIT.

    """
    lista_de_importes = []
    for importe_afip in _importes_tabla_por_cuit(tabla_afip, cuit):
        if importe_afip not in lista_de_importes:
            lista_de_importes.append(importe_afip)

    for importe_tango in _importes_tabla_por_cuit(tabla_tango, cuit):
        if importe_tango not in lista_de_importes:
            lista_de_importes.append(importe_tango)

    return lista_de_importes


def cantidad_filas(tabla: pl.DataFrame) -> int:
    """Funcion que indica la cantidad de filas de una tabla.

    Args:
        tabla (polars.DataFrame) : Tabla para contar las filas.

    Returns:
        (int): Cantidad de filas presentes en la tabla.

    """
    return tabla.select(pl.count()).item()


def cuits_unicos_afip_tango(
    tabla_afip: pl.DataFrame, tabla_tango: pl.DataFrame
) -> list:
    """Funcion que retorna todos los cuit presentes en ambas tablas (AFIP y Tango), sin repetir.

    Args:
        tabla_afip (polars.DataFrame) : Tabla de AFIP.
        tabla_tango (polars.DataFrame) : Tabla de Tango.

    Returns:
        (list): Una lista con todos los cuits presentes en ambas tablas. Sin repetir.

    """
    cuits_afip = _lista_de_cuits(tabla_afip)
    cuits_tango = _lista_de_cuits(tabla_tango)
    lista_unicos = []
    for cuit_afip in cuits_afip:
        cuit = str(cuit_afip)
        if cuit not in lista_unicos:
            lista_unicos.append(cuit)

    for cuit_tango in cuits_tango:
        cuit = str(cuit_tango)
        if cuit not in lista_unicos:
            lista_unicos.append(cuit)

    return lista_unicos


def acortar_string(string: str) -> str:
    """Funcion que acorta un string de largo mayor a 30 caracteres.
    Si es recortado de se le agregan 3 puntos ("...") adelante.

    Args:
        string (str): Cadena a la cual se la operara.

    Returns:
        (str): La cadena procesada.

    """
    if len(string) < 30:
        return string
    else:
        numero = len(string) - 30
        return "..." + string[numero:]


def fecha_para_carpeta(tabla_afip: pl.DataFrame) -> str:
    """Funcion que obtiene la fecha a partir de la tabla de AFIP. Retorna la fecha en formato AAAA/MM.

    Args:
        tabla_afip (pl.DataFrame): Tabla de AFIP.

    Returns:
        (str): Un cadena con la fecha en el formato AAAA/MM
    """
    fecha_string = (
        tabla_afip.select(["Fecha Comprobante"])
        .get_column("Fecha Comprobante")
        .head(1)
        .to_list()[0]
    )

    fecha_split = fecha_string.split("/")
    print(fecha_split)

    return f"{fecha_split[2]}-{fecha_split[1]}"


def checkear_importe_total(
    cuit: str, tabla_afip: pl.DataFrame, tabla_tango: pl.DataFrame
) -> bool:
    """Funcion que verifica que la suma de todos los valores de un CUIT pertenecientes a AFIP es igual a la suma de
    todos los valores de Tango pertenecientes a ese mismo CUIT.

    Args:
        cuit (str): Numero de CUIT.
        tabla_afip (pl.DataFrame): Tabla de AFIP.
        tabla_tango (pl.DataFrame): Tabla de Tango.

    Returns:
        (bool): True si las sumas coinciden, False si no lo hacen.
    """
    importes_afip = (
        tabla_afip.filter(pl.col("CUIT") == cuit)
        .select(["Importe"])
        .get_column("Importe")
        .to_list()
    )

    importes_tango = (
        tabla_tango.filter(pl.col("CUIT") == cuit)
        .select(["Importe"])
        .get_column("Importe")
        .to_list()
    )

    total_afip = _sumar_contenidos_lista(importes_afip)
    total_tango = _sumar_contenidos_lista(importes_tango)

    print(importes_afip)
    print(importes_tango)

    print(total_afip == total_tango)
    return total_afip == total_tango


def _sumar_contenidos_lista(lista: list) -> float:
    """Funcion que suma todos los contenidos de una lista.

    Args:
        lista (list): Lista con los contenidos a sumar.

    Returns:
        (float): La suma de todos los valores contenidos en lista.
    """
    total = 0
    for numero in lista:
        total += numero
    return total


def _eliminar_guion_tango(tabla: pl.DataFrame) -> pl.DataFrame:
    """Funcion que elimina un guion de la columna CUIT.

    Args:
        tabla (polars.DataFrame) : Tabla a eliminar los guiones en su columna CUIT.

    Returns:
        (polars.DataFrame): Tabla formateada como se menciono anteriormente.

    """
    return tabla.with_columns(pl.col("CUIT").str.replace("-", ""))


def _lista_de_cuits(tabla: pl.DataFrame) -> list:
    """Funcion que retorna la lista de los CUITs presentes en una tabla.

    Args:
        tabla (polars.DataFrame) : Tabla a extraer los CUITs.

    Returns:
        (list): Lista de CUITs presentes en la tabla.

    """
    return tabla.select(["CUIT"]).unique().get_column("CUIT").to_list()


def _importes_tabla_por_cuit(tabla: pl.DataFrame, cuit: str) -> list:
    """Funcion que retorna una lista con los importes asociados en cuit.
    Args:
        tabla (polars.DataFrame): Tabla en la cual buscar.
        cuit (str): CUIT con el cual se filtraran todos los importes en la tabla.

    Returns:
        (list): Una lista con todos los importes presentes en la tabla.

    """
    return (
        tabla.filter(pl.col("CUIT") == cuit)
        .select(["Importe"])
        .unique()
        .get_column("Importe")
        .to_list()
    )
