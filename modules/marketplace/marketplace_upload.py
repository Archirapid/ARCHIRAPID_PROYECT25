# modules/marketplace/marketplace_upload.py
"""
Marketplace de proyectos para arquitectos - ARCHIRAPID MVP
Permite subir proyectos completos (3D, RV, memoria, planos) al catálogo
"""

import streamlit as st
import json
import os
from typing import Dict, List, Optional, Tuple
from .data_access import save_proyecto, get_usuario
from .documentacion import generar_memoria_constructiva, generar_presupuesto_estimado

# === CONFIGURACIÓN ===
UPLOAD_DIR = "uploads/proyectos_arquitectos"
ALLOWED_EXTENSIONS = {
    '3d': ['obj', 'fbx', 'gltf', 'glb', 'dae'],
    'rv': ['jpg', 'png', 'jpeg', 'mp4', 'webm'],
    'pdf': ['pdf'],
    'cad': ['dxf', 'dwg', 'svg'],
    'json': ['json']
}

os.makedirs(UPLOAD_DIR, exist_ok=True)

# === FUNCIONES PRINCIPALES ===
def upload_proyecto_form(arquitecto_id: int) -> Optional[Dict]:
    """
    Formulario para subir proyecto de arquitecto

    Args:
        arquitecto_id: ID del arquitecto que sube el proyecto

    Returns:
        Dict con datos del proyecto creado, o None si cancelado
    """
    st.header("🏗️ Subir Proyecto Arquitectónico")

    with st.form("upload_proyecto_form"):
        # Información básica
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del proyecto", placeholder="Casa Moderna Minimalista")
            descripcion = st.text_area("Descripción", placeholder="Proyecto de vivienda unifamiliar...")

        with col2:
            tipo_proyecto = st.selectbox("Tipo", ["Residencial unifamiliar", "Residencial plurifamiliar", "Comercial", "Industrial"])
            superficie_total = st.number_input("Superficie total (m²)", min_value=50, max_value=5000, value=150)

        # Archivos
        st.subheader("📁 Archivos del proyecto")

        col_files1, col_files2 = st.columns(2)

        with col_files1:
            archivo_3d = st.file_uploader("Modelo 3D", type=ALLOWED_EXTENSIONS['3d'], help="OBJ, FBX, GLTF, etc.")
            archivo_rv = st.file_uploader("Render/Video", type=ALLOWED_EXTENSIONS['rv'], help="JPG, PNG, MP4, etc.")
            archivo_pdf = st.file_uploader("Memoria constructiva (PDF)", type=['pdf'], help="Documento técnico completo")

        with col_files2:
            archivo_cad = st.file_uploader("Planos CAD", type=ALLOWED_EXTENSIONS['cad'], help="DXF, DWG, SVG")
            archivo_json = st.file_uploader("Distribución (JSON)", type=['json'], help="JSON con habitaciones y medidas")

        # Metadatos adicionales
        st.subheader("📊 Metadatos")
        precio_venta = st.number_input("Precio de venta (€)", min_value=1000, step=500)
        etiquetas = st.multiselect("Etiquetas", ["Moderno", "Clásico", "Minimalista", "Ecológico", "Accesible", "Bajo consumo"])

        # Validación y envío
        submitted = st.form_submit_button("🚀 Publicar Proyecto", type="primary")

        if submitted:
            return _procesar_upload(
                arquitecto_id=arquitecto_id,
                nombre=nombre,
                descripcion=descripcion,
                tipo_proyecto=tipo_proyecto,
                superficie_total=superficie_total,
                archivos={
                    '3d': archivo_3d,
                    'rv': archivo_rv,
                    'pdf': archivo_pdf,
                    'cad': archivo_cad,
                    'json': archivo_json
                },
                precio_venta=precio_venta,
                etiquetas=etiquetas
            )

    return None

def _procesar_upload(arquitecto_id: int, nombre: str, descripcion: str, tipo_proyecto: str,
                    superficie_total: float, archivos: Dict, precio_venta: float, etiquetas: List[str]) -> Optional[Dict]:
    """
    Procesa la subida de archivos y crea el proyecto
    """
    try:
        # Validar datos mínimos
        if not nombre or not descripcion:
            st.error("❌ Nombre y descripción son obligatorios")
            return None

        # Crear directorio para el proyecto
        proyecto_dir = os.path.join(UPLOAD_DIR, f"arquitecto_{arquitecto_id}_{int(st.session_state.get('timestamp', 0))}")
        os.makedirs(proyecto_dir, exist_ok=True)

        # Guardar archivos y obtener URLs
        urls_archivos = {}

        for tipo, archivo in archivos.items():
            if archivo is not None:
                filename = _sanitize_filename(archivo.name)
                filepath = os.path.join(proyecto_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(archivo.getbuffer())

                urls_archivos[f'{tipo}_url'] = filepath

        # Procesar JSON de distribución si existe
        json_distribucion = None
        if archivos['json']:
            try:
                json_data = json.loads(archivos['json'].getvalue().decode('utf-8'))
                json_distribucion = json_data
            except:
                st.warning("⚠️ No se pudo procesar el archivo JSON de distribución")

        # Generar documentación si no existe
        memoria_texto = ""
        presupuesto_data = {}

        if not archivos['pdf'] and json_distribucion:
            # Generar memoria básica desde JSON
            memoria_texto = generar_memoria_constructiva(json_distribucion, superficie_total * 3)  # Estimación
            presupuesto_data = generar_presupuesto_estimado(json_distribucion)

        # Crear proyecto
        proyecto_data = {
            'autor_tipo': 'arquitecto',
            'autor_id': arquitecto_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'tipo': tipo_proyecto.lower().replace(' ', '_'),
            'total_m2': superficie_total,
            'precio_venta': precio_venta,
            'etiquetas': etiquetas,
            'json_distribucion': json_distribucion,
            'memoria_texto': memoria_texto,
            'presupuesto_estimado': presupuesto_data,
            'validacion_ok': True,  # Asumimos validado por arquitecto
            'estado_publicacion': 'publicada',
            **urls_archivos
        }

        # Guardar en base de datos
        if save_proyecto(proyecto_data):
            st.success("✅ Proyecto publicado exitosamente en el marketplace!")
            return proyecto_data
        else:
            st.error("❌ Error al guardar el proyecto")
            return None

    except Exception as e:
        st.error(f"❌ Error procesando subida: {str(e)}")
        return None

# === FUNCIONES DE EXPLORACIÓN ===
def explorar_proyectos_arquitectos(filtros: Dict = None) -> List[Dict]:
    """
    Lista proyectos de arquitectos disponibles
    """
    from .data_access import list_proyectos

    filtros_arquitectos = {'autor_tipo': 'arquitecto'}
    if filtros:
        filtros_arquitectos.update(filtros)

    return list_proyectos(filtros_arquitectos)

def mostrar_proyecto_arquitecto(proyecto: Dict):
    """
    Muestra detalles de un proyecto de arquitecto
    """
    st.subheader(f"🏗️ {proyecto['nombre']}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(f"**Descripción:** {proyecto.get('descripcion', 'Sin descripción')}")
        st.write(f"**Tipo:** {proyecto.get('tipo', 'No especificado').replace('_', ' ').title()}")
        st.write(f"**Superficie:** {proyecto.get('total_m2', 0)} m²")

        if proyecto.get('etiquetas'):
            st.write(f"**Etiquetas:** {', '.join(proyecto['etiquetas'])}")

        if proyecto.get('presupuesto_estimado'):
            presupuesto = proyecto['presupuesto_estimado']
            st.metric("Presupuesto estimado", f"€{presupuesto.get('total_estimado', 0):,.0f}")

    with col2:
        st.metric("Precio de venta", f"€{proyecto.get('precio_venta', 0):,.0f}")

        # Archivos disponibles
        archivos = []
        if proyecto.get('3d_url'): archivos.append("3D")
        if proyecto.get('rv_url'): archivos.append("RV")
        if proyecto.get('pdf_url'): archivos.append("PDF")
        if proyecto.get('cad_url'): archivos.append("CAD")

        if archivos:
            st.write(f"**Archivos:** {', '.join(archivos)}")

    # Vista previa de distribución
    if proyecto.get('json_distribucion'):
        with st.expander("📊 Distribución del proyecto"):
            st.json(proyecto['json_distribucion'])

    # Memoria constructiva
    if proyecto.get('memoria_texto'):
        with st.expander("📄 Memoria constructiva"):
            st.code(proyecto['memoria_texto'], language="text")

# === FUNCIONES AUXILIARES ===
def _sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo para evitar problemas de seguridad
    """
    import re
    return re.sub(r'[^\w\.-]', '_', filename)

def validar_proyecto_minimo(archivos: Dict) -> Tuple[bool, str]:
    """
    Valida que el proyecto tenga archivos mínimos
    """
    tiene_3d_o_json = archivos.get('3d') is not None or archivos.get('json') is not None
    tiene_documentacion = archivos.get('pdf') is not None

    if not tiene_3d_o_json:
        return False, "Se requiere modelo 3D o distribución JSON"

    if not tiene_documentacion:
        return False, "Se requiere memoria constructiva en PDF"

    return True, "Proyecto válido"

def proyectos_por_arquitecto(arquitecto_id: int) -> List[Dict]:
    """
    Lista proyectos de un arquitecto específico
    """
    from .data_access import list_proyectos
    return list_proyectos({'autor_tipo': 'arquitecto', 'autor_id': arquitecto_id})