"""
Script para generar imágenes de marcador de posición para las fincas
"""
from src.asset_manager import AssetManager
from pathlib import Path

def generate_finca_placeholders():
    """Genera las imágenes de marcador de posición para las fincas."""
    asset_manager = AssetManager(Path(__file__).parent)
    
    # Generar imágenes para fincas
    descriptions = {
        1: ["Vista Principal - Finca Galicia", "Vista Jardín - Finca Galicia"],
        2: ["Vista Panorámica - Finca Alentejo", "Vista Campo - Finca Alentejo"],
        3: ["Vista Frontal - Finca Castilla", "Vista Lateral - Finca Castilla"]
    }
    
    for finca_num, views in descriptions.items():
        for idx, desc in enumerate(views, 1):
            image_path = asset_manager.fincas_path / f"finca{finca_num}_{idx}.png"
            if not image_path.exists():
                print(f"Generando imagen: {image_path.name}")
                asset_manager.create_placeholder_image(image_path, desc)
            else:
                print(f"La imagen {image_path.name} ya existe")

    print("\nGeneración de imágenes completada.")
    status = asset_manager.get_status_report()
    print(f"Total de imágenes de fincas: {status['images']['fincas']}")

if __name__ == "__main__":
    generate_finca_placeholders()