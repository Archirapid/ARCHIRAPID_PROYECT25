import sqlite3

# Verificar ambas bases de datos
for db_name in ['data.db', 'archirapid.db']:
    print(f"\n{'='*50}")
    print(f"VERIFICANDO: {db_name}")
    print('='*50)
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Ver tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"\nTablas: {tables}")
        
        if 'projects' in tables:
            print(f"\n=== ÚLTIMOS 5 PROYECTOS EN {db_name} ===\n")
            cursor.execute("SELECT title, architect_id, architect_name FROM projects ORDER BY created_at DESC LIMIT 5")
            for i, row in enumerate(cursor.fetchall(), 1):
                print(f"{i}. {row[0]}")
                print(f"   architect_id: [{row[1]}]")
                print(f"   architect_name: {row[2]}\n")
            
            print(f"\n=== PROYECTOS DE RAUL ===")
            cursor.execute("SELECT COUNT(*) FROM projects WHERE architect_id = 'e0e43fa3-5cc3-4ef9-a88c-bd6ebf094ac1'")
            count = cursor.fetchone()[0]
            print(f"Total con architect_id correcto: {count}")
            
            cursor.execute("SELECT COUNT(*) FROM projects WHERE architect_name = 'Raul villar'")
            count_name = cursor.fetchone()[0]
            print(f"Total con architect_name 'Raul villar': {count_name}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

