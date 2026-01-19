import sqlite3

conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print('Buscando columna ocr_text en todas las tablas:')
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            if 'ocr' in col[1].lower():
                print(f'✅ Encontrada columna OCR en tabla {table_name}: {col[1]}')
    except:
        pass

# Verificar específicamente la tabla proyectos (con s)
print('\nVerificando tabla proyectos:')
try:
    cursor.execute("PRAGMA table_info(proyectos)")
    columns = cursor.fetchall()
    print('Columnas en proyectos:')
    for col in columns:
        print(f'- {col[1]} ({col[2]})')
        if 'ocr' in col[1].lower():
            print(f'  ✅ Columna OCR encontrada: {col[1]}')

    # Buscar proyecto TEST FINAL PLANOS
    cursor.execute("SELECT id, nombre, ocr_text FROM proyectos WHERE nombre LIKE ?", ('%TEST FINAL PLANOS%',))
    project = cursor.fetchone()
    if project:
        project_id, nombre, ocr_text = project
        print(f'\n✅ Proyecto encontrado en proyectos: {nombre}')
        print(f'ID: {project_id}')
        has_ocr = 'Sí' if ocr_text else 'No'
        print(f'OCR disponible: {has_ocr}')
        if ocr_text:
            print(f'Longitud OCR: {len(ocr_text)} caracteres')
            print(f'Primeros 200 caracteres: {ocr_text[:200]}...')
    else:
        print('\n❌ Proyecto TEST FINAL PLANOS no encontrado en proyectos')
        # Mostrar algunos proyectos
        cursor.execute("SELECT id, nombre FROM proyectos LIMIT 5")
        projects = cursor.fetchall()
        print(f'Proyectos disponibles en proyectos ({len(projects)}):')
        for proj in projects:
            print(f'- ID: {proj[0]}, Nombre: {proj[1]}')

except Exception as e:
    print(f'Error con tabla proyectos: {e}')

conn.close()