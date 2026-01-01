"""
ARCHIRAPID - Contractor Manager
Gestión de constructores y proveedores de servicios
"""
import os
import sqlite3
import uuid
from datetime import datetime
import pandas as pd

class ContractorManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_schema()
        
    def _ensure_schema(self):
        """Crear tabla contractors si no existe"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS contractors (
                id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                cif TEXT,
                category TEXT NOT NULL,
                specialty TEXT,
                zone TEXT,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_contractor(self, data):
        """
        Registrar nuevo constructor/proveedor
        
        Args:
            data: dict con company_name, contact_name, email, category, etc.
            
        Returns:
            (success: bool, result: str)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Verificar si email ya existe
            c.execute("SELECT id FROM contractors WHERE email = ?", (data['email'],))
            if c.fetchone():
                conn.close()
                return False, "Email ya registrado"
            
            contractor_id = uuid.uuid4().hex
            c.execute('''
                INSERT INTO contractors (
                    id, company_name, contact_name, email, phone, cif, 
                    category, specialty, zone, description, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contractor_id,
                data['company_name'],
                data['contact_name'],
                data['email'],
                data.get('phone', ''),
                data.get('cif', ''),
                data['category'],
                data.get('specialty', ''),
                data.get('zone', ''),
                data.get('description', ''),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True, contractor_id
            
        except Exception as e:
            return False, str(e)
    
    def get_contractor(self, contractor_id=None, email=None):
        """
        Obtener datos de un contractor
        
        Args:
            contractor_id: ID del contractor
            email: Email del contractor (alternativo)
            
        Returns:
            dict con datos o None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if contractor_id:
                c.execute("SELECT * FROM contractors WHERE id = ?", (contractor_id,))
            elif email:
                c.execute("SELECT * FROM contractors WHERE email = ?", (email,))
            else:
                conn.close()
                return None
            
            row = c.fetchone()
            conn.close()
            
            if row:
                cols = ['id', 'company_name', 'contact_name', 'email', 'phone', 'cif',
                       'category', 'specialty', 'zone', 'description', 'created_at']
                return dict(zip(cols, row))
            return None
            
        except Exception:
            return None
    
    def get_all_contractors(self, category=None):
        """
        Obtener todos los contractors, opcionalmente filtrados por categoría
        
        Args:
            category: Filtrar por categoría (opcional)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if category:
                query = "SELECT * FROM contractors WHERE category = ? ORDER BY created_at DESC"
                df = pd.read_sql_query(query, conn, params=(category,))
            else:
                query = "SELECT * FROM contractors ORDER BY created_at DESC"
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()
    
    def get_categories(self):
        """Obtener lista de categorías únicas"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT DISTINCT category FROM contractors WHERE category IS NOT NULL")
            categories = [row[0] for row in c.fetchall()]
            conn.close()
            return categories
        except Exception:
            return []
