"""
Migración de Base de Datos - ARCHIRAPID
Actualiza el esquema de BD existente con las nuevas columnas del SPRINT 1
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "data.db"

def migrate_database():
    """Aplica migraciones a la BD existente"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró {DB_PATH}")
        return False
    
    # Backup antes de migrar
    backup_path = f"data.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy(DB_PATH, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # =====================================================
        # MIGRACIÓN 1: Actualizar tabla subscriptions
        # =====================================================
        print("\n🔄 Migrando tabla 'subscriptions'...")
        
        # Verificar si ya tiene las nuevas columnas
        c.execute("PRAGMA table_info(subscriptions)")
        columns = [col[1] for col in c.fetchall()]
        
        needs_migration = False
        new_columns = ['plan_type', 'monthly_proposals_limit', 'commission_rate', 'status', 'start_date', 'end_date']
        
        for col in new_columns:
            if col not in columns:
                needs_migration = True
                break
        
        if needs_migration:
            print("  Creando tabla temporal con nuevo esquema...")
            
            # Crear tabla temporal con esquema nuevo
            c.execute('''
                CREATE TABLE subscriptions_new (
                    id TEXT PRIMARY KEY,
                    architect_id TEXT,
                    plan_type TEXT,
                    price REAL,
                    monthly_proposals_limit INTEGER,
                    commission_rate REAL,
                    status TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    created_at TEXT,
                    FOREIGN KEY (architect_id) REFERENCES architects(id)
                )
            ''')
            
            # Copiar datos existentes con mapeo
            print("  Migrando datos existentes...")
            c.execute("SELECT * FROM subscriptions")
            old_rows = c.fetchall()
            
            for row in old_rows:
                # row = (id, architect_id, plan_name, plan_limit, price, created_at)
                old_id = row[0]
                old_architect_id = row[1]
                old_plan_name = row[2] if len(row) > 2 else 'PRO'
                old_plan_limit = row[3] if len(row) > 3 else 10
                old_price = row[4] if len(row) > 4 else 79.0
                old_created_at = row[5] if len(row) > 5 else datetime.now().isoformat()
                
                # Mapear plan antiguo a nuevo
                plan_mapping = {
                    'BASIC': ('BÁSICO', 29, 3, 0.12),
                    'STANDARD': ('PRO', 79, 10, 0.10),
                    'PRO': ('PRO', 79, 10, 0.10),
                    'PREMIUM': ('PREMIUM', 149, 999, 0.08)
                }
                
                plan_type, price, limit, commission = plan_mapping.get(old_plan_name, ('PRO', 79, 10, 0.10))
                
                # Insertar en tabla nueva
                c.execute('''
                    INSERT INTO subscriptions_new 
                    (id, architect_id, plan_type, price, monthly_proposals_limit, commission_rate, status, start_date, end_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    old_id,
                    old_architect_id,
                    plan_type,
                    price,
                    limit,
                    commission,
                    'active',  # Por defecto activo
                    old_created_at[:10] if old_created_at else datetime.now().date().isoformat(),
                    None,  # Sin fecha fin
                    old_created_at
                ))
            
            # Eliminar tabla vieja y renombrar nueva
            c.execute("DROP TABLE subscriptions")
            c.execute("ALTER TABLE subscriptions_new RENAME TO subscriptions")
            
            print(f"  ✅ Migrados {len(old_rows)} suscripciones")
        else:
            print("  ✅ Tabla 'subscriptions' ya está actualizada")
        
        # =====================================================
        # MIGRACIÓN 2: Crear tabla proposals si no existe
        # =====================================================
        print("\n🔄 Verificando tabla 'proposals'...")
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='proposals'")
        if not c.fetchone():
            print("  Creando tabla 'proposals'...")
            c.execute('''
                CREATE TABLE proposals (
                    id TEXT PRIMARY KEY,
                    architect_id TEXT,
                    plot_id TEXT,
                    proposal_text TEXT,
                    estimated_budget REAL,
                    deadline_days INTEGER,
                    sketch_image_path TEXT,
                    status TEXT,
                    created_at TEXT,
                    responded_at TEXT,
                    FOREIGN KEY (architect_id) REFERENCES architects(id),
                    FOREIGN KEY (plot_id) REFERENCES plots(id)
                )
            ''')
            print("  ✅ Tabla 'proposals' creada")
        else:
            print("  ✅ Tabla 'proposals' ya existe")
        
        # =====================================================
        # MIGRACIÓN 3: Crear tabla clients si no existe
        # =====================================================
        print("\n🔄 Verificando tabla 'clients'...")
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if not c.fetchone():
            print("  Creando tabla 'clients'...")
            c.execute('''
                CREATE TABLE clients (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    nif TEXT,
                    created_at TEXT
                )
            ''')
            print("  ✅ Tabla 'clients' creada")
        else:
            print("  ✅ Tabla 'clients' ya existe")
        
        # =====================================================
        # MIGRACIÓN 4: Crear tabla contractors si no existe
        # =====================================================
        print("\n🔄 Verificando tabla 'contractors'...")
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contractors'")
        if not c.fetchone():
            print("  Creando tabla 'contractors'...")
            c.execute('''
                CREATE TABLE contractors (
                    id TEXT PRIMARY KEY,
                    company_name TEXT,
                    email TEXT UNIQUE,
                    phone TEXT,
                    cif TEXT,
                    specialty TEXT,
                    created_at TEXT
                )
            ''')
            print("  ✅ Tabla 'contractors' creada")
        else:
            print("  ✅ Tabla 'contractors' ya existe")
        
        conn.commit()
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
        print("="*60)
        
        # Estadísticas
        c.execute("SELECT COUNT(*) FROM architects")
        arch_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM subscriptions")
        sub_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM proposals")
        prop_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM plots")
        plot_count = c.fetchone()[0]
        
        print(f"\n📊 Estado de la BD:")
        print(f"  - Arquitectos: {arch_count}")
        print(f"  - Suscripciones: {sub_count}")
        print(f"  - Propuestas: {prop_count}")
        print(f"  - Fincas: {plot_count}")
        
        print(f"\n💾 Backup guardado en: {backup_path}")
        print("🚀 Puedes arrancar la app ahora")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante migración: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        
        # Restaurar backup
        print(f"\n🔄 Restaurando backup...")
        conn.close()
        shutil.copy(backup_path, DB_PATH)
        print("✅ Backup restaurado")
        
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("🔧 MIGRACIÓN DE BASE DE DATOS - ARCHIRAPID SPRINT 1")
    print("="*60)
    print("\nEsto actualizará el esquema de tu base de datos existente.")
    print("Se creará un backup automático antes de hacer cambios.\n")
    
    input("Presiona ENTER para continuar o Ctrl+C para cancelar...")
    
    success = migrate_database()
    
    if success:
        print("\n✅ Todo listo. Ejecuta: streamlit run app.py")
    else:
        print("\n❌ Migración fallida. Revisa los errores arriba.")
