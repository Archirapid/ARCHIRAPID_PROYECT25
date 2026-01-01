import sys
sys.path.append('.')
try:
    from modules.marketplace.owners import obtener_coordenadas_gps
    from src import db
    from datetime import datetime

    print('✅ Módulos importados correctamente')

    # Simular datos extraídos por Gemini
    data_extracted = {
        'referencia_catastral': '1234567ABC1234',
        'superficie_grafica_m2': 1500,
        'municipio': 'Getafe'
    }

    pdf_path = 'test_path.pdf'

    # Preparar datos para insertar (sin depender de st.session_state)
    plot_data = {
        'id': data_extracted.get('referencia_catastral'),
        'catastral_ref': data_extracted.get('referencia_catastral'),
        'm2': data_extracted.get('superficie_grafica_m2'),
        'locality': data_extracted.get('municipio'),
        'province': 'Madrid',
        'plano_catastral_path': pdf_path,
        'type': 'plot',
        'status': 'draft',
        'created_at': datetime.utcnow().isoformat(),
        'title': f'Parcela {data_extracted.get("referencia_catastral")}',
        'description': f'Parcela catastral {data_extracted.get("referencia_catastral")} - {data_extracted.get("municipio", "Sin municipio")}',
        'price': 0,
        'height': None,
        'owner_name': 'Test Owner',
        'owner_email': 'test@example.com',
        'owner_phone': '123456789',
        'image_path': None,
        'registry_note_path': pdf_path,
        'address': f'{data_extracted.get("municipio", "Madrid")}, Madrid',
        'photo_paths': '[]',
        'services': '',
    }

    # Obtener coordenadas GPS
    municipio = data_extracted.get('municipio', '')
    if municipio:
        lat, lon = obtener_coordenadas_gps(municipio, 'Madrid')
        plot_data['lat'] = lat
        plot_data['lon'] = lon
        print(f'📍 Coordenadas GPS obtenidas: {lat:.4f}, {lon:.4f}')
    else:
        plot_data['lat'] = 40.4168
        plot_data['lon'] = -3.7038
        print('⚠️ Usando coordenadas por defecto de Madrid')

    # Insertar en la base de datos
    db.insert_plot(plot_data)
    print('✅ Datos guardados correctamente en BD')

    # Verificar que se guardó
    plots = db.get_all_plots()
    if not plots.empty:
        last_plot = plots.iloc[-1]
        print(f'📊 Última parcela guardada: {last_plot["title"]} - Coords: {last_plot["lat"]:.4f}, {last_plot["lon"]:.4f}')

    print('✅ Prueba completa exitosa')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()