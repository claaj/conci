import polars as pl


def setup_tabla_afip(ruta: str) -> pl.DataFrame:
    df_afip = pl.read_excel(
        source=ruta,
        read_csv_options={"infer_schema_length": 1000}
    )

    df_afip = df_afip.drop([
        'Impuesto',
        'Descripción Impuesto',
        'Régimen',
        'Descripción Régimen',
        'Fecha Ret./Perc.',
        'Número Certificado',
        'Descripción Operación',
        'Descripción Comprobante',
        'Fecha Registración DJ Ag.Ret.',
    ])

    df_afip = df_afip.rename({
        'CUIT Agente Ret./Perc.': 'CUIT',
        'Denominación o Razón Social': 'Razón Social',
        'Importe Ret./Perc.': 'Importe',
        'Número Comprobante': 'Número Comprobante',
        'Fecha Comprobante': 'Fecha Comprobante',
    })

    df_afip = df_afip.select(sorted(df_afip.columns))

    df_afip = df_afip.with_columns(pl.lit('AFIP').alias('Origen'))

    df_afip = castear_columnas(df_afip)

    return df_afip


def setup_tabla_tango(ruta: str) -> pl.DataFrame:
    df_tango = pl.read_excel(
        source=ruta,
        read_csv_options={"infer_schema_length": 1000}
    )

    df_tango = df_tango.drop([
        'COD_IMPUES',
        'DESCRIP',
        'FECH_CONT',
        'COD_PROVE',
        'T_COMP',
        'IMP_TOTAL',
        'JURISDIC',
    ])

    df_tango = df_tango.rename({
        'CUIT': 'CUIT',
        'FECH_COMP': 'Fecha Comprobante',
        'RAZON_SOC': 'Razón Social',
        'N_COMP': 'Número Comprobante',
        'IMPORTE': 'Importe',
    })

    df_tango = df_tango.select(sorted(df_tango.columns))

    df_tango = df_tango.with_columns(pl.lit('Tango').alias('Origen'))

    df_tango = castear_columnas(df_tango)
    df_tango = eliminar_guiones_tango(df_tango)

    return df_tango


def castear_columnas(tabla: pl.DataFrame) -> pl.DataFrame:
    return tabla.select(
        pl.col("CUIT").cast(pl.Utf8),
        pl.col('Razón Social').cast(pl.Utf8),
        pl.col('Importe').cast(pl.Float64),
        pl.col('Número Comprobante').cast(pl.Utf8),
        pl.col('Fecha Comprobante').cast(pl.Utf8),
        pl.col("Origen").cast(pl.Utf8),
    )


def eliminar_guiones_tango(tabla: pl.DataFrame) -> pl.DataFrame:
    tabla = _eliminar_guion_tango(tabla)
    return _eliminar_guion_tango(tabla)


def importes_por_cuit(tabla_afip: pl.DataFrame, tabla_tango: pl.DataFrame, cuit: str) -> list:
    lista_de_importes = []
    for importe_afip in _importes_tabla_por_cuit(tabla_afip, cuit):
        if importe_afip not in lista_de_importes:
            lista_de_importes.append(importe_afip)

    for importe_tango in _importes_tabla_por_cuit(tabla_tango, cuit):
        if importe_tango not in lista_de_importes:
            lista_de_importes.append(importe_tango)

    return lista_de_importes


def cantidad_filas(tabla: pl.DataFrame) -> int:
    return tabla.select(pl.count()).item()


def cuits_unicos_afip_tango(tabla_afip: pl.DataFrame, tabla_tango: pl.DataFrame) -> list:
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
    if len(string) < 30:
        return string
    else:
        numero = len(string) - 30
        return "..." + string[numero:]


def _eliminar_guion_tango(tabla: pl.DataFrame) -> pl.DataFrame:
    return tabla.with_columns(pl.col('CUIT').str.replace("-", ""))


def _lista_de_cuits(tabla: pl.DataFrame) -> list:
    return tabla.select(['CUIT']).unique().get_column('CUIT').to_list()


def _importes_tabla_por_cuit(tabla: pl.DataFrame, cuit: str) -> list:
    return tabla.filter(pl.col("CUIT") == cuit).select(['Importe']).unique().get_column('Importe').to_list()
