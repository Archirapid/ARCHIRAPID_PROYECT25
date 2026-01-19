import math

def ascii_square(area_m2: float) -> str:
    """Devuelve un cuadrado ASCII aproximado a √area × √area metros, con puerta y ventana."""
    lado = math.sqrt(area_m2)
    # número de caracteres por metro (ajustable)
    escala = 4          # 4 caracteres = 1 m (ajusta a tu gusto)
    ancho = int(round(lado * escala))
    alto = ancho

    # Asegurar ancho mínimo para elementos
    if ancho < 10:
        ancho = 10
        alto = 10

    # Construimos la caja base
    top = "   NORTE +" + "-" * (ancho - 2) + "+ " + f"{lado:.1f}m"
    middle_empty = "|" + " " * (ancho - 2) + "|"
    label = "|" + "   CASA   ".center(ancho - 2) + "|"

    # Añadir puerta: en el centro del lado inferior (posición ancho//2)
    door_pos = ancho // 2
    bottom_base = "+" + "-" * (ancho - 2) + "+"
    bottom_with_door = bottom_base[:door_pos] + " " + bottom_base[door_pos+1:]  # Espacio para puerta

    # Añadir ventana: en el lado derecho, centro (línea middle con | en posición)
    window_pos = ancho - 4  # Cerca del final
    middle_with_window = middle_empty[:window_pos] + "[]" + middle_empty[window_pos+2:]  # [] para ventana

    # Plano con elementos
    plano = "\n".join([
        top,
        middle_empty,
        label,
        middle_with_window,  # Ventana en esta línea
        bottom_with_door,    # Puerta en bottom
        f"   {lado:.1f}m"
    ])
    return f"PLANO BÁSICO DEL PROYECTO ({area_m2:.0f} m²)\n\n{plano}\n\nLeyenda: [] = Ventana, espacio en bottom = Puerta"