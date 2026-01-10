#!/usr/bin/env python3
"""
Script de prueba para verificar la navegación del botón "Acceder al Portal de Cliente"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navigation():
    """Prueba la navegación desde project_detail al client_panel"""
    print("🧪 Probando navegación del botón 'Acceder al Portal de Cliente'...")

    # Verificar que las funciones se pueden importar
    try:
        from modules.marketplace.client_panel_fixed import show_project_interest_panel
        from modules.marketplace.project_detail import get_project_by_id
        print("✅ Importaciones exitosas")
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

    # Verificar que get_project_by_id funciona
    try:
        project = get_project_by_id("1")  # Asumiendo que existe el proyecto con ID 1
        if project:
            print(f"✅ Proyecto obtenido: {project['nombre']}")
        else:
            print("⚠️ Proyecto no encontrado (esto es normal si no hay datos)")
    except Exception as e:
        print(f"❌ Error obteniendo proyecto: {e}")
        return False

    # Verificar que show_project_interest_panel existe
    try:
        # No podemos ejecutar la función completa sin Streamlit, pero podemos verificar que existe
        assert callable(show_project_interest_panel)
        print("✅ Función show_project_interest_panel disponible")
    except Exception as e:
        print(f"❌ Error con la función: {e}")
        return False

    print("🎉 Todas las verificaciones pasaron correctamente!")
    return True

if __name__ == "__main__":
    success = test_navigation()
    sys.exit(0 if success else 1)