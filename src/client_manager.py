"""
ARCHIRAPID - Client Manager
Gestión de clientes/compradores
"""
import os
import sqlite3
import uuid
from datetime import datetime
import pandas as pd

class ClientManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_schema()
        
    def _ensure_schema(self):
        """Crear tabla clients si no existe"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                preferences TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_client(self, data):
        """
        Registrar nuevo cliente
        
        Args:
            data: dict con name, email, phone (opcional), address (opcional)
            
        Returns:
            (success: bool, result: str)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Verificar si email ya existe
            c.execute("SELECT id FROM clients WHERE email = ?", (data['email'],))
            if c.fetchone():
                conn.close()
                return False, "Email ya registrado"
            
            client_id = uuid.uuid4().hex
            c.execute('''
                INSERT INTO clients (id, name, email, phone, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                client_id,
                data['name'],
                data['email'],
                data.get('phone', ''),
                data.get('address', ''),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True, client_id
            
        except Exception as e:
            return False, str(e)
    
    def get_client(self, client_id=None, email=None):
        """
        Obtener datos de un cliente
        
        Args:
            client_id: ID del cliente
            email: Email del cliente (alternativo)
            
        Returns:
            dict con datos del cliente o None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if client_id:
                c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            elif email:
                c.execute("SELECT * FROM clients WHERE email = ?", (email,))
            else:
                conn.close()
                return None
            
            row = c.fetchone()
            conn.close()
            
            if row:
                cols = ['id', 'name', 'email', 'phone', 'address', 'preferences', 'created_at']
                return dict(zip(cols, row))
            return None
            
        except Exception:
            return None
    
    def get_all_clients(self):
        """Obtener todos los clientes"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM clients ORDER BY created_at DESC", conn)
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()
    
    def update_preferences(self, client_id, preferences):
        """
        Actualizar preferencias del cliente
        
        Args:
            client_id: ID del cliente
            preferences: str con preferencias (JSON string)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("UPDATE clients SET preferences = ? WHERE id = ?", (preferences, client_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
