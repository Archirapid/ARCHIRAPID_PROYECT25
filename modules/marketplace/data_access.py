# modules/marketplace/data_access.py

# 🚨 STUB MVP: almacenamiento en memoria
# Sustituir por DB real (Postgres, MySQL, etc.) en producción

# === IMPORTS PARA BD ===
from modules.marketplace.utils import list_published_plots, list_projects

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
        "propietario_email": "cliente@ejemplo.com",  # Simular propiedad
        "precio_venta": 850000,
        "foto_url": "https://via.placeholder.com/400x300/4CAF50/white?text=FINCA+POZUELO",
        "estado_publicacion": "publicada",
        "datos_propietario": {
            "metros_cuadrados": 10500,
            "precio_por_m2": 81,
            "valor_catastral": 750000,
            "nota_catastral_completa": "Finca urbana sita en Pozuelo de Alarcón...",
            "fotos": ["foto1.jpg", "foto2.jpg"],
            "documentos": ["escritura.pdf", "certificado_energetico.pdf"]
        }
    },
    {
        "id": 2,
        "titulo": "Solar Madrid Centro",
        "direccion": "Gran Vía 45, Madrid",
        "ref_catastral": "87654321AB123C0002CD",
        "superficie_m2": 8000,
        "ubicacion_geo": {"lat": 40.42, "lng": -3.70},
        "nota_catastral_raw": "Solar en pleno centro",
        "propietario_id": None,
        "propietario_email": None,
        "precio_venta": 1200000,
        "foto_url": "https://via.placeholder.com/400x300/2196F3/white?text=SOLAR+MADRID",
        "estado_publicacion": "publicada",
        "datos_propietario": None
    }
]

_proyectos = [
    {
        "id": 1,
        "titulo": "Casa Residencial Moderna",
        "finca_id": 1,
        "autor_tipo": "arquitecto",
        "total_m2": 3200,
        "precio": 450000,
        "etiquetas": ["residencial", "moderna", "3_plantas"],
        "descripcion": "Proyecto moderno de 3 plantas con jardín",
        "pdf_memoria_url": "memoria_moderna.pdf",
        "cad_url": "plano_moderno.dxf"
    },
    {
        "id": 2,
        "titulo": "Chalet Tradicional",
        "finca_id": 1,
        "autor_tipo": "arquitecto",
        "total_m2": 2800,
        "precio": 380000,
        "etiquetas": ["residencial", "tradicional", "2_plantas"],
        "descripcion": "Chalet tradicional de 2 plantas con garaje",
        "pdf_memoria_url": "memoria_chalet.pdf",
        "cad_url": "plano_chalet.dxf"
    },
    {
        "id": 3,
        "titulo": "Edificio de Apartamentos IA",
        "finca_id": 1,
        "autor_tipo": "ia",
        "total_m2": 4000,
        "precio": 600000,
        "etiquetas": ["residencial", "apartamentos", "4_plantas"],
        "descripcion": "Edificio de apartamentos generado por IA",
        "pdf_memoria_url": "memoria_apartamentos.pdf",
        "cad_url": "plano_apartamentos.dxf"
    }
]

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
    """
    Guarda un nuevo proyecto vinculado a una finca o independiente.
    Soporta versionado automático: si no se pasa 'version', se asigna automáticamente
    la siguiente versión disponible para esa finca.
    """
    proyecto["id"] = len(_proyectos) + 1
    
    # Versionado automático si no se especifica versión
    if "version" not in proyecto and "finca_id" in proyecto:
        versiones_existentes = [
            p.get("version", 0) 
            for p in _proyectos 
            if p.get("finca_id") == proyecto.get("finca_id")
        ]
        proyecto["version"] = max(versiones_existentes) + 1 if versiones_existentes else 1
    elif "version" not in proyecto:
        proyecto["version"] = 1
    
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


# === FUNCIONES AUXILIARES PARA GESTIÓN DE VERSIONES ===

def get_proyectos_by_finca(finca_id: int) -> list:
    """
    Devuelve todas las versiones de proyectos vinculados a una finca.
    
    Args:
        finca_id: ID de la finca
        
    Returns:
        list: Lista de proyectos ordenados por versión descendente
    """
    proyectos = [p for p in _proyectos if p.get("finca_id") == finca_id]
    return sorted(proyectos, key=lambda p: p.get("version", 0), reverse=True)


def get_last_proyecto(finca_id: int) -> dict:
    """
    Devuelve la última versión vigente de un proyecto de una finca.
    
    Args:
        finca_id: ID de la finca
        
    Returns:
        dict: Proyecto con la versión más alta, o dict vacío si no existe
    """
    proyectos = get_proyectos_by_finca(finca_id)
    return proyectos[0] if proyectos else {}


def get_proyecto_version(finca_id: int, version: int) -> dict:
    """
    Devuelve una versión específica de un proyecto de una finca.
    
    Args:
        finca_id: ID de la finca
        version: Número de versión del proyecto
        
    Returns:
        dict: Proyecto con esa versión, o dict vacío si no existe
    """
    for p in _proyectos:
        if p.get("finca_id") == finca_id and p.get("version") == version:
            return p
    return {}


def count_versiones(finca_id: int) -> int:
    """
    Cuenta cuántas versiones de proyecto existen para una finca.
    
    Args:
        finca_id: ID de la finca
        
    Returns:
        int: Número de versiones de proyecto para esa finca
    """
    return len([p for p in _proyectos if p.get("finca_id") == finca_id])

# === NUEVAS FUNCIONES PARA BD — NO REEMPLAZAN LAS EXISTENTES ===
def list_fincas_publicadas() -> list:
    """Devuelve todas las fincas publicadas desde BD (SQLite)."""
    return list_published_plots()

def list_fincas_by_user(email: str) -> list:
    """Devuelve fincas asociadas a un usuario por email."""
    return [f for f in _fincas if f.get("propietario_email") == email]

def get_last_proyecto(finca_id: int) -> dict | None:
    """Devuelve la última versión de proyecto de una finca."""
    proyectos = [p for p in _proyectos if p.get("finca_id") == finca_id]
    if not proyectos:
        return None
    return sorted(proyectos, key=lambda p: p.get("version", 0), reverse=True)[0]

def list_proyectos_compatibles(finca: dict) -> list:
    """MVP: devuelve proyectos compatibles por superficie/uso; fallback a demo."""
    sup = finca.get("superficie_m2", 0) or 0
    compatibles = [p for p in _proyectos if p.get("total_m2", 0) <= sup * 0.33]
    return compatibles or _proyectos[:3]  # demo para inversores

# === FUNCIONES PARA ESQUEMA PARAMÉTRICO ===
def list_fincas_adquiridas(email: str) -> list:
    """
    Devuelve fincas adquiridas por un usuario (propiedad real).
    Microcirugía: filtra por propietario_email con datos completos.
    """
    try:
        # En producción, consultar BD real
        adquiridas = [f for f in _fincas if f.get("propietario_email") == email]
        # Asegurar que tienen datos_propietario completos
        for f in adquiridas:
            if not f.get("datos_propietario"):
                f["datos_propietario"] = {
                    "metros_cuadrados": f.get("superficie_m2", 0),
                    "precio_por_m2": f.get("precio_venta", 0) // max(f.get("superficie_m2", 1), 1),
                    "valor_catastral": f.get("precio_venta", 0) * 0.8 if f.get("precio_venta") else 0,
                    "nota_catastral_completa": f.get("nota_catastral_raw", "Nota catastral no disponible"),
                    "fotos": ["finca_foto_1.jpg", "finca_foto_2.jpg"],
                    "documentos": ["escritura_propiedad.pdf", "certificado_catastral.pdf"]
                }
        return adquiridas
    except Exception as e:
        print(f"Error en list_fincas_adquiridas: {e}")
        return []

def save_plan_parametrico(plan_json: dict, finca_id: int, autor_tipo: str = "user+ia") -> dict:
    """
    Guarda un plan paramétrico completo con versionado automático.
    Microcirugía: integra con sistema existente de proyectos.
    """
    try:
        # Obtener última versión
        last_proj = get_last_proyecto(finca_id)
        next_version = (last_proj.get("version", 0) + 1) if last_proj else 1

        # Crear proyecto con esquema paramétrico
        proyecto = {
            "finca_id": finca_id,
            "autor_tipo": autor_tipo,
            "version": next_version,
            "json_distribucion": plan_json,
            "total_m2": plan_json.get("program", {}).get("total_m2", 0),
            "ubicacion": get_finca(finca_id).get("ubicacion_geo"),
            "ref_catastral": get_finca(finca_id).get("ref_catastral"),
            "titulo": f"Proyecto Paramétrico v{next_version}",
            "descripcion": f"Plan paramétrico completo - {plan_json.get('program', {}).get('total_m2', 0)} m²",
            "presupuesto": plan_json.get("program", {}).get("total_m2", 0) * 950,  # €950/m² estimado
            "esquema_parametrico": True,  # Flag para identificar planes paramétricos
            "materials": plan_json.get("materials", {}),
            "systems": plan_json.get("systems", {}),
            "furniture": plan_json.get("furniture", [])
        }

        # Guardar usando función existente
        saved = save_proyecto(proyecto)

        # Añadir metadatos del esquema paramétrico
        saved["parametric_metadata"] = {
            "site_info": plan_json.get("site", {}),
            "constraints": plan_json.get("constraints", {}),
            "render_settings": plan_json.get("render", {}),
            "history": plan_json.get("history", [])
        }

        return saved

    except Exception as e:
        print(f"Error guardando plan paramétrico: {e}")
        return {}

def get_plan_parametrico(proyecto_id: int) -> dict:
    """
    Recupera un plan paramétrico completo por ID de proyecto.
    Microcirugía: recontruye esquema desde datos guardados.
    """
    try:
        proyecto = get_proyecto(proyecto_id)
        if not proyecto or not proyecto.get("esquema_parametrico"):
            return {}

        # Reconstruir esquema paramétrico completo
        plan_json = proyecto.get("json_distribucion", {})

        # Asegurar esquema completo
        from design_ops import ensure_plan_schema
        finca = get_finca(proyecto.get("finca_id", 0))
        plan_completo = ensure_plan_schema(plan_json, finca)

        # Añadir metadatos del proyecto
        plan_completo["project_metadata"] = {
            "id": proyecto["id"],
            "version": proyecto.get("version", 1),
            "autor_tipo": proyecto.get("autor_tipo", "unknown"),
            "titulo": proyecto.get("titulo", ""),
            "descripcion": proyecto.get("descripcion", ""),
            "presupuesto": proyecto.get("presupuesto", 0)
        }

        return plan_completo

    except Exception as e:
        print(f"Error recuperando plan paramétrico: {e}")
        return {}

def list_planes_parametricos_by_finca(finca_id: int) -> list:
    """
    Lista todos los planes paramétricos de una finca ordenados por versión.
    Microcirugía: filtra proyectos con flag parametrico.
    """
    try:
        proyectos = get_proyectos_by_finca(finca_id)
        parametricos = [p for p in proyectos if p.get("esquema_parametrico")]

        # Enriquecer con datos del plan
        for p in parametricos:
            plan = get_plan_parametrico(p["id"])
            if plan:
                p["plan_summary"] = {
                    "total_m2": plan.get("program", {}).get("total_m2", 0),
                    "rooms_count": len(plan.get("program", {}).get("rooms", [])),
                    "has_pool": plan.get("site", {}).get("pool", {}).get("exists", False),
                    "roof_type": plan.get("roof", {}).get("type", "unknown"),
                    "foundation_type": plan.get("structure", {}).get("foundation", {}).get("type", "unknown")
                }

        return parametricos

    except Exception as e:
        print(f"Error listando planes paramétricos: {e}")
        return []

def migrate_plan_to_parametric(plan_legacy: dict, finca: dict) -> dict:
    """
    Migra un plan legacy al nuevo esquema paramétrico.
    Microcirugía: transformación compatible hacia atrás.
    """
    try:
        # Extraer habitaciones del plan legacy
        habitaciones = plan_legacy.get("habitaciones", [])
        banos = plan_legacy.get("banos", [])
        estancias_principales = plan_legacy.get("estancias_principales", [])

        # Convertir a esquema paramétrico
        rooms = []

        # Convertir habitaciones
        for i, hab in enumerate(habitaciones):
            rooms.append({
                "id": f"room_{i+1}",
                "type": "bedroom",
                "area": hab.get("m2", 12),
                "name": hab.get("nombre", f"Dormitorio {i+1}"),
                "floor": 0,
                "position": {"x": 0, "y": 0},  # Posición por defecto
                "dimensions": {"width": 4, "length": hab.get("m2", 12) / 4}
            })

        # Convertir baños
        for i, ban in enumerate(banos):
            rooms.append({
                "id": f"bathroom_{i+1}",
                "type": "bathroom",
                "area": ban.get("m2", 6),
                "name": ban.get("nombre", f"Baño {i+1}"),
                "floor": 0,
                "position": {"x": 0, "y": 0},
                "dimensions": {"width": 3, "length": ban.get("m2", 6) / 3}
            })

        # Convertir estancias principales
        for i, est in enumerate(estancias_principales):
            room_type = "living" if "salon" in est.get("nombre", "").lower() else "kitchen"
            rooms.append({
                "id": f"main_{i+1}",
                "type": room_type,
                "area": est.get("m2", 20),
                "name": est.get("nombre", f"Estancia {i+1}"),
                "floor": 0,
                "position": {"x": 0, "y": 0},
                "dimensions": {"width": 5, "length": est.get("m2", 20) / 5}
            })

        # Crear plan paramétrico
        plan_parametrico = {
            "site": {
                "area": finca.get("superficie_m2", 0),
                "setbacks": finca.get("retranqueos", {"front": 5, "side": 3, "back": 5}),
                "buildable_max": int(finca.get("superficie_m2", 0) * 0.33),
                "pool": {"area": 0, "position": "south", "exists": False}
            },
            "program": {
                "rooms": rooms,
                "total_m2": sum(r["area"] for r in rooms),
                "floors": 1
            },
            "layout": {
                "walls": [],
                "openings": [],
                "levels": [{"height": 2.8, "index": 0, "name": "Planta Baja"}],
                "dimensions": {"width": 15, "length": 20}
            },
            "structure": {
                "foundation": {"type": "slab", "depth": 0.5, "material": "concrete"},
                "structure_type": "concrete"
            },
            "roof": {
                "type": "flat",
                "pitch_deg": 0,
                "material": "concrete"
            },
            "systems": {
                "plumbing": {"fixtures": [], "pipes": []},
                "electric": {"outlets": [], "lighting": [], "panels": []},
                "hvac": {"units": [], "ducts": []}
            },
            "materials": {
                "exterior": {"walls": "brick", "roof": "tiles", "windows": "aluminum", "doors": "wood"},
                "interior": {"walls": "plaster", "floors": "ceramic", "ceilings": "plaster", "doors": "wood"},
                "finishes": {"kitchen": "granite", "bathrooms": "ceramic", "floors": "parquet"}
            },
            "furniture": {
                "kitchen": [],
                "bathrooms": [],
                "bedrooms": [],
                "living": []
            },
            "constraints": {
                "max_height": 10,
                "occupancy_ratio": 0.3,
                "setback_front": 5,
                "setback_side": 3,
                "setback_back": 5,
                "max_floors": 2
            },
            "render": {
                "lighting": "day",
                "cameras": [],
                "quality": "medium",
                "show_furniture": True,
                "show_dimensions": True
            },
            "history": [{
                "action": "migration_from_legacy",
                "legacy_plan": plan_legacy,
                "timestamp": "now",
                "author": "system"
            }]
        }

        return plan_parametrico

    except Exception as e:
        print(f"Error en migración: {e}")
        return {}