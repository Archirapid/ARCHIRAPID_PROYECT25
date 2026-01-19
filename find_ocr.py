import sqlite3

conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print('Buscando columnas relacionadas con OCR en todas las tablas:')
found_ocr = False
for table in tables:
    table_name = table[0]
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        ocr_columns = []
        for col in columns:
            if 'ocr' in col[1].lower() or 'text' in col[1].lower():
                ocr_columns.append(col[1])
        if ocr_columns:
            print(f'✅ Tabla {table_name} tiene columnas relacionadas:')
            for col in ocr_columns:
                print(f'  - {col}')
            found_ocr = True

            # Mostrar algunos registros de esta tabla
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f'  Registros de muestra ({len(rows)}):')
                for i, row in enumerate(rows):
                    print(f'    {i+1}: {row[:3]}...' if len(row) > 3 else f'    {i+1}: {row}')
            except:
                print('  No se pudieron obtener registros de muestra')

    except Exception as e:
        print(f'Error con tabla {table_name}: {e}')

if not found_ocr:
    print('❌ No se encontraron columnas relacionadas con OCR en ninguna tabla')

conn.close()