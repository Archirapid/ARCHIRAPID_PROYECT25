import os
import sqlite3
import uuid
from datetime import datetime
import json
import pandas as pd
from PIL import Image
import io

class PropertyManager:
    def __init__(self, db_path, uploads_path):
        self.db_path = db_path
        self.uploads_path = uploads_path
        self._ensure_schema()
        
    def _ensure_schema(self):
        """Asegurar que existe el esquema necesario"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabla de propiedades/fincas
        c.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                m2 INTEGER NOT NULL,
                height REAL,
                price REAL NOT NULL,
                type TEXT NOT NULL,
                province TEXT NOT NULL,
                locality TEXT,
                owner_name TEXT,
                owner_email TEXT,
                image_paths TEXT,
                registry_note_path TEXT,
                created_at TEXT
            )
        ''')
                
        conn.commit()
        conn.close()

    def validate_coordinates(self, lat, lon):
        try:
            lat = float(lat)
            lon = float(lon)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except:
            return False

    def validate_email(self, email):
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) if email else True

    def process_images(self, image_files):
        """Procesa y guarda las imágenes subidas"""
        saved_paths = []
        for img_file in image_files:
            try:
                # Abrir imagen con Pillow
                img = Image.open(img_file)
                
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande
                max_size = (1920, 1080)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)
                
                # Generar nombre único
                ext = os.path.splitext(img_file.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png']:
                    ext = '.jpg'
                filename = f"property_{uuid.uuid4().hex}{ext}"
                filepath = os.path.join(self.uploads_path, filename)
                
                # Guardar imagen optimizada
                img.save(filepath, quality=85, optimize=True)
                saved_paths.append(filepath)
                
            except Exception as e:
                print(f"Error procesando imagen {img_file.name}: {str(e)}")
                continue
                
        return saved_paths

    def register_property(self, data, image_files=None):
        """Registrar nueva propiedad"""
        if not self.validate_coordinates(data.get('lat'), data.get('lon')):
            return False, "Coordenadas inválidas"
            
        if data.get('owner_email') and not self.validate_email(data['owner_email']):
            return False, "Email inválido"
            
        try:
            # Procesar imágenes si hay
            image_paths = []
            if image_files:
                image_paths = self.process_images(image_files)
                if not image_paths:
                    return False, "Error procesando las imágenes"
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            property_id = uuid.uuid4().hex
            
            # Convertir lista de rutas a JSON
            image_paths_json = json.dumps(image_paths) if image_paths else None
            
            c.execute('''
                INSERT INTO properties (
                    id, title, description, lat, lon, m2, height, price,
                    type, province, locality, owner_name, owner_email,
                    image_paths, registry_note_path, created_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                property_id,
                data['title'],
                data.get('description', ''),
                float(data['lat']),
                float(data['lon']),
                int(data['m2']),
                float(data.get('height', 0)),
                float(data['price']),
                data['type'],
                data['province'],
                data.get('locality', ''),
                data.get('owner_name', ''),
                data.get('owner_email', ''),
                image_paths_json,
                data.get('registry_note_path'),
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True, property_id
            
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_property(self, property_id):
        """Obtener propiedad por ID"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT * FROM properties WHERE id = ?",
            conn,
            params=(property_id,)
        )
        conn.close()
        
        if df.shape[0] == 0:
            return None
            
        # Convertir JSON de imágenes a lista
        property_data = df.iloc[0].to_dict()
        if property_data.get('image_paths'):
            try:
                property_data['image_paths'] = json.loads(property_data['image_paths'])
            except:
                property_data['image_paths'] = []
                
        return property_data

    def get_all_properties(self):
        """Obtener todas las propiedades"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM properties", conn)
        conn.close()
        
        # Convertir JSON de imágenes a lista para cada fila
        for idx, row in df.iterrows():
            if row.get('image_paths'):
                try:
                    df.at[idx, 'image_paths'] = json.loads(row['image_paths'])
                except:
                    df.at[idx, 'image_paths'] = []
                    
        return df