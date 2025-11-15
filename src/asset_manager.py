"""
Asset Manager para ArchiRapid
Gestiona la verificación y manipulación de recursos visuales del sistema.
"""
import os
import json
import shutil
from pathlib import Path
from PIL import Image
from typing import List, Dict, Optional
import streamlit as st
import uuid
from datetime import datetime

def show_project_form():
    """Muestra formulario para subir un proyecto arquitectónico"""
    st.title("Subir Proyecto Arquitectónico")
    
    with st.form("project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Título del proyecto")
            architect_name = st.text_input("Nombre del arquitecto")
            description = st.text_area("Descripción del proyecto")
            area_m2 = st.number_input("Área del proyecto (m²)", min_value=1)
            max_height = st.number_input("Altura máxima (metros)", min_value=1.0)
            
        with col2:
            style = st.selectbox("Estilo arquitectónico", 
                               ["Moderno", "Contemporáneo", "Minimalista", 
                                "Mediterráneo", "Tradicional", "Industrial"])
            price = st.number_input("Precio del proyecto (€)", min_value=0.0)
            project_file = st.file_uploader("Archivo del proyecto (PDF)", type=['pdf'])
        
        submitted = st.form_submit_button("Subir Proyecto")
        
        if submitted:
            try:
                # Validar datos obligatorios
                if not all([title, architect_name, description, area_m2, max_height, 
                           style, price, project_file]):
                    st.error("Por favor completa todos los campos obligatorios")
                    return
                    
                # Guardar archivo
                file_path = save_file(project_file, "project")
                
                # Crear registro
                project_data = {
                    'id': uuid.uuid4().hex,
                    'title': title,
                    'architect_name': architect_name,
                    'area_m2': int(area_m2),
                    'max_height': float(max_height),
                    'style': style,
                    'price': float(price),
                    'file_path': file_path,
                    'description': description,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                # Insertar en DB
                insert_project(project_data)
                
                st.success("¡Proyecto subido exitosamente!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error al subir el proyecto: {str(e)}")

def show_projects():
    """Muestra el listado de proyectos arquitectónicos"""
    st.title("Proyectos Arquitectónicos")
    
    # Obtener datos
    df = get_all_projects()
    if df.shape[0] == 0:
        st.warning("No hay proyectos registrados")
        return
        
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        min_area = st.number_input("Área mínima (m²)", min_value=0)
        max_area = st.number_input("Área máxima (m²)", min_value=0)
    with col2:    
        selected_styles = st.multiselect("Estilos", 
                                       ["Moderno", "Contemporáneo", "Minimalista",
                                        "Mediterráneo", "Tradicional", "Industrial"])
        
    # Aplicar filtros
    filtered_df = df.copy()
    if min_area > 0:
        filtered_df = filtered_df[filtered_df['area_m2'] >= min_area]
    if max_area > 0:
        filtered_df = filtered_df[filtered_df['area_m2'] <= max_area]
    if selected_styles:
        filtered_df = filtered_df[filtered_df['style'].isin(selected_styles)]
        
    # Mostrar proyectos filtrados
    st.subheader(f"Mostrando {filtered_df.shape[0]} proyectos")
    
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="plot-card">
                <h3>{row['title']}</h3>
                <p><b>Arquitecto:</b> {row['architect_name']}</p>
                <p><b>Área:</b> {row['area_m2']}m² | <b>Altura máxima:</b> {row['max_height']}m</p>
                <p><b>Estilo:</b> {row['style']}</p>
                <p><b>Precio:</b> {row['price']}€</p>
                <p>{row['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if row['file_path']:
                st.download_button(
                    "Descargar PDF",
                    open(row['file_path'], 'rb'),
                    file_name=f"proyecto_{row['id']}.pdf",
                    mime="application/pdf"
                )

class AssetManager:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.assets_path = self.root_path / 'assets'
        self.fincas_path = self.assets_path / 'fincas'
        self.projects_path = self.assets_path / 'projects'
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Asegura que existan todos los directorios necesarios."""
        self.fincas_path.mkdir(parents=True, exist_ok=True)
        self.projects_path.mkdir(parents=True, exist_ok=True)

    def verify_image(self, image_path: Path) -> bool:
        """Verifica si una imagen es válida y utilizable."""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def validate_json_paths(self) -> Dict[str, List[str]]:
        """Valida que todas las rutas en los archivos JSON existan."""
        issues = {'fincas': [], 'projects': []}
        
        # Validar projects.json
        with open(self.root_path / 'projects.json', 'r', encoding='utf-8') as f:
            projects = json.load(f)
            for project in projects:
                image_path = self.root_path / project['image']
                if not image_path.exists():
                    issues['projects'].append(f"Imagen no encontrada: {project['image']}")

        # Validar fincas.json
        with open(self.root_path / 'fincas.json', 'r', encoding='utf-8') as f:
            fincas = json.load(f)
            for finca in fincas:
                for image in finca['images']:
                    image_path = self.root_path / image
                    if not image_path.exists():
                        issues['fincas'].append(f"Imagen no encontrada: {image}")

        return issues

    def create_placeholder_image(self, path: Path, text: str) -> None:
        """Crea una imagen de marcador de posición con texto."""
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        
        # Crear objeto para dibujar
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            # Intentar usar una fuente del sistema
            font_size = 40
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Si no se encuentra la fuente, usar la predeterminada
            font = ImageFont.load_default()
        
        # Calcular la posición del texto para centrarlo
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Dibujar un rectángulo de fondo
        padding = 20
        draw.rectangle(
            [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
            fill='#ffffff',
            outline='#cccccc',
            width=2
        )
        
        # Dibujar el texto
        draw.text((x, y), text, font=font, fill='#333333')
        
        # Asegurar que el directorio existe
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar la imagen
        img.save(path)

    def generate_placeholders(self) -> None:
        """Genera imágenes de marcador de posición para todos los assets faltantes."""
        # Generar para proyectos
        for i in range(1, 4):
            path = self.projects_path / f"project{i}.png"
            if not path.exists():
                self.create_placeholder_image(path, f"Proyecto {i}")

        # Generar para fincas
        for i in range(1, 4):
            for j in range(1, 3):
                path = self.fincas_path / f"finca{i}_{j}.png"
                if not path.exists():
                    self.create_placeholder_image(path, f"Finca {i} - Vista {j}")

    def migrate_legacy_images(self) -> None:
        """Migra imágenes antiguas a la nueva estructura de directorios."""
        old_images = list(self.assets_path.glob('project*.png'))
        for old_image in old_images:
            if old_image.stem.startswith('project'):
                shutil.move(str(old_image), str(self.projects_path / old_image.name))

    def get_status_report(self) -> Dict:
        """Genera un reporte del estado actual de los assets."""
        return {
            'directories': {
                'fincas': self.fincas_path.exists(),
                'projects': self.projects_path.exists()
            },
            'images': {
                'fincas': len(list(self.fincas_path.glob('*.png'))),
                'projects': len(list(self.projects_path.glob('*.png')))
            },
            'issues': self.validate_json_paths()
        }

# =====================================================
# STUBS / IMPLEMENTACIONES MÍNIMAS PARA EVITAR ERRORES DE COMPILACIÓN
# Estas funciones se usan en formularios pero no estaban definidas.
# Se provee una versión mínima para integridad del sistema.
# =====================================================
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / 'data.db')
ASSETS_DIR = BASE_DIR / 'assets'
PROJECTS_DIR = ASSETS_DIR / 'projects'
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def save_file(uploaded_file, kind: str) -> Optional[str]:
    """Guarda archivo subido y devuelve la ruta. Si falla devuelve None."""
    if not uploaded_file:
        return None
    suffix = Path(uploaded_file.name).suffix
    target = PROJECTS_DIR / f"{uuid.uuid4().hex}{suffix}"
    try:
        with open(target, 'wb') as f:
            f.write(uploaded_file.read())
        return str(target)
    except Exception:
        return None

def _ensure_projects_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT,
            architect_name TEXT,
            area_m2 INTEGER,
            max_height REAL,
            style TEXT,
            price REAL,
            file_path TEXT,
            description TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_project(project_data: Dict) -> None:
    _ensure_projects_table()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO projects
        (id,title,architect_name,area_m2,max_height,style,price,file_path,description,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        project_data.get('id'),
        project_data.get('title'),
        project_data.get('architect_name'),
        project_data.get('area_m2'),
        project_data.get('max_height'),
        project_data.get('style'),
        project_data.get('price'),
        project_data.get('file_path'),
        project_data.get('description'),
        project_data.get('created_at'),
    ))
    conn.commit()
    conn.close()

def get_all_projects() -> pd.DataFrame:
    _ensure_projects_table()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM projects", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id","title","architect_name","area_m2","max_height","style","price","file_path","description","created_at"])
