"""
ARCHIRAPID - Migration Script
Sprint 1.5: Extend projects table with portfolio fields
Date: 2024-11-14
"""
import sqlite3
import shutil
from datetime import datetime

DB_PATH = "data.db"

def backup_database():
    """Crear backup antes de migrar"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data.db.backup_sprint15_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def check_columns_exist(cursor, table_name, columns):
    """Verifica si columnas ya existen en la tabla"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = [row[1] for row in cursor.fetchall()]
    return all(col in existing_cols for col in columns)

def migrate():
    """Ejecutar migración"""
    print("\n🚀 INICIANDO MIGRACIÓN SPRINT 1.5: PORTFOLIO DE PROYECTOS\n")
    
    # Backup
    backup_database()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if already migrated
    new_columns = ['m2_construidos', 'm2_parcela_minima', 'm2_parcela_maxima', 'habitaciones', 
                   'banos', 'garaje', 'plantas', 'certificacion_energetica', 'tipo_proyecto',
                   'foto_principal', 'galeria_fotos', 'modelo_3d_glb', 'render_vr',
                   'planos_pdf', 'planos_dwg', 'memoria_pdf', 'presupuesto_pdf', 'gemelo_digital_ifc']
    
    if check_columns_exist(cursor, 'projects', new_columns):
        print("⚠️ Las columnas ya existen. Migración no necesaria.")
        conn.close()
        return
    
    print("📋 Extendiendo tabla projects con nuevos campos...")
    
    # Create new table with extended schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects_new (
            id TEXT PRIMARY KEY,
            title TEXT,
            architect_name TEXT,
            architect_id TEXT,
            area_m2 INTEGER,
            max_height REAL,
            style TEXT,
            price REAL,
            file_path TEXT,
            description TEXT,
            created_at TEXT,
            -- NEW FIELDS FOR MATCHING & TECHNICAL SPECS
            m2_construidos INTEGER,
            m2_parcela_minima INTEGER,
            m2_parcela_maxima INTEGER,
            habitaciones INTEGER,
            banos INTEGER,
            garaje INTEGER,
            plantas INTEGER,
            certificacion_energetica TEXT,
            tipo_proyecto TEXT,
            -- MEDIA FILES (JSON arrays for multiple files)
            foto_principal TEXT,
            galeria_fotos TEXT,
            modelo_3d_glb TEXT,
            render_vr TEXT,
            planos_pdf TEXT,
            planos_dwg TEXT,
            memoria_pdf TEXT,
            presupuesto_pdf TEXT,
            gemelo_digital_ifc TEXT
        )
    ''')
    
    # Copy existing data
    cursor.execute('''
        INSERT INTO projects_new 
        (id, title, architect_name, architect_id, area_m2, max_height, style, price, 
         file_path, description, created_at)
        SELECT id, title, architect_name, architect_id, area_m2, max_height, style, price,
               file_path, description, created_at
        FROM projects
    ''')
    
    migrated = cursor.rowcount
    
    # Drop old table and rename new
    cursor.execute("DROP TABLE IF EXISTS projects")
    cursor.execute("ALTER TABLE projects_new RENAME TO projects")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Migrados {migrated} proyecto(s)")
    print("\n📊 ESTADO DE LA BD:")
    
    # Show stats
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM architects")
    arch_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM plots")
    plots_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM projects")
    projects_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
    active_subs = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   - Arquitectos: {arch_count}")
    print(f"   - Fincas: {plots_count}")
    print(f"   - Proyectos: {projects_count}")
    print(f"   - Suscripciones activas: {active_subs}")
    
    print("\n✅ MIGRACIÓN COMPLETADA CON ÉXITO")
    print("🎯 Ahora puedes:")
    print("   1. Ejecutar app.py")
    print("   2. Ir a Arquitectos → Mis Proyectos")
    print("   3. Subir proyectos con fotos, 3D, planos DWG/PDF")
    print("   4. Ver matching automático en preview de fincas\n")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
