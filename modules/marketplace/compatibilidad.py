# modules/marketplace/compatibilidad.py

from modules.marketplace.data_access import list_proyectos

# 🚨 STUB MVP: reglas simples de compatibilidad
# En producción se añadirán más criterios (uso, normativa local, orientación, etc.)

def list_proyectos_compatibles(finca: dict) -> list:
    """
    Devuelve proyectos compatibles con una finca según reglas simples:
    - Superficie construida del proyecto ≤ 33% de la superficie de la finca
    - Etiquetas incluyen 'residencial'
    """
    superficie_max = finca.get("superficie_m2", 0) * 0.33
    proyectos = list_proyectos()

    compatibles = []
    for p in proyectos:
        if p.get("total_m2", 0) <= superficie_max:
            etiquetas = p.get("etiquetas", [])
            if "residencial" in etiquetas:
                compatibles.append(p)

    return compatibles