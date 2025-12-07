# modules/marketplace/catastro_api.py

# 🚨 STUB MVP: simulación de API Catastro
# Sustituir por API real de Catastro en producción

def fetch_by_address(direccion: str, municipio: str = "Madrid") -> dict:
    """
    Simula obtención de datos catastrales por dirección.
    Devuelve datos fijos para demostración.
    """
    return {
        "superficie_m2": 10500,
        "ref_catastral": "1234567VK4513S0001AB",
        "ubicacion_geo": {
            "lat": 40.45,
            "lng": -3.80,
            "municipio": municipio,
            "direccion_completa": f"{direccion}, {municipio}"
        },
        "nota_catastral_raw": {
            "fuente": "simulado_mvp",
            "superficie_registral": 10500,
            "uso_principal": "Residencial unifamiliar",
            "valor_catastral_estimado": 8400000,
            "fecha_consulta": "2025-12-07",
            "notas": "Datos simulados para demostración MVP"
        },
        "estado": "activo",
        "tipo": "urbana"
    }

def fetch_by_ref_catastral(ref_catastral: str) -> dict:
    """
    Simula obtención de datos catastrales por referencia catastral.
    Devuelve datos fijos para demostración.
    """
    return {
        "superficie_m2": 10500,
        "ref_catastral": ref_catastral,
        "ubicacion_geo": {
            "lat": 40.45,
            "lng": -3.80,
            "municipio": "Madrid",
            "direccion_completa": f"Dirección simulada para {ref_catastral}"
        },
        "nota_catastral_raw": {
            "fuente": "simulado_mvp",
            "superficie_registral": 10500,
            "uso_principal": "Residencial unifamiliar",
            "valor_catastral_estimado": 8400000,
            "fecha_consulta": "2025-12-07",
            "notas": f"Datos simulados para ref: {ref_catastral}"
        },
        "estado": "activo",
        "tipo": "urbana"
    }