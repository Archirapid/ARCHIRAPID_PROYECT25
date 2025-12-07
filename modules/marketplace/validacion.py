"""
Módulo de validación para planes de vivienda con reglas genéricas.
Este módulo proporciona validaciones básicas para el MVP, sin reemplazar normativa real.
"""

def reglas_min_m2(tipo: str) -> int:
    """
    Devuelve el mínimo m² requerido para un tipo de estancia según reglas genéricas.

    Args:
        tipo: Tipo de estancia (ej: "Dormitorio", "Salón Comedor", etc.)

    Returns:
        int: Mínimo m² requerido
    """
    mapa = {
        "Dormitorio": 8,
        "Dormitorio principal": 10,
        "Salón": 12,
        "Salón Comedor": 12,
        "Cocina": 6,
        "Baño": 3,
        "Aseo": 2,
        "Despensa": 0,
        "Trastero": 0,
        "Garage": 12,
        "Estudio": 6
    }
    # Regla por defecto si no se reconoce el tipo
    return mapa.get(tipo, 6)


def validar_plan_local(plan_json: dict, superficie_finca: float) -> dict:
    """
    Valida el plan con reglas mínimas genéricas para el MVP.

    Args:
        plan_json: Plan generado por IA con habitaciones y garage
        superficie_finca: Superficie total de la finca en m²

    Returns:
        dict: {
            "ok": bool,
            "total_m2": float,
            "errores": lista de textos,
            "recomendaciones": lista de textos
        }
    """
    errores = []
    recomendaciones = []

    # Calcular total construido si no viene en el JSON
    total = plan_json.get("total_m2")
    if total is None:
        total = 0
        for h in plan_json.get("habitaciones", []):
            total += float(h.get("m2", 0))
        if "garage" in plan_json:
            total += float(plan_json["garage"].get("m2", 0))

    # Validar límite máximo construible (33%)
    max_construible = superficie_finca * 0.33
    if total > max_construible:
        errores.append(".1f"".1f")

    # Recomendación de altura libre
    recomendaciones.append("Altura libre mínima recomendada: 2.6 m. Verificar estructura y climatización.")

    # Validar cada estancia
    for h in plan_json.get("habitaciones", []):
        nombre = h.get("nombre", "Estancia")
        m2 = float(h.get("m2", 0))

        # Determinar tipo por nombre (heurística simple)
        tipo = "Dormitorio" if "Dormitorio" in nombre else (
            "Salón Comedor" if "Salón" in nombre or "Comedor" in nombre else
            "Cocina" if "Cocina" in nombre else
            "Baño" if "Baño" in nombre or "Aseo" in nombre else
            "Estudio" if "Estudio" in nombre else
            "Despensa" if "Despensa" in nombre else
            "Trastero" if "Trastero" in nombre else
            "Estancia"
        )

        minimo = reglas_min_m2(tipo)
        if m2 < minimo:
            errores.append(".1f"".1f")
            if tipo == "Dormitorio" and m2 < 6:
                recomendaciones.append(".1f")
        elif tipo == "Dormitorio" and m2 < 10:
            recomendaciones.append(".1f")

    # Validar garage
    if "garage" in plan_json:
        gm2 = float(plan_json["garage"].get("m2", 0))
        if gm2 < 12:
            recomendaciones.append(".1f")

    # Recomendación de pasillos
    recomendaciones.append("Pasillos: ancho recomendado ≥ 0.9 m para accesibilidad.")

    ok = len(errores) == 0
    return {
        "ok": ok,
        "total_m2": total,
        "errores": errores,
        "recomendaciones": recomendaciones
    }