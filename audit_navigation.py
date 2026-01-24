import sys
sys.path.append('.')

print('🔍 AUDITORÍA PROFUNDA - FLUJO DE USUARIO')
print('=' * 50)

# Simular navegación por páginas principales
try:
    import app
    print('✅ App principal importada')

    # Verificar que las páginas principales existen en PAGES
    if hasattr(app, 'PAGES'):
        pages = app.PAGES
        print(f'✅ PAGES es de tipo: {type(pages)}')

        if isinstance(pages, dict):
            print(f'✅ Páginas disponibles: {list(pages.keys())}')
            # Verificar páginas críticas
            required_pages = ['🏠 Home', '🏪 Marketplace', '👤 Panel Cliente']
            for page in required_pages:
                if page in pages:
                    print(f'✅ Página \"{page}\" disponible')
                else:
                    print(f'❌ Página \"{page}\" NO encontrada')
        elif isinstance(pages, list):
            print(f'✅ Páginas disponibles (lista): {pages}')
            # Verificar páginas críticas
            required_pages = ['🏠 Inicio / Marketplace', 'Arquitectos (Marketplace)', '👤 Panel de Cliente']
            for page in required_pages:
                if page in pages:
                    print(f'✅ Página \"{page}\" disponible')
                else:
                    print(f'❌ Página \"{page}\" NO encontrada')
        else:
            print(f'❌ PAGES tiene tipo inesperado: {type(pages)}')
    else:
        print('❌ PAGES no definido en app.py')

except Exception as e:
    print(f'❌ Error en navegación: {e}')

# Verificar módulos marketplace
try:
    from modules.marketplace import client_panel
    import modules.marketplace.marketplace as marketplace_module
    print('✅ Módulos marketplace importados')

    # Verificar funciones clave
    if hasattr(client_panel, 'show_selected_project_panel'):
        print('✅ show_selected_project_panel disponible')
    else:
        print('❌ show_selected_project_panel NO encontrado')

    if hasattr(marketplace_module, 'render_client_panel'):
        print('✅ render_client_panel disponible')
    else:
        print('❌ render_client_panel NO encontrado')

    # Verificar render_home (puede no existir, es opcional)
    if hasattr(marketplace_module, 'render_home'):
        print('✅ render_home disponible')
    else:
        print('⚠️  render_home NO encontrado (puede ser opcional)')

except Exception as e:
    print(f'❌ Error en módulos marketplace: {e}')

print('✅ AUDITORÍA DE NAVEGACIÓN COMPLETADA')