# modules/marketplace/data_access.py

# 🚨 STUB MVP: almacenamiento en memoria
# Sustituir por DB real (Postgres, MySQL, etc.) en producción

# === DATOS EN MEMORIA PARA MVP ===
_fincas = [
    {
        "id": 1,
        "titulo": "Parcela Pozuelo",
        "direccion": "Calle Mayor 123, Pozuelo de Alarcón",
        "ref_catastral": "1234567VK4513S0001AB",
        "superficie_m2": 10500,
        "ubicacion_geo": {"lat": 40.45, "lng": -3.80},
        "nota_catastral_raw": "Nota catastral simulada",
        "propietario_id": 10,
        "estado_publicacion": "publicada"
    }
]

_proyectos = []
_transacciones = []

def get_finca(finca_id: int) -> dict:
    """Devuelve la finca por ID."""
    for f in _fincas:
        if f["id"] == finca_id:
            return f
    return {}

def list_fincas() -> list:
    """Lista todas las fincas disponibles."""
    return _fincas

def save_finca(finca: dict) -> dict:
    """Guarda una nueva finca."""
    finca["id"] = len(_fincas) + 1
    _fincas.append(finca)
    return finca

def save_proyecto(proyecto: dict) -> dict:
    """Guarda un nuevo proyecto vinculado a una finca o independiente."""
    proyecto["id"] = len(_proyectos) + 1
    _proyectos.append(proyecto)
    return proyecto

def get_proyecto(proyecto_id: int) -> dict:
    """Devuelve un proyecto por ID."""
    for p in _proyectos:
        if p["id"] == proyecto_id:
            return p
    return {}

def list_proyectos() -> list:
    """Lista todos los proyectos."""
    return _proyectos

def save_transaccion(transaccion: dict) -> dict:
    """Guarda una transacción (pago/reserva/descarga)."""
    transaccion["id"] = len(_transacciones) + 1
    _transacciones.append(transaccion)
    return transaccion

def get_usuario(usuario_id: int) -> dict:
    """Devuelve un usuario por ID (stub)."""
    return {"id": usuario_id, "nombre": f"Usuario {usuario_id}", "tipo": "cliente"}