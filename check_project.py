import sqlite3

conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()

# Verificar esquema de la tabla projects
cursor.execute("PRAGMA table_info(projects)")
columns = cursor.fetchall()
print('Columnas en tabla projects:')
for col in columns:
    print(f'- {col[1]} ({col[2]})')

print('\nBuscando proyecto TEST FINAL PLANOS...')
cursor.execute("SELECT id, title, ocr_text FROM projects WHERE title LIKE ?", ('%TEST FINAL PLANOS%',))
project = cursor.fetchone()

if project:
    project_id, title, ocr_text = project
    print(f'✅ Proyecto encontrado: {title}')
    print(f'ID: {project_id}')
    has_ocr = 'Sí' if ocr_text else 'No'
    print(f'OCR disponible: {has_ocr}')
    if ocr_text:
        print(f'Longitud OCR: {len(ocr_text)} caracteres')
        print(f'Primeros 200 caracteres: {ocr_text[:200]}...')
    else:
        print('No hay texto OCR disponible')
else:
    print('❌ Proyecto TEST FINAL PLANOS no encontrado')
    # Mostrar todos los proyectos disponibles
    cursor.execute("SELECT id, title FROM projects LIMIT 10")
    projects = cursor.fetchall()
    print(f'\nProyectos disponibles ({len(projects)}):')
    for proj in projects:
        print(f'- ID: {proj[0]}, Título: {proj[1]}')

conn.close()