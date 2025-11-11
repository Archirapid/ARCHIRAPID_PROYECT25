"""
Script de configuración y verificación del sistema ArchiRapid
"""
import os
from src.asset_manager import AssetManager
from pathlib import Path
import sys
from typing import Dict, Any
import json
import shutil

def setup_environment():
    """Configurar el entorno de ARCHIRAPID"""
    # Definir rutas base
    BASE = os.path.dirname(os.path.abspath(__file__))
    UPLOADS = os.path.join(BASE, "uploads")
    
    # Crear directorio de uploads si no existe
    os.makedirs(UPLOADS, exist_ok=True)
    
    # Asegurarse de que existan los subdirectorios necesarios
    subdirs = ["plots", "projects", "registry"]
    for subdir in subdirs:
        os.makedirs(os.path.join(UPLOADS, subdir), exist_ok=True)
    
    print("✅ Directorios de uploads creados correctamente")
    print(f"📁 Ubicación: {UPLOADS}")
    print("\nEstructura creada:")
    print(f"uploads/")
    for subdir in subdirs:
        print(f"  └── {subdir}/")

def setup_environment() -> Dict[str, Any]:
    """Configura y verifica el entorno de la aplicación."""
    root_path = Path(__file__).parent
    
    # Inicializar el gestor de assets
    asset_manager = AssetManager(root_path)
    
    # Verificar estructura de directorios
    status = asset_manager.get_status_report()
    
    # Migrar imágenes antiguas si existen
    asset_manager.migrate_legacy_images()
    
    # Generar placeholders para imágenes faltantes
    asset_manager.generate_placeholders()
    
    # Verificar integridad de JSONs
    validate_json_structure()
    
    return status

def validate_json_structure() -> None:
    """Valida la estructura de los archivos JSON."""
    root_path = Path(__file__).parent
    
    # Esquemas esperados
    project_schema = {
        "required": ["id", "name", "description", "area_m2", "height_m", 
                    "price_estimate", "max_buildable_m2", "type", "suitable_for", "image"],
        "properties": {
            "id": {"type": "string"},
            "suitable_for": {"type": "array"}
        }
    }
    
    finca_schema = {
        "required": ["id", "title", "lat", "lon", "m2", "price", "type", 
                    "province", "description", "suitable_projects", "images"],
        "properties": {
            "id": {"type": "string"},
            "images": {"type": "array"}
        }
    }
    
    # Validar projects.json
    with open(root_path / 'projects.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)
        for project in projects:
            for field in project_schema["required"]:
                if field not in project:
                    raise ValueError(f"Campo requerido '{field}' faltante en project {project['id']}")

    # Validar fincas.json
    with open(root_path / 'fincas.json', 'r', encoding='utf-8') as f:
        fincas = json.load(f)
        for finca in fincas:
            for field in finca_schema["required"]:
                if field not in finca:
                    raise ValueError(f"Campo requerido '{field}' faltante en finca {finca['id']}")

def main():
    """Función principal de configuración."""
    try:
        status = setup_environment()
        print("\n=== Estado del Sistema ArchiRapid ===")
        print("\nDirectorios:")
        for dir_name, exists in status['directories'].items():
            print(f"✓ {dir_name}: {'Existe' if exists else 'No existe'}")
        
        print("\nImágenes:")
        for category, count in status['images'].items():
            print(f"✓ {category}: {count} imágenes encontradas")
        
        print("\nProblemas Detectados:")
        if not any(status['issues'].values()):
            print("✓ No se encontraron problemas")
        else:
            for category, issues in status['issues'].items():
                if issues:
                    print(f"\n{category}:")
                    for issue in issues:
                        print(f"  ! {issue}")
        
        print("\nConfiguración completada exitosamente.")
        
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()