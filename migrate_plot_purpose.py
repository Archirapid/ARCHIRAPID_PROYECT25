#!/usr/bin/env python3
"""
Migration: Add plot_purpose to plots table
Adds: plot_purpose column to track if owner wants to sell or build
"""

import sqlite3
import shutil
from datetime import datetime

def migrate():
    # Backup first
    backup_name = f"data.db.backup_plot_purpose_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2('data.db', backup_name)
    print(f"✅ Backup creado: {backup_name}")
    
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    try:
        # Check if column already exists
        columns = [row[1] for row in c.execute('PRAGMA table_info(plots)')]
        
        if 'plot_purpose' not in columns:
            print("📝 Agregando columna plot_purpose a plots...")
            c.execute('''
                ALTER TABLE plots 
                ADD COLUMN plot_purpose TEXT DEFAULT 'vender'
            ''')
            conn.commit()
            print("✅ Columna plot_purpose agregada")
        else:
            print("ℹ️ Columna plot_purpose ya existe")
        
        # Verify
        result = c.execute('PRAGMA table_info(plots)').fetchall()
        print("\n📋 Esquema actualizado de plots:")
        for row in result:
            print(f"  {row[1]} ({row[2]})")
        
        conn.commit()
        print("\n✅ Migración completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en migración: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
