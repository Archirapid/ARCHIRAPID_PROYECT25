#!/usr/bin/env python3
"""
Diagnóstico específico del error de navegación: 'list' object has no attribute 'keys'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def diagnosticar_error_navegacion():
    print("🔍 DIAGNÓSTICO DEL ERROR DE NAVEGACIÓN")
    print("=" * 50)

    try:
        # Importar módulos principales
        import streamlit as st
        import app
        print("✅ Módulos principales importados")

        # Verificar PAGES
        if hasattr(app, 'PAGES'):
            print(f"✅ PAGES definido: {len(app.PAGES)} páginas")
            for page in app.PAGES:
                print(f"  - {page}")
        else:
            print("❌ PAGES no definido en app")

        # Verificar funciones de navegación
        if hasattr(app, 'detalles_proyecto_v2'):
            print("✅ detalles_proyecto_v2 disponible")
        else:
            print("❌ detalles_proyecto_v2 no disponible")

        # Simular session state
        class MockSessionState:
            def __init__(self):
                self.page = "Home"
                self.selected_project_v2 = None

        mock_st = MockSessionState()

        # Intentar ejecutar navegación
        print("\n🔍 Probando navegación...")

        # Simular llamada a main sin streamlit
        try:
            # Verificar si hay problemas en la lógica de navegación
            if hasattr(app, 'main'):
                print("✅ Función main disponible")
            else:
                print("❌ Función main no disponible")

        except Exception as e:
            print(f"❌ Error en main: {e}")

        # Verificar marketplace
        try:
            import modules.marketplace as marketplace
            print("✅ Marketplace importado")

            # Verificar funciones clave
            if hasattr(marketplace, 'render_home'):
                print("✅ render_home disponible")
            else:
                print("❌ render_home no disponible")

            if hasattr(marketplace, 'render_client_panel'):
                print("✅ render_client_panel disponible")
            else:
                print("❌ render_client_panel no disponible")

        except Exception as e:
            print(f"❌ Error en marketplace: {e}")

        # Verificar client_panel
        try:
            import modules.client_panel as client_panel
            print("✅ Client panel importado")

            if hasattr(client_panel, 'show_selected_project_panel'):
                print("✅ show_selected_project_panel disponible")
            else:
                print("❌ show_selected_project_panel no disponible")

        except Exception as e:
            print(f"❌ Error en client_panel: {e}")

        # Verificar posibles problemas con datos
        print("\n🔍 Verificando posibles problemas con datos...")

        try:
            import data_access
            print("✅ data_access importado")

            # Verificar funciones de datos
            if hasattr(data_access, 'get_featured_projects'):
                print("✅ get_featured_projects disponible")
                try:
                    projects = data_access.get_featured_projects()
                    print(f"✅ get_featured_projects ejecutado: {len(projects)} proyectos")
                    if projects:
                        first_project = projects[0]
                        print(f"  Tipo del primer proyecto: {type(first_project)}")
                        if isinstance(first_project, dict):
                            print(f"  Keys del proyecto: {list(first_project.keys())}")
                        elif isinstance(first_project, list):
                            print("  ⚠️  Proyecto es una lista, no un dict - ¡Este podría ser el problema!")
                            print(f"  Contenido de la lista: {first_project}")
                        else:
                            print(f"  Tipo inesperado: {type(first_project)}")
                except Exception as e:
                    print(f"❌ Error ejecutando get_featured_projects: {e}")
            else:
                print("❌ get_featured_projects no disponible")

        except Exception as e:
            print(f"❌ Error en data_access: {e}")

    except Exception as e:
        print(f"❌ Error general en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    diagnosticar_error_navegacion()