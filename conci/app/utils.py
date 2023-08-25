def acortar_string(string: str, cantidad: int) -> str:
    """Funcion que acorta un string de largo x de caracteres.
    Si es recortado de se le agregan 3 puntos ("...") adelante.

    Args:
        string (str): Cadena a la cual se la operara.
        cantidad (int): Cantidad de caracteres.

    Returns:
        (str): La cadena procesada.

    """
    if len(string) < cantidad:
        return string
    else:
        numero = len(string) - cantidad
        return "..." + string[numero:]
