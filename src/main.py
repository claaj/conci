import polars as pl

def eliminar_guiones_tango(tabla): 
    tabla = eliminar_guion_tango(tabla)
    return eliminar_guion_tango(tabla)

def eliminar_guion_tango(tabla): 
    return tabla.with_columns(pl.col('CUIT').str.replace("-", ""))

def lista_de_cuits(tabla):
    return tabla.select(['CUIT']).unique().collect().get_column('CUIT').to_list()

def lista_de_importes_por_cuit(tabla, cuit):
    return tabla.filter(pl.col("CUIT") == cuit).select(['Importe']).unique().collect().get_column('Importe').to_list()

def cantidad_filas(tabla) -> int:
    try:
        return tabla.select(pl.count()).collect().item()
    except:
        return 0

if __name__ == '__main__':
    df_afip = pl.read_excel(
        source = "planillas/afip.xlsx",
        read_csv_options = { "infer_schema_length": 1000 }
    ).lazy()

    df_tango = pl.read_excel("planillas/tango.xlsx").lazy()

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
        'CUIT Agente Ret./Perc.' : 'CUIT',
        'Denominación o Razón Social' : 'Razón Social',
        'Importe Ret./Perc.' : 'Importe',
        'Número Comprobante' : 'Número Comprobante',
        'Fecha Comprobante' : 'Fecha Comprobante',
    })

    df_afip = df_afip.with_columns([
        pl.col('CUIT').cast(pl.Utf8),
        'Razón Social',
        'Importe',
        'Número Comprobante',
        'Fecha Comprobante',
    ])

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
        'FECH_COMP' : 'Fecha Comprobante',
        'RAZON_SOC' : 'Razón Social',
        'N_COMP' : 'Número Comprobante',
        'IMPORTE' : 'Importe',
    })

    acumulado = pl.DataFrame({})

    df_tango = eliminar_guiones_tango(df_tango)
    df_tango = df_tango
    cuits_tango = lista_de_cuits(df_tango)

    for cuit in cuits_tango:
        importes_tango = lista_de_importes_por_cuit(df_tango, cuit) 
        for importe in importes_tango:
            try:
                filtro_tango = df_tango.filter((pl.col("CUIT") == cuit) & (pl.col("Importe") == importe))
                filtro_afip = df_afip.filter((pl.col("CUIT") == cuit) & (pl.col("Importe") == importe))

                diferencia_cantidad = cantidad_filas(filtro_tango) - cantidad_filas(filtro_afip)
                print(diferencia_cantidad)
                
                if diferencia_cantidad > 0:
                    acumulado = acumulado.vstack(filtro_tango.with_row_count(name = "num_fila", offset = 1).filter(pl.col("num_fila") <= diferencia_cantidad).drop("num_fila").collect())

                elif diferencia_cantidad < 0:
                    acumulado = acumulado.vstack(filtro_afip.with_row_count(name = "num_fila", offset = 1).filter(pl.col("num_fila") <= abs(diferencia_cantidad)).drop("num_fila").collect())
            except:
                #print("Cuit e importe no coinciden en ambas tablas")
                1+1

    df_afip.collect().write_excel("procesadas/afip.xlsx")
    df_tango.collect().write_excel("procesadas/tango.xlsx")
    acumulado.write_excel("procesadas/acumulado.xlsx")
