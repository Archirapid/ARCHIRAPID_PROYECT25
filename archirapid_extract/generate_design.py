"""
ARCHIRAPID - Diseñador Paramétrico Asistido
Genera diseños arquitectónicos preliminares basados en datos catastrales validados.

FASE 1: Implementación Core sin dependencias de IA
- Carga datos de validación y geometría
- Calcula escala píxeles → metros
- Computa área edificable con retranqueos
- Genera huella óptima del edificio
- Distribuye espacios con heurísticas
- Renderiza plano 2D (PNG)
- Exporta modelo 3D (GLB)
- Estima presupuesto

Author: ARCHIRAPID Team
Date: 2025-11-13
Version: 1.0.0-FASE1
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Polygon, Point
from shapely.affinity import scale as shapely_scale
import trimesh
from functools import lru_cache


# =======================
# CONFIGURACIÓN GLOBAL
# =======================

DEFAULT_SETBACK = 3.0  # Retranqueo en metros
DEFAULT_FLOOR_HEIGHT = 3.0  # Altura por planta en metros
DEFAULT_COST_PER_M2 = 900.0  # €/m² construcción (estándar calidad media)
MIN_ROOM_AREA = 4.0  # m² mínimos por habitación


# =======================
# 1. CARGA DE DATOS
# =======================

@lru_cache(maxsize=1)
def load_inputs(base_path: str) -> Dict:
    """
    Carga datos de validación y geometría catastral.
    
    Args:
        base_path: Ruta a carpeta catastro_output/
        
    Returns:
        Dict con validation_report, geojson_polygon, success flag
    """
    result = {
        "success": False,
        "validation": None,
        "polygon": None,
        "error": None
    }
    
    # Cargar validation_report.json
    validation_path = Path(base_path) / "validation_report.json"
    if not validation_path.exists():
        result["error"] = f"No encontrado: {validation_path}"
        return result
    
    try:
        with open(validation_path, 'r', encoding='utf-8') as f:
            result["validation"] = json.load(f)
    except Exception as e:
        result["error"] = f"Error leyendo validation_report.json: {e}"
        return result
    
    # Cargar plot_polygon.geojson (NO parcel_vector.json)
    geojson_path = Path(base_path) / "plot_polygon.geojson"
    if not geojson_path.exists():
        result["error"] = f"No encontrado: {geojson_path}"
        return result
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
            
        # Extraer coordenadas del GeoJSON
        if geojson_data.get("type") == "FeatureCollection":
            features = geojson_data.get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"][0]
            else:
                result["error"] = "GeoJSON sin features"
                return result
        elif geojson_data.get("type") == "Feature":
            coords = geojson_data["geometry"]["coordinates"][0]
        else:
            coords = geojson_data.get("coordinates", [[]])[0]
        
        # Crear Polygon de Shapely (CORRECCIÓN: no usar shape() sobre dict)
        result["polygon"] = Polygon(coords)
        
    except Exception as e:
        result["error"] = f"Error leyendo plot_polygon.geojson: {e}"
        return result
    
    result["success"] = True
    return result


# =======================
# 2. ESTIMACIÓN DE ESCALA
# =======================

@lru_cache(maxsize=32)
def estimate_scale(polygon: Polygon, surface_m2: float) -> Dict:
    """
    Estima conversión píxeles → metros con validación robusta.
    
    Args:
        polygon: Polígono en coordenadas pixel/imagen
        surface_m2: Superficie real en m² del catastro
        
    Returns:
        Dict con scale_factor (m/px), bounds, validations
    """
    result = {
        "success": False,
        "scale_factor": None,
        "bounds": None,
        "area_px": None,
        "error": None,
        "confidence": "low"
    }
    
    # Área en píxeles
    area_px = polygon.area
    if area_px <= 0:
        result["error"] = "Polígono sin área válida"
        return result
    
    # Escala naive: sqrt(m²/px²)
    m2_per_px = surface_m2 / area_px
    scale_naive = np.sqrt(m2_per_px)
    
    # Validación de coherencia geométrica
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    width_px = bounds[2] - bounds[0]
    height_px = bounds[3] - bounds[1]
    
    width_m = width_px * scale_naive
    height_m = height_px * scale_naive
    
    # Validar dimensiones razonables (finca entre 5m y 500m de lado)
    if width_m < 5 or height_m < 5:
        result["error"] = f"Dimensiones irreales: {width_m:.1f}x{height_m:.1f}m"
        return result
    
    if width_m > 500 or height_m > 500:
        result["error"] = f"Dimensiones excesivas: {width_m:.1f}x{height_m:.1f}m"
        return result
    
    # Verificar área recalculada
    area_estimated = area_px * (scale_naive ** 2)
    error_percent = abs(area_estimated - surface_m2) / surface_m2 * 100
    
    if error_percent > 30:
        result["confidence"] = "low"
    elif error_percent > 10:
        result["confidence"] = "medium"
    else:
        result["confidence"] = "high"
    
    result["success"] = True
    result["scale_factor"] = scale_naive
    result["bounds"] = bounds
    result["area_px"] = area_px
    result["width_m"] = width_m
    result["height_m"] = height_m
    result["error_percent"] = error_percent
    
    return result


# =======================
# 3. ÁREA EDIFICABLE
# =======================

def compute_inner_buildable(polygon: Polygon, setback_m: float, scale_factor: float) -> Optional[Polygon]:
    """
    Calcula área edificable aplicando retranqueo (buffer negativo).
    
    Args:
        polygon: Polígono original en píxeles
        setback_m: Retranqueo en metros
        scale_factor: Conversión m/px
        
    Returns:
        Polygon edificable o None si queda vacío
    """
    # Convertir retranqueo a píxeles
    setback_px = setback_m / scale_factor
    
    # Buffer negativo
    buildable = polygon.buffer(-setback_px)
    
    # Verificar si quedó área
    if buildable.is_empty or buildable.area <= 0:
        return None
    
    return buildable


# =======================
# 4. HUELLA EDIFICIO
# =======================

def choose_footprint(buildable: Polygon, target_area_m2: float, scale_factor: float) -> Optional[Polygon]:
    """
    Inscribe rectángulo óptimo dentro del área edificable.
    
    Args:
        buildable: Polígono edificable
        target_area_m2: Área objetivo en m²
        scale_factor: Conversión m/px
        
    Returns:
        Polygon rectangular o None si falla
    """
    # Obtener bounding box del área edificable
    minx, miny, maxx, maxy = buildable.bounds
    width = maxx - minx
    height = maxy - miny
    
    # Convertir target a píxeles²
    target_px2 = target_area_m2 / (scale_factor ** 2)
    
    # Calcular dimensiones óptimas (mantener proporción del área edificable)
    aspect = width / height if height > 0 else 1.0
    
    # Resolver: w * h = target_px2, w/h = aspect
    # => h = sqrt(target_px2 / aspect)
    h_opt = np.sqrt(target_px2 / aspect)
    w_opt = h_opt * aspect
    
    # Escalar al 90% del área edificable como margen de seguridad
    scale_down = 0.9
    w_opt *= scale_down
    h_opt *= scale_down
    
    # Centrar rectángulo
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    
    rect_coords = [
        (cx - w_opt/2, cy - h_opt/2),
        (cx + w_opt/2, cy - h_opt/2),
        (cx + w_opt/2, cy + h_opt/2),
        (cx - w_opt/2, cy + h_opt/2),
        (cx - w_opt/2, cy - h_opt/2)
    ]
    
    footprint = Polygon(rect_coords)
    
    # Verificar que está dentro del área edificable
    if not buildable.contains(footprint):
        # Intentar reducir más
        for scale_attempt in [0.8, 0.7, 0.6]:
            w_test = w_opt * scale_attempt
            h_test = h_opt * scale_attempt
            rect_test = [
                (cx - w_test/2, cy - h_test/2),
                (cx + w_test/2, cy - h_test/2),
                (cx + w_test/2, cy + h_test/2),
                (cx - w_test/2, cy + h_test/2),
                (cx - w_test/2, cy - h_test/2)
            ]
            footprint_test = Polygon(rect_test)
            if buildable.contains(footprint_test):
                return footprint_test
        
        return None
    
    return footprint


# =======================
# 5. DISTRIBUCIÓN LAYOUT
# =======================

def generate_layout(footprint_area_m2: float, num_bedrooms: int = 2) -> Dict:
    """
    Genera distribución heurística de espacios.
    
    Args:
        footprint_area_m2: Área de la huella en m²
        num_bedrooms: Número de dormitorios
        
    Returns:
        Dict con espacios {nombre: m²}
    """
    layout = {}
    
    # Heurísticas de distribución
    layout["Salón-Comedor"] = footprint_area_m2 * 0.30
    layout["Cocina"] = footprint_area_m2 * 0.12
    
    # Dormitorios (mínimo 9m² cada uno)
    bedroom_area = max(footprint_area_m2 * 0.12, 9.0)
    for i in range(num_bedrooms):
        layout[f"Dormitorio {i+1}"] = bedroom_area
    
    # Baños (mínimo 4m² cada uno)
    num_bathrooms = max(1, num_bedrooms)
    bathroom_area = max(footprint_area_m2 * 0.04, 4.0)
    for i in range(num_bathrooms):
        layout[f"Baño {i+1}"] = bathroom_area
    
    # Circulación y distribución
    layout["Distribución"] = footprint_area_m2 * 0.10
    
    # Normalizar para que sume exactamente footprint_area_m2
    total_assigned = sum(layout.values())
    if total_assigned > 0:
        factor = footprint_area_m2 / total_assigned
        layout = {k: v * factor for k, v in layout.items()}
    
    return layout


# =======================
# 6. RENDERIZADO 2D
# =======================

def render_plan(polygon: Polygon, buildable: Optional[Polygon], footprint: Optional[Polygon],
                layout: Dict, scale_factor: float, output_path: str) -> bool:
    """
    Genera plano 2D en PNG con Matplotlib.
    
    Args:
        polygon: Parcela original
        buildable: Área edificable
        footprint: Huella edificio
        layout: Distribución de espacios
        scale_factor: Conversión m/px
        output_path: Ruta del PNG
        
    Returns:
        True si éxito
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 1. Parcela completa (gris claro)
        x, y = polygon.exterior.xy
        ax.fill(x, y, alpha=0.3, fc='lightgray', ec='black', linewidth=2, label='Parcela')
        
        # 2. Área edificable (verde claro)
        if buildable:
            x, y = buildable.exterior.xy
            ax.fill(x, y, alpha=0.4, fc='lightgreen', ec='green', linewidth=1.5, label='Área Edificable')
        # 3. Huella edificio (azul)
        if footprint:
            x, y = footprint.exterior.xy
            ax.fill(x, y, alpha=0.6, fc='lightblue', ec='blue', linewidth=2, label='Edificio')
            
            # Anotar dimensiones
            minx, miny, maxx, maxy = footprint.bounds
            width_m = (maxx - minx) * scale_factor
            height_m = (maxy - miny) * scale_factor
            cx = (minx + maxx) / 2
            cy = (miny + maxy) / 2
            ax.text(cx, cy, f"{width_m:.1f}m × {height_m:.1f}m\n{width_m*height_m:.1f}m²",
                   ha='center', va='center', fontsize=10, weight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 4. Leyenda de distribución
        if layout:
            legend_text = "DISTRIBUCIÓN:\n" + "\n".join([f"• {k}: {v:.1f}m²" for k, v in layout.items()])
            ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
        
        ax.set_aspect('equal')
        ax.legend(loc='upper right')
        ax.set_title('ARCHIRAPID - Plano Preliminar', fontsize=14, weight='bold')
        ax.set_xlabel('Coordenadas X (píxeles)', fontsize=10)
        ax.set_ylabel('Coordenadas Y (píxeles)', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error renderizando plano: {e}")
        return False


# =======================
# 7. EXPORTACIÓN 3D
# =======================

def export_3d(footprint: Polygon, num_floors: int, floor_height: float,
              scale_factor: float, output_path: str) -> bool:
    """
    Exporta modelo 3D en formato GLB usando Trimesh.
    
    Args:
        footprint: Huella del edificio
        num_floors: Número de plantas
        floor_height: Altura por planta (m)
        scale_factor: Conversión m/px
        output_path: Ruta del GLB
        
    Returns:
        True si éxito
    """
    try:
        # Convertir Polygon a coordenadas 3D
        coords = list(footprint.exterior.coords[:-1])  # Sin duplicar último punto
        
        # Escalar a metros
        vertices_2d = np.array(coords) * scale_factor
        
        # Crear base del edificio (Z=0)
        n_verts = len(vertices_2d)
        vertices_base = np.column_stack([vertices_2d, np.zeros(n_verts)])
        # Altura total del edificio
        total_height = num_floors * floor_height
        # Vértices superiores (techo)
        vertices_top = np.column_stack([vertices_2d, np.full(n_verts, total_height)])
        
        # Combinar vértices
        vertices = np.vstack([vertices_base, vertices_top])
        
        # Crear caras (triangulación)
        faces = []
        
        # Cara inferior (base)
        for i in range(1, n_verts - 1):
            faces.append([0, i, i + 1])
        
        # Cara superior (techo)
        for i in range(1, n_verts - 1):
            faces.append([n_verts, n_verts + i + 1, n_verts + i])
        
        # Caras laterales (paredes)
        for i in range(n_verts):
            next_i = (i + 1) % n_verts
            # Dos triángulos por cara lateral
            faces.append([i, next_i, n_verts + i])
            faces.append([next_i, n_verts + next_i, n_verts + i])
        
        # Crear mesh
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        # Exportar a GLB
        mesh.export(output_path, file_type='glb')
        
        return True
        
    except Exception as e:
        print(f"Error exportando 3D: {e}")
        return False


# =======================
# 8. PRESUPUESTO
# =======================

def estimate_budget(buildable_m2: float, num_floors: int, cost_per_m2: float = DEFAULT_COST_PER_M2) -> Dict:
    """
    Estima presupuesto de construcción.
    
    Args:
        buildable_m2: Área edificable total
        num_floors: Número de plantas
        cost_per_m2: Coste por m² construido
        
    Returns:
        Dict con desglose de presupuesto
    """
    total_m2 = buildable_m2 * num_floors
    
    budget = {
        "superficie_construida_m2": total_m2,
        "coste_por_m2_eur": cost_per_m2,
        "construccion_eur": total_m2 * cost_per_m2,
        "proyecto_licencias_eur": total_m2 * cost_per_m2 * 0.15,  # 15% adicional
        "total_estimado_eur": total_m2 * cost_per_m2 * 1.15
    }
    
    return budget


# =======================
# 9. ORQUESTADOR PRINCIPAL
# =======================

def build_project(catastro_path: str, output_dir: str, num_bedrooms: int = 2,
                  num_floors: int = 1, setback_m: float = DEFAULT_SETBACK) -> Dict:
    """
    Orquestador principal del generador de diseño.
    
    Args:
        catastro_path: Ruta a carpeta catastro_output/
        output_dir: Ruta donde guardar outputs
        num_bedrooms: Número de dormitorios
        num_floors: Número de plantas
        setback_m: Retranqueo en metros
        
    Returns:
        Dict con resultados completos y rutas de archivos generados
    """
    result = {
        "success": False,
        "error": None,
        "files_generated": [],
        "metadata": {}
    }
    
    # 1. Cargar datos
    print("📂 Cargando datos catastrales...")
    inputs = load_inputs(catastro_path)
    if not inputs["success"]:
        result["error"] = inputs["error"]
        return result
    
    validation = inputs["validation"]
    polygon = inputs["polygon"]
    
    # Verificar edificabilidad
    if not validation.get("is_buildable", False):
        result["error"] = "Finca NO edificable según validación"
        return result
    
    surface_m2 = validation.get("surface_m2")
    buildable_m2 = validation.get("buildable_m2")

    # Fallback robusto: leer edificability.json si faltan valores
    if (surface_m2 is None) or (buildable_m2 is None):
        try:
            eda_path = Path(catastro_path) / "edificability.json"
            if eda_path.exists():
                with open(eda_path, 'r', encoding='utf-8') as ef:
                    eda = json.load(ef)
                if surface_m2 is None:
                    # campos esperados en edificability.json
                    s = eda.get("surface_m2")
                    if isinstance(s, (int, float)) and s > 0:
                        surface_m2 = float(s)
                if buildable_m2 is None:
                    b = eda.get("buildable_m2") or eda.get("max_buildable_m2")
                    if isinstance(b, (int, float)) and b > 0:
                        buildable_m2 = float(b)
                    else:
                        # calcular a partir de ratio si es posible
                        ratio = eda.get("edificability_percent") or eda.get("edificability_ratio")
                        if ratio is not None and surface_m2:
                            try:
                                buildable_m2 = float(surface_m2) * float(ratio)
                            except Exception:
                                pass
        except Exception:
            # Ignorar errores de fallback; validaremos abajo
            pass

    if not surface_m2 or not buildable_m2:
        result["error"] = "Datos de superficie inválidos"
        return result
    
    # 2. Estimar escala
    print("📏 Estimando escala píxeles → metros...")
    scale_info = estimate_scale(polygon, surface_m2)
    if not scale_info["success"]:
        result["error"] = scale_info["error"]
        return result
    
    scale_factor = scale_info["scale_factor"]
    result["metadata"]["scale_factor"] = scale_factor
    result["metadata"]["scale_confidence"] = scale_info["confidence"]
    
    # 3. Calcular área edificable
    print("🏗️ Calculando área edificable...")
    buildable_poly = compute_inner_buildable(polygon, setback_m, scale_factor)
    if not buildable_poly:
        result["error"] = f"Área edificable vacía con retranqueo de {setback_m}m"
        return result
    
    # 4. Calcular huella
    print("📐 Generando huella del edificio...")
    footprint = choose_footprint(buildable_poly, buildable_m2, scale_factor)
    if not footprint:
        result["error"] = "No se pudo inscribir huella en área edificable"
        return result
    
    footprint_area_m2 = footprint.area * (scale_factor ** 2)
    result["metadata"]["footprint_area_m2"] = footprint_area_m2
    
    # 5. Generar layout
    print("🏠 Generando distribución de espacios...")
    layout = generate_layout(footprint_area_m2, num_bedrooms)
    result["metadata"]["layout"] = layout
    
    # 6. Renderizar plano 2D
    print("🎨 Renderizando plano 2D...")
    os.makedirs(output_dir, exist_ok=True)
    plan_path = os.path.join(output_dir, "design_plan.png")
    
    if render_plan(polygon, buildable_poly, footprint, layout, scale_factor, plan_path):
        result["files_generated"].append(plan_path)
        print(f"✅ Plano guardado: {plan_path}")
    else:
        result["error"] = "Error generando plano 2D"
        return result
    
    # 7. Exportar modelo 3D
    print("🏢 Exportando modelo 3D...")
    model_path = os.path.join(output_dir, "design_model.glb")
    
    if export_3d(footprint, num_floors, DEFAULT_FLOOR_HEIGHT, scale_factor, model_path):
        result["files_generated"].append(model_path)
        print(f"✅ Modelo 3D guardado: {model_path}")
    else:
        result["error"] = "Error generando modelo 3D"
        return result
    
    # 8. Estimar presupuesto
    print("💰 Estimando presupuesto...")
    budget = estimate_budget(buildable_m2, num_floors)
    result["metadata"]["budget"] = budget
    
    # 9. Guardar manifest
    manifest = {
        "version": "1.0.0-FASE1",
        "generated_at": "2025-11-13",
        "inputs": {
            "surface_m2": surface_m2,
            "buildable_m2": buildable_m2,
            "num_bedrooms": num_bedrooms,
            "num_floors": num_floors,
            "setback_m": setback_m
        },
        "scale": {
            "factor_m_per_px": scale_factor,
            "confidence": scale_info["confidence"],
            "error_percent": scale_info.get("error_percent", 0)
        },
        "geometry": {
            "footprint_area_m2": footprint_area_m2,
            "building_dimensions_m": {
                "width": scale_info["width_m"],
                "height": scale_info["height_m"]
            }
        },
        "layout": layout,
        "budget": budget,
        "files": result["files_generated"]
    }
    
    manifest_path = os.path.join(output_dir, "design_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    result["files_generated"].append(manifest_path)
    print(f"✅ Manifest guardado: {manifest_path}")
    
    result["success"] = True
    result["metadata"]["manifest"] = manifest
    print("\n🎉 Diseño generado exitosamente!")
    
    return result


# =======================
# FUNCIÓN DE PRUEBA
# =======================

if __name__ == "__main__":
    # Test básico
    catastro_dir = "catastro_output"
    output_dir = "design_output"
    
    result = build_project(
        catastro_path=catastro_dir,
        output_dir=output_dir,
        num_bedrooms=2,
        num_floors=1,
        setback_m=3.0
    )
    
    if result["success"]:
        print("\n✅ ÉXITO")
        print(f"Archivos generados: {len(result['files_generated'])}")
        for f in result["files_generated"]:
            print(f"  - {f}")
    else:
        print(f"\n❌ ERROR: {result['error']}")
