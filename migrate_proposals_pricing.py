"""
Migración: Añadir campos de pricing detallado a tabla proposals
- delivery_format (PDF/AutoCAD)
- delivery_price (1200/1800)
- supervision_fee
- visa_fee
- total_cliente
- commission
"""

import sqlite3
import shutil
from datetime import datetime

DB_PATH = 'data.db'

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'data.db.backup_pricing_{timestamp}'
    shutil.copy(DB_PATH, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def migrate():
    print("🔄 INICIANDO MIGRACIÓN: Campos pricing en proposals...")
    
    # Crear backup
    backup_file = backup_database()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Verificar si las columnas ya existen
    c.execute("PRAGMA table_info(proposals)")
    existing_columns = [col[1] for col in c.fetchall()]
    
    new_columns = {
        'delivery_format': 'TEXT DEFAULT "PDF"',
        'delivery_price': 'REAL DEFAULT 1200',
        'supervision_fee': 'REAL DEFAULT 0',
        'visa_fee': 'REAL DEFAULT 0',
        'total_cliente': 'REAL DEFAULT 0',
        'commission': 'REAL DEFAULT 0'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in existing_columns:
            print(f"  ➕ Añadiendo columna: {col_name}")
            c.execute(f'ALTER TABLE proposals ADD COLUMN {col_name} {col_type}')
        else:
            print(f"  ⏭️ Columna {col_name} ya existe")
    
    conn.commit()
    
    # Verificar propuestas existentes y actualizar campos
    c.execute("SELECT id, estimated_budget FROM proposals")
    proposals = c.fetchall()
    
    print(f"\n📊 Actualizando {len(proposals)} propuesta(s) existente(s)...")
    
    for prop_id, budget in proposals:
        # Asignar valores por defecto razonables
        delivery_price = 1200  # PDF por defecto
        commission = budget * 0.12  # 12% comisión básica
        total = budget + delivery_price + commission
        
        c.execute("""
            UPDATE proposals 
            SET delivery_format = ?, delivery_price = ?, total_cliente = ?, commission = ?
            WHERE id = ?
        """, ("PDF Básico", delivery_price, total, commission, prop_id))
    
    conn.commit()
    
    # Verificar resultado
    c.execute("SELECT COUNT(*) FROM proposals")
    total_proposals = c.fetchone()[0]
    
    c.execute("PRAGMA table_info(proposals)")
    final_columns = [col[1] for col in c.fetchall()]
    
    conn.close()
    
    print(f"\n✅ MIGRACIÓN COMPLETADA CON ÉXITO")
    print(f"   - Backup: {backup_file}")
    print(f"   - Propuestas actualizadas: {len(proposals)}")
    print(f"   - Total columnas en proposals: {len(final_columns)}")
    print(f"   - Nuevas columnas: {', '.join(new_columns.keys())}")

if __name__ == "__main__":
    migrate()
