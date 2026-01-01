import os
import sqlite3
import uuid
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

class ArchitectManager:
    def __init__(self, db_path, uploads_path):
        self.db_path = db_path
        self.uploads_path = uploads_path
        self._ensure_schema()
        
    def _ensure_schema(self):
        """Asegurar que existe el esquema necesario"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabla arquitectos
        c.execute('''
            CREATE TABLE IF NOT EXISTS architects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                company TEXT,
                nif TEXT,
                created_at TEXT
            )
        ''')
        
        # Tabla suscripciones
        c.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id TEXT PRIMARY KEY,
                architect_id TEXT NOT NULL,
                plan_name TEXT NOT NULL,
                plan_limit INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at TEXT,
                FOREIGN KEY (architect_id) REFERENCES architects(id)
            )
        ''')
        
        # Añadir architect_id a projects si no existe
        c.execute("PRAGMA table_info(projects)")
        cols = [r[1] for r in c.fetchall()]
        if "architect_id" not in cols:
            try:
                c.execute("ALTER TABLE projects ADD COLUMN architect_id TEXT REFERENCES architects(id)")
            except:
                pass
                
        conn.commit()
        conn.close()

    def validate_email(self, email):
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        import re
        pattern = r'^\+?\d{9,15}$'
        return re.match(pattern, phone) if phone else True

    def register_architect(self, data):
        """Registrar nuevo arquitecto"""
        if not self.validate_email(data['email']):
            return False, "Email inválido"
        if data.get('phone') and not self.validate_phone(data['phone']):
            return False, "Teléfono inválido"
            
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            arch_id = uuid.uuid4().hex
            c.execute('''
                INSERT INTO architects (id, name, email, phone, company, nif, created_at)
                VALUES (?,?,?,?,?,?,?)
            ''', (
                arch_id,
                data['name'],
                data['email'],
                data.get('phone',''),
                data.get('company',''),
                data.get('nif',''),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True, arch_id
        except sqlite3.IntegrityError:
            return False, "Email ya registrado"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_architect(self, email=None, architect_id=None):
        """Obtener arquitecto por email o ID"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM architects WHERE email = ?" if email else "SELECT * FROM architects WHERE id = ?"
        param = email if email else architect_id
        df = pd.read_sql_query(query, conn, params=(param,))
        conn.close()
        return df.iloc[0].to_dict() if df.shape[0] > 0 else None

    def create_subscription(self, architect_id, plan_name, plan_limit, price):
        """Crear nueva suscripción"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            sub_id = uuid.uuid4().hex
            c.execute('''
                INSERT INTO subscriptions (id, architect_id, plan_name, plan_limit, price, created_at)
                VALUES (?,?,?,?,?,?)
            ''', (
                sub_id,
                architect_id,
                plan_name,
                plan_limit,
                price,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True, sub_id
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_subscription(self, architect_id):
        """Obtener suscripción actual del arquitecto"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM subscriptions WHERE architect_id = ? ORDER BY created_at DESC LIMIT 1",
            conn, params=(architect_id,)
        )
        conn.close()
        return df.iloc[0].to_dict() if df.shape[0] > 0 else None

    def count_projects(self, architect_id):
        """Contar proyectos del arquitecto"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM projects WHERE architect_id = ?", (architect_id,))
        count = c.fetchone()[0]
        conn.close()
        return count

    def organize_project_files(self, project_id, files):
        """Organizar archivos del proyecto por tipo"""
        project_dir = os.path.join(self.uploads_path, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        file_structure = {
            'documentacion': ['pdf'],
            'planos': ['dwg', 'rvt'],
            'imagenes': ['png', 'jpg', 'jpeg'],
            'otros': ['zip', 'ifc']
        }
        
        saved_paths = []
        for file in files:
            ext = file.name.lower().rsplit('.', 1)[1]
            for folder, exts in file_structure.items():
                if ext in exts:
                    folder_path = os.path.join(project_dir, folder)
                    os.makedirs(folder_path, exist_ok=True)
                    file_path = os.path.join(folder_path, file.name)
                    with open(file_path, 'wb') as f:
                        f.write(file.getbuffer())
                    saved_paths.append(file_path)
                    break
        
        return saved_paths