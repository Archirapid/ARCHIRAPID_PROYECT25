"""
Migración Sprint 2: Agregar project_id a proposals y crear tabla commissions
Fecha: 2025-11-14
"""

import sqlite3
import os

DB_PATH = "data.db"

def migrate():
    print("🔄 Iniciando migración Sprint 2...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # 1. Agregar project_id a proposals
        print("📝 Agregando columna project_id a proposals...")
        c.execute("ALTER TABLE proposals ADD COLUMN project_id TEXT")
        print("✅ Columna project_id agregada")
        
        # 2. Crear tabla commissions
        print("📝 Creando tabla commissions...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS commissions (
                id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                architect_id TEXT NOT NULL,
                client_id TEXT,
                amount REAL NOT NULL,
                paid BOOLEAN DEFAULT 0,
                payment_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (proposal_id) REFERENCES proposals(id),
                FOREIGN KEY (architect_id) REFERENCES architects(id),
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        ''')
        print("✅ Tabla commissions creada")
        
        # 3. Crear tabla payments (para registrar pagos de clientes)
        print("📝 Creando tabla payments...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                proposal_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT,
                card_last4 TEXT,
                status TEXT DEFAULT 'completed',
                transaction_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (proposal_id) REFERENCES proposals(id),
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        ''')
        print("✅ Tabla payments creada")
        
        conn.commit()
        print("\n🎉 Migración Sprint 2 completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error en migración: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Backup antes de migrar
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data.db.backup_sprint2_migration_{timestamp}"
    
    print(f"💾 Creando backup: {backup_path}")
    shutil.copy(DB_PATH, backup_path)
    print(f"✅ Backup creado")
    
    migrate()
