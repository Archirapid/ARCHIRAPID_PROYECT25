# export_dxf.py
# -*- coding: utf-8 -*-
"""
Módulo de exportación a formato DXF (AutoCAD) para ARCHIRAPID
Convierte polígonos vectorizados de parcelas catastrales a formato DXF

Uso:
    from export_dxf import create_dxf_from_geojson, create_dxf_from_polygon
    
    # Desde archivo GeoJSON
    dxf_bytes = create_dxf_from_geojson("plot_polygon.geojson")
    
    # Desde lista de coordenadas
    coords = [(0, 0), (100, 0), (100, 50), (0, 50)]
    dxf_bytes = create_dxf_from_polygon(coords, "Parcela 001")
"""

import ezdxf
from ezdxf import units
import json
from pathlib import Path
from typing import List, Tuple, Optional
import io


def create_dxf_from_polygon(
    coordinates: List[Tuple[float, float]],
    layer_name: str = "PARCELA",
    plot_id: str = "",
    scale_factor: float = 1.0
) -> bytes:
    """
    Crea un archivo DXF desde coordenadas de polígono
    
    Args:
        coordinates: Lista de tuplas (x, y) con las coordenadas del polígono
        layer_name: Nombre de la capa en AutoCAD
        plot_id: Identificador de la parcela (opcional)
        scale_factor: Factor de escala para convertir píxeles a metros (opcional)
    
    Returns:
        bytes: Contenido del archivo DXF en formato binario
    """
    
    # Crear nuevo documento DXF (AutoCAD 2018)
    doc = ezdxf.new('R2018', setup=True)
    doc.units = units.M  # Unidades en metros
    
    # Obtener modelspace (espacio de trabajo principal)
    msp = doc.modelspace()
    
    # Crear capa para la parcela
    doc.layers.add(layer_name, color=3, linetype='CONTINUOUS')
    
    # Aplicar factor de escala si se especifica
    if scale_factor != 1.0:
        scaled_coords = [(x * scale_factor, y * scale_factor) for x, y in coordinates]
    else:
        scaled_coords = coordinates
    
    # Cerrar el polígono si no está cerrado
    if scaled_coords[0] != scaled_coords[-1]:
        scaled_coords.append(scaled_coords[0])
    
    # Crear polilínea cerrada (POLYLINE)
    polyline = msp.add_lwpolyline(
        scaled_coords,
        dxfattribs={
            'layer': layer_name,
            'closed': True,
            'color': 3  # Verde
        }
    )
    
    # Añadir texto con ID de parcela si se proporciona
    if plot_id:
        # Calcular centro del polígono para colocar el texto
        center_x = sum(x for x, y in scaled_coords[:-1]) / (len(scaled_coords) - 1)
        center_y = sum(y for x, y in scaled_coords[:-1]) / (len(scaled_coords) - 1)
        
        msp.add_text(
            plot_id,
            dxfattribs={
                'layer': layer_name,
                'height': 2.0,
                'color': 1  # Rojo
            }
        ).set_placement((center_x, center_y))
    
    # Añadir información de área como atributo
    # Calcular área aproximada (fórmula del área de polígono)
    area = 0
    for i in range(len(scaled_coords) - 1):
        x1, y1 = scaled_coords[i]
        x2, y2 = scaled_coords[i + 1]
        area += (x1 * y2 - x2 * y1)
    area = abs(area) / 2.0
    
    # Añadir texto con área
    msp.add_text(
        f"Área: {area:.2f} m²",
        dxfattribs={
            'layer': layer_name,
            'height': 1.5,
            'color': 7  # Blanco/Negro
        }
    ).set_placement((scaled_coords[0][0], scaled_coords[0][1] - 5))
    
    # Guardar a string en memoria y convertir a bytes
    stream = io.StringIO()
    doc.write(stream)
    dxf_string = stream.getvalue()
    
    # Convertir a bytes UTF-8
    return dxf_string.encode('utf-8')


def create_dxf_from_geojson(
    geojson_path: str,
    layer_name: str = "PARCELA",
    scale_factor: float = 1.0
) -> bytes:
    """
    Crea un archivo DXF desde un archivo GeoJSON
    
    Args:
        geojson_path: Ruta al archivo GeoJSON con el polígono
        layer_name: Nombre de la capa en AutoCAD
        scale_factor: Factor de escala para convertir coordenadas
    
    Returns:
        bytes: Contenido del archivo DXF en formato binario
    
    Raises:
        FileNotFoundError: Si el archivo GeoJSON no existe
        ValueError: Si el GeoJSON no tiene el formato esperado
    """
    
    # Leer archivo GeoJSON
    geojson_file = Path(geojson_path)
    if not geojson_file.exists():
        raise FileNotFoundError(f"Archivo GeoJSON no encontrado: {geojson_path}")
    
    with open(geojson_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extraer coordenadas del GeoJSON
    if 'features' in data and len(data['features']) > 0:
        # Formato FeatureCollection
        geometry = data['features'][0]['geometry']
        coordinates = geometry['coordinates'][0]  # Primera geometría, primer anillo
        plot_id = data['features'][0].get('properties', {}).get('id', '')
    elif 'geometry' in data:
        # Formato Feature directo
        coordinates = data['geometry']['coordinates'][0]
        plot_id = data.get('properties', {}).get('id', '')
    elif 'coordinates' in data:
        # Formato Geometry directo
        coordinates = data['coordinates'][0]
        plot_id = ''
    else:
        raise ValueError("Formato de GeoJSON no reconocido")
    
    # Convertir a tuplas (x, y)
    coords_tuples = [(float(x), float(y)) for x, y in coordinates]
    
    # Crear DXF
    return create_dxf_from_polygon(
        coords_tuples,
        layer_name=layer_name,
        plot_id=plot_id,
        scale_factor=scale_factor
    )


def create_dxf_from_cadastral_output(
    output_dir: str = "catastro_output",
    scale_factor: float = 0.1
) -> Optional[bytes]:
    """
    Crea un archivo DXF desde la salida del pipeline catastral
    
    Args:
        output_dir: Directorio con los archivos de salida del pipeline
        scale_factor: Factor de escala píxeles -> metros (0.1 = 10 píxeles = 1 metro)
    
    Returns:
        bytes: Contenido del archivo DXF, o None si no se encuentra el GeoJSON
    """
    
    # Buscar archivo GeoJSON
    geojson_path = Path(output_dir) / "plot_polygon.geojson"
    
    if not geojson_path.exists():
        return None
    
    # Leer edificabilidad para añadir información
    edificability_path = Path(output_dir) / "edificability.json"
    plot_id = ""
    
    if edificability_path.exists():
        with open(edificability_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            plot_id = data.get('cadastral_reference', '')
    
    # Crear DXF con ID de parcela
    try:
        dxf_bytes = create_dxf_from_geojson(
            str(geojson_path),
            layer_name="PARCELA_CATASTRAL",
            scale_factor=scale_factor
        )
        return dxf_bytes
    except Exception as e:
        print(f"Error creando DXF: {e}")
        return None


# Script de prueba si se ejecuta directamente
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("EXPORT DXF - ARCHIRAPID")
    print("=" * 60)
    
    # Prueba con datos de ejemplo
    test_coords = [
        (0, 0),
        (100, 0),
        (100, 50),
        (50, 75),
        (0, 50)
    ]
    
    print("\n✅ Creando DXF de prueba con polígono de ejemplo...")
    dxf_data = create_dxf_from_polygon(
        test_coords,
        plot_id="TEST_001",
        scale_factor=1.0
    )
    
    # Guardar archivo de prueba
    output_path = Path("test_export.dxf")
    with open(output_path, 'wb') as f:
        f.write(dxf_data)
    
    print(f"✅ Archivo DXF creado: {output_path}")
    print(f"   Tamaño: {len(dxf_data)} bytes")
    print(f"   Coordenadas: {len(test_coords)} vértices")
    
    # Intentar crear desde output catastral si existe
    print("\n🔍 Buscando salida del pipeline catastral...")
    dxf_from_pipeline = create_dxf_from_cadastral_output()
    
    if dxf_from_pipeline:
        pipeline_path = Path("parcela_catastral.dxf")
        with open(pipeline_path, 'wb') as f:
            f.write(dxf_from_pipeline)
        print(f"✅ DXF catastral creado: {pipeline_path}")
    else:
        print("⚠️  No se encontró salida del pipeline catastral")
    
    print("\n✅ Prueba completada")
