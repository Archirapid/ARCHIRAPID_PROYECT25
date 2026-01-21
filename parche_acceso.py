#!/usr/bin/env python3
"""
Script temporal para parche de acceso inmediato
Actualiza usuario raul@arquitecto2026.com a profesional
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import db

def parche_acceso_inmediato():
    """Actualiza el usuario raul@arquitecto2026.com a profesional"""
    email = "raul@arquitecto2026.com"

    conn = db.get_conn()
    try:
        cur = conn.cursor()

        # Verificar si existe el usuario
        cur.execute("SELECT id, email, full_name FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        row = cur.fetchone()

        if not row:
            print(f"❌ Usuario {email} no encontrado. Creando usuario profesional...")
            # Crear usuario
            from werkzeug.security import generate_password_hash
            import uuid
            from datetime import datetime

            user_id = str(uuid.uuid4())
            hashed_password = generate_password_hash("123456")
            cur.execute("""
                INSERT INTO users (id, email, full_name, role, is_professional, password_hash, created_at)
                VALUES (?, ?, ?, 'architect', 1, ?, ?)
            """, (user_id, email, "Raúl Arquitecto", hashed_password, datetime.utcnow().isoformat()))
            conn.commit()
            print(f"✅ Usuario {email} creado como profesional")
            return

        user_id = row[0]
        print(f"✅ Usuario {email} encontrado (ID: {user_id}). Actualizando a profesional...")

        # Actualizar usuario existente
        cur.execute("""
            UPDATE users
            SET role = 'architect', is_professional = 1
            WHERE id = ?
        """, (user_id,))
        conn.commit()

        if cur.rowcount > 0:
            print(f"✅ Usuario {email} actualizado a profesional (role='architect', is_professional=True)")
        else:
            print(f"⚠️ No se actualizó ningún registro para {email}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    parche_acceso_inmediato()