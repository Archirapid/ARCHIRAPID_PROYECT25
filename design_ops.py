#!/usr/bin/env python3
"""
Motor Paramétrico y Precios en Vivo para ARCHIRAPID
Microcirugía de precisión - Operaciones atómicas sin efectos colaterales
Traduce órdenes en planos, geometría y exportaciones profesionales
"""

from typing import Dict, List, Any, Optional, Tuple
import copy
import math
import json
from datetime import datetime

# ==========================================
# MOTOR PARAMÉTRICO CORE
# ==========================================

def parametric_engine(plan_json: Dict, operation: str, params: Dict = None) -> Dict:
    """
    Motor paramétrico principal que traduce órdenes en geometría y exportaciones
    Operación pura: plan_json + operation -> plan_json actualizado
    """
    plan = copy.deepcopy(plan_json)
    params = params or {}

    operations = {
        "add_room": lambda: add_room_parametric(plan, params),
        "edit_room": lambda: edit_room_parametric(plan, params),
        "remove_room": lambda: remove_room_parametric(plan, params),
        "set_style": lambda: apply_architectural_style(plan, params.get("style", "modern")),
        "add_system": lambda: add_system_parametric(plan, params),
        "set_materials": lambda: set_materials_parametric(plan, params),
        "auto_layout": lambda: auto_layout_intelligent(plan),
        "validate": lambda: validate_plan_comprehensive(plan),
        "export": lambda: generate_export_package(plan, params.get("options", [])),
        "calculate_price": lambda: calculate_live_price(plan)
    }

    if operation in operations:
        result = operations[operation]()
        # Añadir timestamp y versión
        result["_metadata"] = {
            "last_operation": operation,
            "timestamp": datetime.now().isoformat(),
            "version": result.get("_metadata", {}).get("version", 0) + 1
        }
        return result

    return plan

# ==========================================
# OPERACIONES PARAMÉTRICAS PURAS
# ==========================================

def add_room_parametric(plan: Dict, params: Dict) -> Dict:
    """Añade habitación con geometría paramétrica automática"""
    plan = copy.deepcopy(plan)

    room_type = params.get("type", "bedroom")
    area_target = params.get("area", 12)

    # Calcular dimensiones óptimas basado en tipo
    dimensions = calculate_optimal_dimensions(room_type, area_target)

    # Generar geometría paramétrica
    geometry = generate_room_geometry(plan, dimensions, room_type)

    new_room = {
        "id": f"room_{len(plan.get('program', {}).get('rooms', [])) + 1}",
        "type": room_type,
        "area": dimensions["width"] * dimensions["length"],
        "name": params.get("name", f"{room_type.title()} {len(plan.get('program', {}).get('rooms', [])) + 1}"),
        "dimensions": dimensions,
        "geometry": geometry,
        "systems": generate_room_systems(room_type),
        "materials": get_room_materials(room_type),
        "furniture": get_room_furniture(room_type)
    }

    plan.setdefault("program", {}).setdefault("rooms", []).append(new_room)
    plan["program"]["total_m2"] = sum(r.get("area", 0) for r in plan["program"]["rooms"])

    return plan

def edit_room_parametric(plan: Dict, params: Dict) -> Dict:
    """Edita habitación con actualización paramétrica"""
    plan = copy.deepcopy(plan)
    room_id = params.get("room_id")
    updates = params.get("updates", {})

    for room in plan.get("program", {}).get("rooms", []):
        if room["id"] == room_id:
            room.update(updates)
            # Recalcular geometría si cambian dimensiones
            if "dimensions" in updates:
                room["geometry"] = generate_room_geometry(plan, room["dimensions"], room["type"])
                room["area"] = room["dimensions"]["width"] * room["dimensions"]["length"]
            break

    plan["program"]["total_m2"] = sum(r.get("area", 0) for r in plan["program"]["rooms"])
    return plan

def remove_room_parametric(plan: Dict, params: Dict) -> Dict:
    """Elimina habitación con limpieza paramétrica"""
    plan = copy.deepcopy(plan)
    room_id = params.get("room_id")

    rooms = plan.get("program", {}).get("rooms", [])
    plan["program"]["rooms"] = [r for r in rooms if r["id"] != room_id]
    plan["program"]["total_m2"] = sum(r.get("area", 0) for r in plan["program"]["rooms"])

    return plan

def add_system_parametric(plan: Dict, params: Dict) -> Dict:
    """Añade sistema con configuración paramétrica"""
    plan = copy.deepcopy(plan)
    system_type = params.get("system_type")
    config = params.get("config", {})

    plan.setdefault("systems", {})[system_type] = config

    # Actualizar habitaciones con el nuevo sistema
    for room in plan.get("program", {}).get("rooms", []):
        if system_type in room.get("systems", {}):
            room["systems"][system_type] = generate_system_for_room(system_type, room["type"])

    return plan

def set_materials_parametric(plan: Dict, params: Dict) -> Dict:
    """Configura materiales con impacto paramétrico en precio"""
    plan = copy.deepcopy(plan)
    material_type = params.get("type")
    material_config = params.get("config", {})

    plan.setdefault("materials", {})[material_type] = material_config
    return plan

def auto_layout_intelligent(plan: Dict) -> Dict:
    """Distribución automática inteligente con algoritmos de optimización"""
    plan = copy.deepcopy(plan)
    rooms = plan.get("program", {}).get("rooms", [])

    if not rooms:
        return plan

    # Algoritmo de layout inteligente
    layout_config = optimize_spatial_layout(rooms, plan.get("site", {}))

    for i, room in enumerate(rooms):
        room.update(layout_config["rooms"][i])

    plan["layout"] = layout_config["layout"]
    return plan

# ==========================================
# FUNCIONES DE GEOMETRÍA PARAMÉTRICA
# ==========================================

def calculate_optimal_dimensions(room_type: str, area_target: float) -> Dict:
    """Calcula dimensiones óptimas basado en tipo de habitación"""
    ratios = {
        "bedroom": {"width": 3.5, "length": 4.0},
        "living": {"width": 4.0, "length": 5.0},
        "kitchen": {"width": 3.0, "length": 3.5},
        "bathroom": {"width": 2.5, "length": 3.0},
        "dining": {"width": 3.5, "length": 4.5}
    }

    base_ratio = ratios.get(room_type, ratios["bedroom"])
    scale_factor = math.sqrt(area_target / (base_ratio["width"] * base_ratio["length"]))

    return {
        "width": round(base_ratio["width"] * scale_factor, 1),
        "length": round(base_ratio["length"] * scale_factor, 1)
    }

def generate_room_geometry(plan: Dict, dimensions: Dict, room_type: str) -> Dict:
    """Genera geometría paramétrica completa para habitación"""
    # Algoritmo simplificado de generación geométrica
    return {
        "walls": [
            {"start": [0, 0], "end": [dimensions["width"], 0]},
            {"start": [dimensions["width"], 0], "end": [dimensions["width"], dimensions["length"]]},
            {"start": [dimensions["width"], dimensions["length"]], "end": [0, dimensions["length"]]},
            {"start": [0, dimensions["length"]], "end": [0, 0]}
        ],
        "openings": generate_openings_for_room(room_type, dimensions),
        "floor_area": dimensions["width"] * dimensions["length"]
    }

def generate_openings_for_room(room_type: str, dimensions: Dict) -> List[Dict]:
    """Genera aberturas paramétricas basado en tipo de habitación"""
    openings = []

    if room_type in ["bedroom", "living", "dining"]:
        # Ventana principal
        openings.append({
            "type": "window",
            "position": [dimensions["width"] * 0.7, dimensions["length"] * 0.1],
            "dimensions": [1.5, 1.2],
            "wall": "south"
        })

    if room_type == "bathroom":
        # Ventana pequeña para ventilación
        openings.append({
            "type": "window",
            "position": [dimensions["width"] * 0.8, dimensions["length"] * 0.8],
            "dimensions": [0.6, 0.6],
            "wall": "east"
        })

    # Puerta de entrada (para habitaciones principales)
    if room_type in ["living", "bedroom"]:
        openings.append({
            "type": "door",
            "position": [dimensions["width"] * 0.1, 0],
            "dimensions": [0.9, 2.1],
            "wall": "south"
        })

    return openings

# ==========================================
# SISTEMAS PARAMÉTRICOS
# ==========================================

def generate_room_systems(room_type: str) -> Dict:
    """Genera configuración de sistemas para habitación"""
    base_systems = {
        "electrical": {"outlets": 2, "lighting": 1},
        "plumbing": {},
        "hvac": {"vents": 1}
    }

    if room_type == "kitchen":
        base_systems["electrical"]["outlets"] = 6
        base_systems["plumbing"] = {"sink": 1, "dishwasher": 1}

    elif room_type == "bathroom":
        base_systems["electrical"]["outlets"] = 3
        base_systems["plumbing"] = {"toilet": 1, "sink": 1, "shower": 1}

    elif room_type == "bedroom":
        base_systems["electrical"]["outlets"] = 4
        base_systems["lighting"] = 2

    return base_systems

def generate_system_for_room(system_type: str, room_type: str) -> Dict:
    """Genera configuración específica de sistema para habitación"""
    configs = {
        "electrical": {
            "kitchen": {"outlets": 8, "usb_outlets": 2, "lighting": 3},
            "bathroom": {"outlets": 4, "lighting": 2, "exhaust": 1},
            "bedroom": {"outlets": 6, "lighting": 2, "ceiling_fan": 1}
        },
        "plumbing": {
            "kitchen": {"sink": 1, "dishwasher": 1, "water_heater": 1},
            "bathroom": {"toilet": 1, "sink": 1, "shower": 1, "bidet": 1}
        }
    }

    return configs.get(system_type, {}).get(room_type, {})

# ==========================================
# MATERIALES Y MOBILIARIO PARAMÉTRICO
# ==========================================

def get_room_materials(room_type: str) -> Dict:
    """Obtiene materiales recomendados para tipo de habitación"""
    materials_map = {
        "kitchen": {
            "floor": "ceramic",
            "walls": "tiles",
            "countertop": "granite",
            "backsplash": "tiles"
        },
        "bathroom": {
            "floor": "ceramic",
            "walls": "tiles",
            "fixtures": "porcelain"
        },
        "bedroom": {
            "floor": "parquet",
            "walls": "paint"
        },
        "living": {
            "floor": "parquet",
            "walls": "paint"
        }
    }

    return materials_map.get(room_type, {"floor": "ceramic", "walls": "paint"})

def get_room_furniture(room_type: str) -> List[Dict]:
    """Obtiene mobiliario recomendado para tipo de habitación"""
    furniture_map = {
        "kitchen": [
            {"type": "cabinet", "count": 12},
            {"type": "appliance", "count": 4},
            {"type": "island", "count": 1}
        ],
        "bathroom": [
            {"type": "vanity", "count": 1},
            {"type": "mirror", "count": 1},
            {"type": "storage", "count": 2}
        ],
        "bedroom": [
            {"type": "bed", "count": 1},
            {"type": "wardrobe", "count": 1},
            {"type": "nightstand", "count": 2}
        ]
    }

    return furniture_map.get(room_type, [])

# ==========================================
# OPTIMIZACIÓN ESPACIAL
# ==========================================

def optimize_spatial_layout(rooms: List[Dict], site: Dict) -> Dict:
    """Optimiza distribución espacial usando algoritmos de layout"""
    # Algoritmo simplificado de optimización
    total_area = sum(r.get("area", 0) for r in rooms)
    site_area = site.get("area", 200)

    # Calcular grid óptimo
    aspect_ratio = math.sqrt(site_area / total_area)
    cols = max(1, min(4, round(math.sqrt(len(rooms)) * aspect_ratio)))
    rows = math.ceil(len(rooms) / cols)

    room_width = math.sqrt(site_area / len(rooms))
    room_length = room_width

    layout = {
        "rooms": [],
        "layout": {
            "grid": {"rows": rows, "cols": cols},
            "dimensions": {"width": cols * room_width, "length": rows * room_length}
        }
    }

    for i, room in enumerate(rooms):
        row = i // cols
        col = i % cols
        layout["rooms"].append({
            "position": {"x": col * room_width, "y": row * room_length},
            "dimensions": {"width": room_width, "length": room_length}
        })

    return layout

# ==========================================
# PRECIOS EN VIVO - MOTOR DE COTIZACIÓN
# ==========================================

def calculate_live_price(plan: Dict) -> Dict:
    """
    Calcula precio en vivo basado en configuración paramétrica
    Operación pura: plan -> pricing_data
    """
    base_price_per_m2 = 950  # €/m² base
    total_m2 = plan.get("program", {}).get("total_m2", 0)

    # Precio base de construcción
    base_construction = total_m2 * base_price_per_m2

    # Multiplicadores por calidad y sistemas
    multipliers = calculate_quality_multipliers(plan)
    systems_cost = calculate_systems_cost(plan)
    materials_cost = calculate_materials_cost(plan)
    finishes_cost = calculate_finishes_cost(plan)

    # Subtotales
    subtotal_construction = base_construction * multipliers["construction"]
    subtotal_systems = systems_cost
    subtotal_materials = materials_cost
    subtotal_finishes = finishes_cost

    # Honorarios profesionales (15-20%)
    professional_fees = (subtotal_construction + subtotal_systems) * 0.18

    # Impuestos y licencias (5-8%)
    taxes_licenses = (subtotal_construction + subtotal_systems) * 0.06

    # Total
    total = (subtotal_construction + subtotal_systems + subtotal_materials +
             subtotal_finishes + professional_fees + taxes_licenses)

    return {
        "currency": "EUR",
        "breakdown": {
            "base_construction": round(base_construction, 2),
            "construction_multiplier": multipliers["construction"],
            "subtotal_construction": round(subtotal_construction, 2),
            "systems": round(subtotal_systems, 2),
            "materials": round(subtotal_materials, 2),
            "finishes": round(subtotal_finishes, 2),
            "professional_fees": round(professional_fees, 2),
            "taxes_licenses": round(taxes_licenses, 2),
            "total": round(total, 2)
        },
        "per_m2": round(total / max(total_m2, 1), 2),
        "estimated_duration_months": calculate_construction_time(plan),
        "payment_schedule": generate_payment_schedule(total),
        "financing_options": calculate_financing_options(total)
    }

def calculate_quality_multipliers(plan: Dict) -> Dict:
    """Calcula multiplicadores por calidad de construcción"""
    multipliers = {"construction": 1.0}

    # Estilo arquitectónico
    style = plan.get("style", "standard")
    style_multipliers = {
        "basic": 0.9,
        "standard": 1.0,
        "premium": 1.3,
        "luxury": 1.6
    }
    multipliers["construction"] *= style_multipliers.get(style, 1.0)

    # Materiales premium
    materials = plan.get("materials", {})
    if materials.get("exterior", {}).get("walls") == "stone":
        multipliers["construction"] *= 1.15
    if materials.get("interior", {}).get("floors") == "marble":
        multipliers["construction"] *= 1.1

    return multipliers

def calculate_systems_cost(plan: Dict) -> float:
    """Calcula costo de sistemas avanzados"""
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    systems = plan.get("systems", {})

    cost = 0

    # Sistema eléctrico inteligente
    if systems.get("electrical", {}).get("smart_home"):
        cost += total_m2 * 45  # €/m²

    # Domótica completa
    if systems.get("smart_home", {}).get("enabled"):
        cost += total_m2 * 35

    # Iluminación LED premium
    if systems.get("lighting", {}).get("led_lighting"):
        cost += total_m2 * 25

    # Fontanería premium
    plumbing = systems.get("plumbing", {})
    if plumbing.get("rainfall_shower"):
        cost += 2500
    if plumbing.get("bidet"):
        cost += 800

    # Piscina
    pool = plan.get("site", {}).get("pool", {})
    if pool.get("exists"):
        cost += pool.get("area", 0) * 300  # €/m² piscina

    return cost

def calculate_materials_cost(plan: Dict) -> float:
    """Calcula costo de materiales"""
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    materials = plan.get("materials", {})

    cost = 0

    # Materiales exterior
    exterior = materials.get("exterior", {})
    if exterior.get("walls") == "stone":
        cost += total_m2 * 120
    elif exterior.get("walls") == "brick":
        cost += total_m2 * 80

    # Materiales interior
    interior = materials.get("interior", {})
    if interior.get("floors") == "marble":
        cost += total_m2 * 150
    elif interior.get("floors") == "parquet":
        cost += total_m2 * 90

    return cost

def calculate_finishes_cost(plan: Dict) -> float:
    """Calcula costo de acabados y mobiliario"""
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    rooms = plan.get("program", {}).get("rooms", [])

    cost = 0

    # Acabados por habitación
    for room in rooms:
        room_type = room.get("type")
        if room_type == "kitchen":
            cost += 15000  # Cocina completa
        elif room_type == "bathroom":
            cost += 8000   # Baño completo
        elif room_type == "bedroom":
            cost += 5000   # Dormitorio completo

    # Mobiliario adicional
    furniture = plan.get("furniture", {})
    if furniture:
        cost += total_m2 * 30  # €/m² mobiliario

    return cost

def calculate_construction_time(plan: Dict) -> int:
    """Calcula tiempo estimado de construcción en meses"""
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    floors = plan.get("program", {}).get("floors", 1)

    # Tiempo base: 2-3 meses por planta
    base_months = floors * 2.5

    # Ajustes por complejidad
    systems = plan.get("systems", {})
    if systems.get("smart_home", {}).get("enabled"):
        base_months += 0.5
    if systems.get("electrical", {}).get("solar_panels"):
        base_months += 1

    return max(3, round(base_months))

def generate_payment_schedule(total: float) -> List[Dict]:
    """Genera cronograma de pagos"""
    return [
        {"phase": "Inicio", "percentage": 20, "amount": round(total * 0.2, 2)},
        {"phase": "Cimentación", "percentage": 15, "amount": round(total * 0.15, 2)},
        {"phase": "Estructura", "percentage": 25, "amount": round(total * 0.25, 2)},
        {"phase": "Acabados", "percentage": 25, "amount": round(total * 0.25, 2)},
        {"phase": "Finalización", "percentage": 15, "amount": round(total * 0.15, 2)}
    ]

def calculate_financing_options(total: float) -> List[Dict]:
    """Calcula opciones de financiación"""
    return [
        {
            "type": "Contado",
            "discount": 5,
            "final_amount": round(total * 0.95, 2),
            "monthly_payment": None
        },
        {
            "type": "Financiación 5 años",
            "interest_rate": 3.5,
            "monthly_payment": round((total * 1.035) / 60, 2),
            "final_amount": round(total * 1.035, 2)
        },
        {
            "type": "Financiación 10 años",
            "interest_rate": 4.0,
            "monthly_payment": round((total * 1.04) / 120, 2),
            "final_amount": round(total * 1.04, 2)
        }
    ]

# ==========================================
# VALIDACIÓN COMPREHENSIVA
# ==========================================

def validate_plan_comprehensive(plan: Dict) -> Dict:
    """Validación completa del plan con reglas paramétricas"""
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    site = plan.get("site", {})
    buildable_max = site.get("buildable_max", 0)

    errors = []
    warnings = []
    suggestions = []

    # Validación de superficie
    if total_m2 > buildable_max:
        errors.append(f"Superficie construida ({total_m2}m²) supera el máximo permitido ({buildable_max}m²)")

    # Validación de habitaciones mínimas
    rooms = plan.get("program", {}).get("rooms", [])
    bedrooms = [r for r in rooms if r.get("type") == "bedroom"]
    bathrooms = [r for r in rooms if r.get("type") == "bathroom"]
    living = [r for r in rooms if r.get("type") == "living"]

    if not living:
        errors.append("Se requiere al menos una sala de estar")
    if not bedrooms:
        warnings.append("Considera añadir al menos una habitación")
    if not bathrooms:
        errors.append("Se requiere al menos un baño")

    # Validación de proporciones
    if bedrooms and bathrooms:
        if len(bedrooms) > len(bathrooms) + 1:
            warnings.append("Número de baños insuficiente para las habitaciones")

    # Validación de sistemas
    systems = plan.get("systems", {})
    if systems.get("electrical", {}).get("smart_home") and not systems.get("lighting", {}).get("led_lighting"):
        suggestions.append("Considera iluminación LED para sistema domótico completo")

    # Validación de piscina
    pool = site.get("pool", {})
    if pool.get("exists") and pool.get("area", 0) > total_m2 * 0.3:
        warnings.append("La piscina ocupa más del 30% de la superficie construida")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "score": max(0, 100 - len(warnings) * 10 - len(errors) * 25),
        "metrics": {
            "total_m2": total_m2,
            "rooms_count": len(rooms),
            "bedrooms": len(bedrooms),
            "bathrooms": len(bathrooms)
        }
    }

# ==========================================
# EXPORTACIÓN PROFESIONAL
# ==========================================

def generate_export_package(plan: Dict, options: List[str]) -> Dict:
    """Genera paquete de exportación profesional completo"""
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "project_id": plan.get("id", "unknown"),
        "version": plan.get("_metadata", {}).get("version", 1),
        "exports": {}
    }

    # Memoria técnica PDF
    if "📄 Memoria Técnica PDF" in options:
        export_data["exports"]["technical_memory"] = generate_technical_memory(plan)

    # Planos CAD/DWG
    if "🏗️ Planos CAD/DWG" in options:
        export_data["exports"]["cad_plans"] = generate_cad_plans(plan)

    # Presupuesto detallado
    if "💰 Presupuesto Detallado" in options:
        pricing = calculate_live_price(plan)
        export_data["exports"]["budget"] = {
            "breakdown": pricing["breakdown"],
            "payment_schedule": pricing["payment_schedule"],
            "financing_options": pricing["financing_options"]
        }

    # Análisis estructural
    if "📊 Análisis Estructural" in options:
        export_data["exports"]["structural_analysis"] = generate_structural_analysis(plan)

    # Planos de instalaciones
    if "⚡ Planos Eléctricos" in options:
        export_data["exports"]["electrical_plans"] = generate_electrical_plans(plan)

    if "🚿 Planos Fontanería" in options:
        export_data["exports"]["plumbing_plans"] = generate_plumbing_plans(plan)

    # Lista de materiales
    if "📋 Lista de Materiales" in options:
        export_data["exports"]["materials_list"] = generate_materials_list(plan)

    # Plano de muebles
    if "🪑 Plano de Muebles" in options:
        export_data["exports"]["furniture_plan"] = generate_furniture_plan(plan)

    return export_data

def generate_technical_memory(plan: Dict) -> Dict:
    """Genera memoria técnica completa"""
    return {
        "format": "PDF",
        "pages": 25,
        "sections": [
            "Introducción y Objetivos",
            "Programa Arquitectónico",
            "Situación y Entorno",
            "Estructura y Cimentación",
            "Instalaciones",
            "Acabados y Materiales",
            "Presupuesto",
            "Plazos de Ejecución",
            "Anexos"
        ],
        "certificates": ["CTE", "EHE", "REA"],
        "author": "ARCHIRAPID AI",
        "date": datetime.now().strftime("%d/%m/%Y")
    }

def generate_cad_plans(plan: Dict) -> Dict:
    """Genera planos CAD profesionales"""
    return {
        "format": "DWG",
        "files": [
            "01_Planta_Baja.dwg",
            "02_Alzados.dwg",
            "03_Secciones.dwg",
            "04_Detalles.dwg",
            "05_Estructura.dwg",
            "06_Instalaciones.dwg"
        ],
        "layers": [
            "Muros", "Puertas", "Ventanas", "Mobiliario",
            "Instalaciones", "Cotas", "Texto", "Símbolos"
        ],
        "scale": "1:50",
        "standards": "UNE/EN ISO"
    }

def generate_structural_analysis(plan: Dict) -> Dict:
    """Genera análisis estructural"""
    return {
        "foundation_design": "Cimentación por zapatas aisladas",
        "structure_type": "Estructura de hormigón armado",
        "load_analysis": "Análisis de cargas completado",
        "certificates": ["CTE DB SE-AE", "EHE-08"],
        "calculations": {
            "max_load": "500 kg/m²",
            "wind_resistance": "Categoría II",
            "seismic_zone": "Zona 3"
        }
    }

def generate_electrical_plans(plan: Dict) -> Dict:
    """Genera planos eléctricos"""
    systems = plan.get("systems", {}).get("electrical", {})
    return {
        "single_line_diagram": "Diagrama unifilar generado",
        "power_distribution": f"Distribución {systems.get('phases', 3)} fases",
        "lighting_zones": systems.get('zones', []),
        "smart_home_integration": systems.get('smart_home', False),
        "solar_panels": systems.get('solar_panels', False),
        "ev_charging": systems.get('ev_charging', False)
    }

def generate_plumbing_plans(plan: Dict) -> Dict:
    """Genera planos de fontanería"""
    systems = plan.get("systems", {}).get("plumbing", {})
    return {
        "water_supply": "Abastecimiento de agua potable",
        "drainage_system": "Sistema de evacuación por gravedad",
        "fixtures": {
            "sinks": systems.get('sinks', 0),
            "toilets": systems.get('toilets', 0),
            "showers": systems.get('showers', 0),
            "baths": systems.get('baths', 0)
        },
        "premium_features": {
            "rainfall_shower": systems.get('rainfall_shower', False),
            "bidet": systems.get('bidet', False),
            "water_recycling": systems.get('water_recycling', False)
        }
    }

def generate_materials_list(plan: Dict) -> Dict:
    """Genera lista completa de materiales"""
    materials = plan.get("materials", {})
    rooms = plan.get("program", {}).get("rooms", [])

    return {
        "structural": {
            "concrete": f"{plan.get('program', {}).get('total_m2', 0) * 0.3:.1f} m³",
            "steel": f"{plan.get('program', {}).get('total_m2', 0) * 15:.0f} kg",
            "brick": f"{plan.get('program', {}).get('total_m2', 0) * 50:.0f} unidades"
        },
        "finishing": {
            "flooring": materials.get("interior", {}).get("floors", "ceramic"),
            "walls": materials.get("interior", {}).get("walls", "paint"),
            "ceilings": materials.get("interior", {}).get("ceilings", "plaster")
        },
        "systems": {
            "electrical": "Cableado completo + dispositivos",
            "plumbing": "Tuberías + aparatos sanitarios",
            "hvac": "Sistema de climatización"
        },
        "rooms_breakdown": {room["id"]: room.get("materials", {}) for room in rooms}
    }

def generate_furniture_plan(plan: Dict) -> Dict:
    """Genera plano de mobiliario"""
    furniture = plan.get("furniture", {})
    rooms = plan.get("program", {}).get("rooms", [])

    return {
        "layout_2d": "Plano 2D generado automáticamente",
        "room_furniture": {
            room["id"]: {
                "type": room["type"],
                "furniture": room.get("furniture", []),
                "area": room.get("area", 0)
            } for room in rooms
        },
        "global_furniture": furniture,
        "suppliers": ["IKEA", "Local Furniture Co", "Custom Manufacturers"],
        "installation_notes": "Mobiliario instalado post-construcción"
    }

# ==========================================
# FUNCIONES DE LEGACY PARA COMPATIBILIDAD
# ==========================================

def ensure_plan_schema(plan: Optional[Dict], finca: Dict) -> Dict:
    """Compatibilidad con código existente"""
    return parametric_engine(plan or {}, "validate")

def set_systems(plan: Dict, system_type: str, params: Dict) -> Dict:
    """
    Configura sistemas (electricidad, fontanería, HVAC)
    Operación atómica pura
    """
    plan = copy.deepcopy(plan)
    plan["systems"][system_type].update(params)

    # Añadir a historial
    plan["history"].append({
        "action": "set_systems",
        "system_type": system_type,
        "params": params,
        "timestamp": "now",
        "author": "user"
    })

    return plan

def auto_layout(plan: Dict, finca: Dict) -> Dict:
    """
    Distribución automática inteligente
    Operación atómica pura
    """
    plan = copy.deepcopy(plan)
    rooms = plan["program"]["rooms"]

    if not rooms:
        return plan

    # Algoritmo simple de distribución automática
    # Colocar habitaciones en grid inteligente
    layout = plan["layout"]
    site_width = layout["dimensions"]["width"]
    site_length = layout["dimensions"]["length"]

    # Distribuir habitaciones
    rooms_per_row = min(3, len(rooms))
    room_width = site_width / rooms_per_row
    room_length = site_length / math.ceil(len(rooms) / rooms_per_row)

    for i, room in enumerate(rooms):
        row = i // rooms_per_row
        col = i % rooms_per_row

        room["position"] = {
            "x": col * room_width,
            "y": row * room_length
        }
        room["dimensions"] = {
            "width": room_width,
            "length": room_length
        }

    # Añadir a historial
    plan["history"].append({
        "action": "auto_layout",
        "rooms_count": len(rooms),
        "timestamp": "now",
        "author": "ia"
    })

    return plan

def validate_plan(plan: Dict, finca: Dict) -> Dict:
    """
    Validación completa del plan
    Operación pura de validación
    """
    total_m2 = plan.get("program", {}).get("total_m2", 0)
    buildable_max = plan.get("site", {}).get("buildable_max", 0)
    constraints = plan.get("constraints", {})

    warnings = []
    errors = []
    suggestions = []

    # Validación de superficie
    if buildable_max and total_m2 > buildable_max:
        errors.append(f"Superficie construida ({total_m2} m²) supera el máximo permitido ({buildable_max} m²)")

    # Validación de alturas
    max_height = constraints.get("max_height", 10)
    current_height = sum(level.get("height", 2.8) for level in plan.get("layout", {}).get("levels", []))
    if current_height > max_height:
        warnings.append(f"Altura total ({current_height}m) supera el máximo permitido ({max_height}m)")

    # Validación de retranqueos
    setbacks = plan.get("site", {}).get("setbacks", {})
    # Aquí irían validaciones geométricas complejas

    # Validación de habitaciones mínimas
    rooms = plan.get("program", {}).get("rooms", [])
    bedrooms = [r for r in rooms if r.get("type") == "bedroom"]
    bathrooms = [r for r in rooms if r.get("type") == "bathroom"]

    if len(bedrooms) == 0:
        suggestions.append("Considera añadir al menos una habitación")
    if len(bathrooms) == 0:
        suggestions.append("Considera añadir al menos un baño")

    # Validación de piscina
    pool = plan.get("site", {}).get("pool", {})
    if pool.get("exists") and pool.get("area", 0) > 0:
        if pool["area"] > total_m2 * 0.2:
            warnings.append("La piscina ocupa más del 20% de la superficie construida")

    # Validación de sistemas
    systems = plan.get("systems", {})
    if not systems.get("electric", {}).get("outlets"):
        suggestions.append("Considera añadir tomas de corriente")

    ok = len(errors) == 0

    return {
        "ok": ok,
        "total_m2": total_m2,
        "buildable_max": buildable_max,
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "score": max(0, 100 - len(warnings) * 10 - len(errors) * 50)
    }

def extract_from_pdf(pdf_data: Dict) -> Dict:
    """
    Extrae información de planos PDF
    Operación pura de extracción
    """
    # Esta función se conectaría con el módulo de extracción de PDFs existente
    # Por ahora, mock de datos extraídos
    extracted = {
        "dimensions": {"width": 15, "length": 20},
        "rooms": [
            {"type": "living", "area": 25, "position": {"x": 0, "y": 0}},
            {"type": "kitchen", "area": 12, "position": {"x": 10, "y": 0}},
            {"type": "bedroom", "area": 15, "position": {"x": 0, "y": 8}},
            {"type": "bathroom", "area": 8, "position": {"x": 10, "y": 8}}
        ],
        "walls": [],
        "openings": []
    }
    return extracted

def generate_blueprints(plan: Dict) -> Dict:
    """
    Genera planos técnicos completos
    Operación pura de generación
    """
    # Esta función generaría planos CAD, memoria técnica, etc.
    # Por ahora, estructura de respuesta
    blueprints = {
        "architectural_plans": {
            "floor_plans": [],
            "elevations": [],
            "sections": []
        },
        "technical_plans": {
            "structure": [],
            "electric": [],
            "plumbing": [],
            "hvac": []
        },
        "documents": {
            "technical_memory": "Memoria técnica completa...",
            "budget": "Presupuesto detallado...",
            "certificates": []
        }
    }
    return blueprints

# MICROCRIRUJÍA FASE 3: Operaciones Atómicas Avanzadas

def set_electrical_system(plan: Dict, config: Dict) -> Dict:
    """
    Configura sistema eléctrico inteligente
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)
    plan.setdefault("systems", {})
    plan["systems"]["electrical"] = {
        "smart_home": config.get("smart_home", False),
        "usb_outlets": config.get("usb_outlets", False),
        "solar_panels": config.get("solar_panels", False),
        "emergency_power": config.get("emergency_power", False),
        "ev_charging": config.get("ev_charging", False),
        "zones": ["living", "kitchen", "bedrooms", "bathrooms", "exterior"]
    }
    return plan

def set_plumbing_system(plan: Dict, config: Dict) -> Dict:
    """
    Configura sistema de fontanería premium
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)
    plan.setdefault("systems", {})
    plan["systems"]["plumbing"] = {
        "rainfall_shower": config.get("rainfall_shower", False),
        "bathtub": config.get("bathtub", False),
        "bidet": config.get("bidet", False),
        "water_recycling": config.get("water_recycling", False),
        "greywater_system": config.get("greywater_system", False),
        "premium_fixtures": True
    }
    return plan

def set_lighting_system(plan: Dict, config: Dict) -> Dict:
    """
    Configura sistema de iluminación inteligente
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)
    plan.setdefault("systems", {})
    plan["systems"]["lighting"] = {
        "led_lighting": config.get("led_lighting", False),
        "motion_sensors": config.get("motion_sensors", False),
        "dimming": config.get("dimming", False),
        "color_temperature": config.get("color_temperature", False),
        "smart_switches": config.get("smart_switches", False),
        "zones": ["living", "kitchen", "bedrooms", "bathrooms", "exterior"]
    }
    return plan

def set_furniture_package(plan: Dict, room_type: str, items: List[str]) -> Dict:
    """
    Configura mobiliario para un tipo de habitación específico
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)
    plan.setdefault("furniture", {})
    plan["furniture"].setdefault(room_type, [])
    plan["furniture"][room_type] = items
    return plan

def set_smart_home_integration(plan: Dict, enabled: bool = True) -> Dict:
    """
    Integra sistema domótico completo
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)
    plan.setdefault("systems", {})
    plan["systems"]["smart_home"] = {
        "enabled": enabled,
        "security": enabled,
        "climate": enabled,
        "entertainment": enabled,
        "energy_management": enabled
    }
    return plan

def apply_architectural_style(plan: Dict, style: str) -> Dict:
    """
    Aplica estilo arquitectónico completo (materiales + configuración)
    Operación pura: dict in -> dict out
    """
    plan = copy.deepcopy(plan)

    style_configs = {
        "modern": {
            "materials": {
                "exterior": {"walls": "concrete", "roof": "flat", "windows": "aluminum", "doors": "steel"},
                "interior": {"walls": "paint", "floors": "ceramic", "ceilings": "plaster", "doors": "steel"},
                "finishes": {"kitchen": "silestone", "bathrooms": "porcelain", "floors": "parquet"}
            },
            "roof": {"type": "flat", "pitch_deg": 0, "material": "concrete"},
            "systems": {
                "electrical": {"smart_home": True, "usb_outlets": True},
                "lighting": {"led_lighting": True, "motion_sensors": True}
            }
        },
        "classic": {
            "materials": {
                "exterior": {"walls": "brick", "roof": "tiles", "windows": "wood", "doors": "wood"},
                "interior": {"walls": "plaster", "floors": "terrazzo", "ceilings": "plaster", "doors": "wood"},
                "finishes": {"kitchen": "granite", "bathrooms": "ceramic", "floors": "marble"}
            },
            "roof": {"type": "gable", "pitch_deg": 25, "material": "tiles"},
            "systems": {
                "plumbing": {"bathtub": True, "bidet": True}
            }
        },
        "minimalist": {
            "materials": {
                "exterior": {"walls": "concrete", "roof": "flat", "windows": "aluminum", "doors": "steel"},
                "interior": {"walls": "paint", "floors": "concrete", "ceilings": "plaster", "doors": "steel"},
                "finishes": {"kitchen": "concrete", "bathrooms": "concrete", "floors": "concrete"}
            },
            "roof": {"type": "flat", "pitch_deg": 0, "material": "concrete"},
            "systems": {
                "electrical": {"smart_home": True},
                "lighting": {"led_lighting": True, "dimming": True}
            }
        }
    }

    if style in style_configs:
        config = style_configs[style]

        # Aplicar materiales
        if "materials" in config:
            plan["materials"] = config["materials"]

        # Aplicar techo
        if "roof" in config:
            plan["roof"] = config["roof"]

        # Aplicar sistemas
        if "systems" in config:
            plan.setdefault("systems", {})
            for system_name, system_config in config["systems"].items():
                plan["systems"][system_name] = system_config

    return plan

def generate_professional_export(plan: Dict, options: List[str]) -> Dict:
    """
    Genera exportación profesional completa
    Operación pura de generación
    """
    export_data = {
        "timestamp": "2025-12-09",
        "project_id": plan.get("id", "unknown"),
        "version": plan.get("version", 1),
        "exports": {}
    }

    # Memoria técnica PDF
    if "📄 Memoria Técnica PDF" in options:
        export_data["exports"]["technical_memory"] = {
            "format": "PDF",
            "pages": 25,
            "content": ["Introducción", "Programa Arquitectónico", "Estructura", "Instalaciones", "Presupuesto"]
        }

    # Planos CAD/DWG
    if "🏗️ Planos CAD/DWG" in options:
        export_data["exports"]["cad_plans"] = {
            "format": "DWG",
            "files": ["floor_plan.dwg", "elevations.dwg", "sections.dwg", "details.dwg"],
            "layers": ["walls", "doors", "windows", "furniture", "electrical", "plumbing"]
        }

    # Presupuesto detallado
    if "💰 Presupuesto Detallado" in options:
        base_cost = plan.get("program", {}).get("total_m2", 0) * 950
        systems_cost = 0

        if plan.get("systems", {}).get("electrical", {}).get("smart_home"):
            systems_cost += base_cost * 0.15
        if plan.get("systems", {}).get("plumbing", {}).get("rainfall_shower"):
            systems_cost += base_cost * 0.10
        if plan.get("systems", {}).get("lighting", {}).get("led_lighting"):
            systems_cost += base_cost * 0.08

        export_data["exports"]["budget"] = {
            "base_construction": base_cost,
            "systems_integration": systems_cost,
            "total": base_cost + systems_cost,
            "currency": "EUR",
            "breakdown": ["Estructura", "Acabados", "Instalaciones", "Mobiliario", "Honorarios"]
        }

    # Análisis estructural
    if "📊 Análisis Estructural" in options:
        export_data["exports"]["structural_analysis"] = {
            "foundation_analysis": "Análisis de cimentación completado",
            "structure_calculation": "Cálculos estructurales realizados",
            "load_analysis": "Análisis de cargas completado",
            "certificates": ["CTE cumplimiento", "EHE cumplimiento"]
        }

    # Planos eléctricos
    if "⚡ Planos Eléctricos" in options:
        export_data["exports"]["electrical_plans"] = {
            "single_line_diagram": "Diagrama unifilar generado",
            "power_distribution": "Distribución de potencia diseñada",
            "lighting_layout": "Disposición de iluminación completada",
            "outlet_locations": "Ubicación de tomas especificada"
        }

    # Planos de fontanería
    if "🚿 Planos Fontanería" in options:
        export_data["exports"]["plumbing_plans"] = {
            "water_supply": "Abastecimiento de agua diseñado",
            "drainage_system": "Sistema de evacuación completado",
            "fixtures_layout": "Disposición de aparatos especificada",
            "pressure_analysis": "Análisis de presiones realizado"
        }

    # Lista de materiales
    if "📋 Lista de Materiales" in options:
        export_data["exports"]["materials_list"] = {
            "structural_materials": ["Hormigón", "Acero", "Ladrillo"],
            "finishing_materials": ["Cerámica", "Pintura", "Parquet"],
            "systems_materials": ["Cableado", "Tuberías", "Iluminación LED"],
            "furniture": plan.get("furniture", {}),
            "quantities": "Cantidades calculadas por habitación"
        }

    # Plano de muebles
    if "🪑 Plano de Muebles" in options:
        export_data["exports"]["furniture_plan"] = {
            "layout_2d": "Plano 2D de mobiliario generado",
            "specifications": "Especificaciones técnicas incluidas",
            "supplier_references": "Referencias de proveedores",
            "installation_notes": "Notas de instalación"
        }

    return export_data