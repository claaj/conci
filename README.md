# Conci 
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Es una herramienta que ayuda a conciliar percepciones entre AFIP y Tango.

![captura-conci](https://github.com/claaj/conci/assets/102485147/804f074a-cdd1-4c11-8231-d2f89fc3f9a1)

## ¿Qué hace este programa?
Este programa toma dos tablas `(.xlsx)` del mismo mes una de AFIP y otra de Tango.
De estas dos tablas se eliminan todas la columnas que no se utilizan.

Luego se eliminan las filas que contengan el mismo CUIT e importe en ambas tablas.
Dejando solo los registros que no se repiten en ambas tablas.

En la carpeta de guardado indicada se exportan tres archivos:
- Tabla de AFIP sin las columnas que no se utilizan.
- Tabla de Tango sin las columnas que no se utilizan.
- Tabla de acumulados con los registros que no se repiten en ambas tablas. (Se agrega una columna origen, indicando si vienen de una tabla de AFIP o de Tango).

Antes de procesar se puede agregar una tabla de acumulados de un mes anterior, se separan las filas de afip y se agregaran la tabla de AFIP, lo mismo con la de Tango.
Luego se operará como se comentó anteriormente.

## Futuras mejoras
- [x] Documentar el código.
- [ ] Agregar tests para todas las funciones implementadas.
- [ ] Implementar la funcionalidad de conciliar retenciones.

## ¿Qué tecnologías se utilizan?
Este programa está desarrollado en [Python](https://www.python.org/).

Se utilizaron las siguientes librerias:
- [Polars](https://www.pola.rs/) (Analisis de datos).
- [Customtkinter](https://github.com/TomSchimansky/CustomTkinter) (GUI).
- [CTkMessagebox](https://github.com/Akascape/CTkMessagebox) (GUI).
- [Pyinstaller](https://pyinstaller.org/) (Para generar un executable portable).
- [Poetry](https://python-poetry.org/) (Adminatrador de  dependencias).

> [!WARNING]
> Este programa todavía se encuentra en desarrollo no se recomienda la utilización en producción.
