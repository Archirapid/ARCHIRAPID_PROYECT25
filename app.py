"""
ARCHIRAPID MVP - Main Application
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime
import base64
import json
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from payment_simulator import payment_modal, show_payment_success

# Configuration
BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

st.set_page_config(page_title="ARCHIRAPID MVP", layout="wide")

def init_db():
    """Initialize database using centralized src.db module."""
    from src.db import ensure_tables
    ensure_tables()

def save_file(uploaded_file, prefix="file", max_size_mb=10, allowed_mime_types=None):
    """
    Guarda archivo uploaded con validaciones de seguridad.
    
    Args:
        uploaded_file: Archivo de Streamlit file_uploader
        prefix: Prefijo para nombre del archivo
        max_size_mb: Tamaño máximo en MB (default 10MB)
        allowed_mime_types: Lista de MIME types permitidos (None = permitir todos)
    
    Returns:
        str: Path del archivo guardado
    
    Raises:
        ValueError: Si el archivo excede tamaño o MIME type no permitido
    """
    # Validar tamaño
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(f"Archivo demasiado grande ({file_size_mb:.1f}MB). Máximo: {max_size_mb}MB")
    
    # Validar MIME type real (no solo extensión)
    if allowed_mime_types:
        file_bytes = uploaded_file.getvalue()
        detected_mime = uploaded_file.type  # Default: confiar en browser
        
        # Intentar detección real con python-magic si está disponible
        try:
            import magic
            detected_mime = magic.from_buffer(file_bytes, mime=True)
        except ImportError:
            pass  # Usar tipo reportado por browser
        except Exception:
            pass  # Fallback silencioso
        
        if detected_mime not in allowed_mime_types:
            raise ValueError(f"Tipo de archivo no permitido ({detected_mime}). Permitidos: {', '.join(allowed_mime_types)}")
    
    # Guardar archivo
    ext = os.path.splitext(uploaded_file.name)[1]
    fname = f"{prefix}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOADS, fname)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    from src.logger import log
    log('file_upload_success', prefix=prefix, size_mb=round(file_size_mb, 2), mime=uploaded_file.type)
    
    return path


# =====================================================
# SUBSCRIPTION & PROPOSALS HELPERS
# =====================================================
def get_subscription_plans():
    """Planes de suscripción disponibles"""
    return {
        'BÁSICO': {'price': 29, 'proposals_limit': 3, 'commission': 0.12, 'features': ['3 propuestas/mes', 'Fincas hasta 500m²', 'Comisión 12%']},
        'PRO': {'price': 79, 'proposals_limit': 10, 'commission': 0.10, 'features': ['10 propuestas/mes', 'Acceso todas las fincas', 'Comisión 10%', 'Badge Verificado']},
        'PREMIUM': {'price': 149, 'proposals_limit': 999, 'commission': 0.08, 'features': ['Propuestas ilimitadas', 'Prioridad en matching', 'Comisión 8%', 'Diseños 3D premium']}
    }

def get_architect_subscription(architect_id):
    """Obtiene suscripción activa del arquitecto"""
    from src.db import get_conn
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM subscriptions WHERE architect_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1", conn, params=(architect_id,))
    conn.close()
    if df.shape[0] == 0:
        return None
    return df.iloc[0].to_dict()

def insert_subscription(data):
    """Crear nueva suscripción"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO subscriptions (id, architect_id, plan_type, price, monthly_proposals_limit, commission_rate, status, start_date, end_date, created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['architect_id'], data['plan_type'], data['price'], data['monthly_proposals_limit'], 
        data['commission_rate'], data['status'], data['start_date'], data.get('end_date'), data['created_at']
    ))
    conn.commit()
    conn.close()

def get_proposals_sent_this_month(architect_id):
    """Cuenta propuestas enviadas este mes"""
    from datetime import datetime
    current_month = datetime.now().strftime('%Y-%m')
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT COUNT(*) as count FROM proposals WHERE architect_id = ? AND created_at LIKE ?", 
                           conn, params=(architect_id, f"{current_month}%"))
    conn.close()
    return df.iloc[0]['count'] if df.shape[0] > 0 else 0

def insert_proposal(data):
    """Insertar nueva propuesta con detalles económicos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO proposals (
        id, architect_id, plot_id, proposal_text, estimated_budget, deadline_days, 
        sketch_image_path, status, created_at, responded_at,
        delivery_format, delivery_price, supervision_fee, visa_fee, total_cliente, commission,
        project_id
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['architect_id'], data['plot_id'], data['proposal_text'], 
        data['estimated_budget'], data['deadline_days'], data.get('sketch_image_path'), 
        data['status'], data['created_at'], data.get('responded_at'),
        data.get('delivery_format', 'PDF'), data.get('delivery_price', 1200),
        data.get('supervision_fee', 0), data.get('visa_fee', 0),
        data.get('total_cliente', 0), data.get('commission', 0),
        data.get('project_id')
    ))
    conn.commit()
    conn.close()

def get_proposals_for_plot(plot_id):
    """Obtiene todas las propuestas para una finca"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT p.*, a.name as architect_name, a.email as architect_email, a.company as architect_company
        FROM proposals p
        LEFT JOIN architects a ON p.architect_id = a.id
        WHERE p.plot_id = ?
        ORDER BY p.created_at DESC
    """, conn, params=(plot_id,))
    conn.close()
    return df

def get_client_proposals(client_email):
    """Obtiene todas las propuestas recibidas por un cliente (vía fincas de su propiedad)"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT 
            p.*,
            a.name as architect_name, 
            a.email as architect_email,
            a.company as architect_company,
            pl.title as plot_title,
            pl.province as plot_province,
            pl.m2 as plot_m2,
            proj.title as project_title,
            proj.foto_principal as project_photo,
            proj.m2_construidos as project_m2,
            proj.habitaciones as project_rooms,
            proj.style as project_style
        FROM proposals p
        LEFT JOIN architects a ON p.architect_id = a.id
        LEFT JOIN plots pl ON p.plot_id = pl.id
        LEFT JOIN projects proj ON p.project_id = proj.id
        WHERE pl.owner_email = ?
        ORDER BY p.created_at DESC
    """, conn, params=(client_email,))
    conn.close()
    return df

def update_proposal_status(proposal_id, new_status):
    """Actualiza estado de propuesta (accepted/rejected)"""
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE proposals SET status = ?, responded_at = ? WHERE id = ?", 
              (new_status, datetime.now().isoformat(), proposal_id))
    conn.commit()
    conn.close()

# =====================================================
# PROJECTS PORTFOLIO HELPERS
# =====================================================
def insert_project(data):
    """Inserta nuevo proyecto en portfolio de arquitecto"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO projects (
        id, title, architect_name, architect_id, area_m2, max_height, style, price, 
        file_path, description, created_at, m2_construidos, m2_parcela_minima, m2_parcela_maxima,
        habitaciones, banos, garaje, plantas, certificacion_energetica, tipo_proyecto,
        foto_principal, galeria_fotos, modelo_3d_glb, render_vr, planos_pdf, 
        planos_dwg, memoria_pdf, presupuesto_pdf, gemelo_digital_ifc
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['title'], data.get('architect_name'), data['architect_id'],
        data.get('area_m2'), data.get('max_height'), data.get('style'), data.get('price'),
        data.get('file_path'), data.get('description'), data['created_at'],
        data.get('m2_construidos'), data.get('m2_parcela_minima'), data.get('m2_parcela_maxima'),
        data.get('habitaciones'), data.get('banos'), data.get('garaje'), data.get('plantas'),
        data.get('certificacion_energetica'), data.get('tipo_proyecto'),
        data.get('foto_principal'), data.get('galeria_fotos'), data.get('modelo_3d_glb'),
        data.get('render_vr'), data.get('planos_pdf'), data.get('planos_dwg'),
        data.get('memoria_pdf'), data.get('presupuesto_pdf'), data.get('gemelo_digital_ifc')
    ))
    conn.commit()
    conn.close()

def get_architect_projects(architect_id):
    """Obtiene todos los proyectos de un arquitecto"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects WHERE architect_id = ? ORDER BY created_at DESC", 
                           conn, params=(architect_id,))
    conn.close()
    return df

def get_project_by_id(project_id):
    """Obtiene un proyecto específico"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects WHERE id = ?", conn, params=(project_id,))
    conn.close()
    if df.shape[0] == 0:
        return None
    return df.iloc[0].to_dict()

def get_compatible_projects(plot_m2, plot_type='vivienda'):
    """
    Algoritmo de matching: encuentra proyectos compatibles con una finca
    Criterios: m2_parcela dentro del rango, tipo compatible
    """
    conn = sqlite3.connect(DB_PATH)
    # Busca proyectos donde el m2 de la parcela esté en el rango [minima, maxima]
    query = """
        SELECT *, 
        CASE 
            WHEN ? BETWEEN m2_parcela_minima AND m2_parcela_maxima THEN 100
            WHEN ? < m2_parcela_minima THEN 50
            ELSE 30
        END as match_score
        FROM projects 
        WHERE m2_parcela_minima IS NOT NULL 
        ORDER BY match_score DESC, created_at DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn, params=(plot_m2, plot_m2))
    conn.close()
    return df

def delete_project(project_id):
    """Elimina un proyecto"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# =====================================================
# DB FUNCTIONS - Delegate to src.db for consistency
# =====================================================
from src.db import insert_plot, get_all_plots, get_plot_by_id, insert_project, get_all_projects

def insert_reservation(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO reservations (id, plot_id, buyer_name, buyer_email, amount, kind, created_at) VALUES (?,?,?,?,?,?,?)',
              (data['id'], data['plot_id'], data['buyer_name'], data['buyer_email'], data['amount'], data['kind'], data['created_at']))
    conn.commit()
    conn.close()

def get_image_base64(image_path):
    try:
        with open(image_path, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    except Exception:
        return None

# =====================================================
# MODAL: ANÁLISIS CATASTRAL
# =====================================================
@st.dialog("📊 Análisis Catastral Completo", width="small")
def show_analysis_modal(plot_id):
    """Modal profesional con tabs para análisis catastral completo"""
    from pathlib import Path
    
    cache_all = st.session_state.get('analysis_cache', {})
    cache = cache_all.get(plot_id)
    
    if not cache:
        st.error("❌ No hay datos de análisis disponibles.")
        return
    
    # CRÍTICO: Obtener datos REALES de la finca desde BD (no confiar solo en OCR)
    plot_data = get_plot_by_id(plot_id)
    if not plot_data:
        st.error("❌ No se encontró la finca en la base de datos.")
        return
    
    edata = cache.get('edata') or {}
    vdata = cache.get('vdata') or {}
    output_dir = Path(cache.get('output_dir', 'archirapid_extract/catastro_output'))
    overlay_img = output_dir / "contours_visualization.png"
    clean_img = output_dir / "contours_clean.png"
    
    user_has_paid = st.session_state.get('payment_completed', False)
    
    # USAR DATOS REALES DE LA BD (no del OCR que puede estar equivocado)
    plot_type = plot_data.get('type', 'rural').lower()
    is_buildable = plot_type in ['urban', 'industrial']
    
    tab_names = ["📊 Métricas", "🗺️ Plano", "📥 DXF"]
    if user_has_paid and is_buildable:
        tab_names.append("🏗️ Diseñador IA")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        # Destacar estado edificable con banner visual
        if is_buildable:
            st.success(f"### ✅ FINCA EDIFICABLE - Tipo: {plot_data.get('type', 'N/A').upper()}")
        else:
            st.error(f"### ❌ NO EDIFICABLE - Tipo: {plot_data.get('type', 'N/A').upper()}")
        
        st.markdown("---")
        st.markdown("### 📋 Información Registrada (Base de Datos)")
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.metric("📍 Tipo de Finca", plot_data.get('type', 'N/A').upper())
        with bc2:
            st.metric("📏 Superficie Registrada", f"{plot_data.get('m2', 0):,.0f} m²")
        with bc3:
            st.metric("💰 Precio", f"€{plot_data.get('price', 0):,.0f}")
        
        st.markdown("---")
        st.markdown("### 🔍 Datos del Análisis Catastral (OCR)")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.metric("Ref. Catastral", edata.get("cadastral_ref") or "N/A")
            st.metric("Superficie Detectada", f"{edata.get('surface_m2', 0):,.0f} m²")
        with mc2:
            st.metric("Máx. Edificable (estimado)", f"{edata.get('max_buildable_m2', 0):,.1f} m²")
            perc = edata.get('edificability_percent') or 0
            st.metric("% Edificabilidad", f"{perc*100:.1f}%")
        
        # Info sobre validación de datos
        ocr_type = vdata.get('classification', {}).get('terrain_type', '') if vdata else ''
        if ocr_type and ocr_type.lower() not in ['', 'desconocido', plot_type]:
            st.info(f"ℹ️ **Nota:** El OCR detectó '{ocr_type}' en el PDF, pero prevalecen los datos registrados ('{plot_type.upper()}'). La clasificación definitiva la determina el registro oficial.")
    
    with tabs[1]:
        if clean_img.exists():
            st.image(str(clean_img), width='stretch')
    
    with tabs[2]:
        try:
            from archirapid_extract.export_dxf import create_dxf_from_cadastral_output
            dxf_bytes = create_dxf_from_cadastral_output(output_dir=str(output_dir), scale_factor=0.1)
            if dxf_bytes:
                ref = edata.get("cadastral_ref") or "parcela"
                st.download_button("⬇️ Descargar DXF", dxf_bytes, f"ARCHIRAPID_{ref}.dxf", "application/dxf", width='stretch')
        except Exception as e:
            st.error(f"Error: {e}")
    
    if user_has_paid and is_buildable and len(tabs) > 3:
        with tabs[3]:
            st.caption("🎯 Diseño paramétrico 3D")
            c1, c2, c3 = st.columns(3)
            with c1:
                beds = st.selectbox("Dormitorios", [1,2,3,4], 1, key=f"beds_{plot_id}")
            with c2:
                floors = st.selectbox("Plantas", [1,2,3], 0, key=f"floors_{plot_id}")
            with c3:
                setback = st.slider("Retranqueo (m)", 1.0, 8.0, 3.0, 0.5, key=f"set_{plot_id}")
            
            if st.button("🚀 Generar Diseño", key=f"gen_{plot_id}", type="primary", width='stretch'):
                st.session_state['design_requested'] = {'bedrooms': beds, 'floors': floors, 'setback': setback, 'plot_id': plot_id}
                st.rerun()
            
            design_key = f"design_result_{plot_id}"
            if st.session_state.get(design_key):
                res = st.session_state[design_key]
                if res.get('success'):
                    plan_path = "archirapid_extract/design_output/design_plan.png"
                    if os.path.exists(plan_path):
                        st.image(plan_path, width='stretch')
                    model_path = "archirapid_extract/design_output/design_model.glb"
                    if os.path.exists(model_path):
                        with open(model_path, 'rb') as f:
                            glb = f.read()
                        import base64 as b64
                        st.components.v1.html(f'<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script><model-viewer src="data:model/gltf-binary;base64,{b64.b64encode(glb).decode()}" camera-controls auto-rotate style="width:100%;height:400px;"></model-viewer>', 420)
    elif is_buildable and not user_has_paid:
        st.info("💡 Reserva o compra para acceder al Diseñador IA")

# =====================================================
# MODAL: ENVÍO DE PROPUESTA (Arquitecto → Propietario)
# =====================================================
@st.dialog("📨 Enviar Propuesta", width="small")
def show_proposal_modal(plot_id, architect_id):
    """Modal para que arquitecto envíe propuesta"""
    plot = get_plot_by_id(plot_id)
    subscription = get_architect_subscription(architect_id)
    
    if not plot:
        st.error("❌ Finca no encontrada")
        return
    
    if not subscription:
        st.error("❌ Necesitas una suscripción activa")
        return
    
    # Verificar límite mensual
    proposals_sent = get_proposals_sent_this_month(architect_id)
    remaining = subscription['monthly_proposals_limit'] - proposals_sent
    
    if remaining <= 0:
        st.error(f"❌ Has alcanzado el límite de {subscription['monthly_proposals_limit']} propuestas/mes")
        st.info("💡 Actualiza tu plan para enviar más propuestas")
        return
    
    st.info(f"📊 Te quedan {remaining}/{subscription['monthly_proposals_limit']} propuestas este mes")
    
    # Mostrar info de la finca
    st.markdown(f"### 🏡 {plot['title']}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📏 Superficie", f"{int(plot['m2']):,} m²")
    with col2:
        st.metric("💰 Precio Finca", f"€{int(plot['price']):,}")
    with col3:
        st.metric("📍 Ubicación", f"{plot['province']}")
    
    st.markdown("---")
    
    # Opción: enviar con proyecto de portfolio o propuesta libre
    st.markdown("### 📂 Tipo de Propuesta")
    proposal_type = st.radio(
        "",
        ["💼 Con Proyecto de mi Portfolio", "✍️ Propuesta Personalizada"],
        horizontal=True,
        help="Envía un proyecto existente o escribe una propuesta desde cero"
    )
    
    selected_project = None
    if proposal_type == "💼 Con Proyecto de mi Portfolio":
        # Cargar proyectos del arquitecto
        projects_df = get_architect_projects(architect_id)
        
        if projects_df.shape[0] == 0:
            st.warning("⚠️ No tienes proyectos en tu portfolio. Ve a 'Mis Proyectos' para crear uno.")
            st.info("💡 O selecciona 'Propuesta Personalizada' para enviar texto libre")
        else:
            # Filtrar proyectos compatibles con la parcela
            compatible_projects = []
            for idx, proj in projects_df.iterrows():
                if (proj.get('m2_parcela_minima') and proj.get('m2_parcela_maxima') and
                    plot['m2'] >= proj['m2_parcela_minima'] and plot['m2'] <= proj['m2_parcela_maxima']):
                    compatible_projects.append((proj['id'], f"✅ {proj['title']} ({proj['m2_construidos']}m², {proj.get('habitaciones', '?')} hab) - COMPATIBLE"))
                else:
                    compatible_projects.append((proj['id'], f"⚠️ {proj['title']} ({proj['m2_construidos']}m², {proj.get('habitaciones', '?')} hab)"))
            
            if compatible_projects:
                project_options = {title: pid for pid, title in compatible_projects}
                selected_title = st.selectbox(
                    "Selecciona un proyecto:",
                    options=list(project_options.keys()),
                    help="Los proyectos marcados con ✅ son compatibles con el tamaño de la parcela"
                )
                
                selected_project_id = project_options[selected_title]
                selected_project = get_project_by_id(selected_project_id)
                
                if selected_project:
                    st.success(f"📐 Proyecto seleccionado: **{selected_project['title']}**")
                    
                    # Mostrar preview del proyecto
                    prev_col1, prev_col2, prev_col3 = st.columns(3)
                    with prev_col1:
                        if selected_project.get('foto_principal') and os.path.exists(selected_project['foto_principal']):
                            st.image(selected_project['foto_principal'], width='stretch')
                    with prev_col2:
                        st.metric("m² Construidos", selected_project.get('m2_construidos', '-'))
                        st.metric("Habitaciones", selected_project.get('habitaciones', '-'))
                    with prev_col3:
                        st.metric("Precio Estimado", f"€{selected_project.get('price', 0):,.0f}")
                        st.metric("Estilo", selected_project.get('style', '-').title())
                    
                    # Auto-rellenar datos desde proyecto
                    proposal_text = st.text_area(
                        "📝 Mensaje al propietario (opcional)",
                        value=f"Le presento mi proyecto '{selected_project['title']}':\n\n{selected_project.get('description', '')}",
                        height=150
                    )
                    
                    # Usar datos del proyecto
                    estimated_budget = selected_project.get('price', 50000)
                    deadline_days = 90  # Default
                    
                    st.caption(f"💰 Presupuesto: €{estimated_budget:,.0f} (desde proyecto)")
                    st.caption("📅 Plazo de entrega: 90 días (ajustable después)")
    
    if proposal_type == "✍️ Propuesta Personalizada" or selected_project is None:
        # Formulario de propuesta libre
        proposal_text = st.text_area(
            "📝 Describe tu propuesta al propietario",
            placeholder="Explica tu visión para esta finca, experiencia relevante, metodología de trabajo...",
            height=150
        )
        
        col_budget, col_deadline = st.columns(2)
        with col_budget:
            estimated_budget = st.number_input(
                "💰 Presupuesto Estimado Proyecto (€)",
                min_value=1000,
                value=50000,
                step=1000,
                help="Presupuesto total del proyecto arquitectónico completo"
            )
        with col_deadline:
            deadline_days = st.number_input(
                "📅 Plazo de Entrega (días)",
                min_value=7,
                value=90,
                step=7,
                help="Días estimados para completar el proyecto"
            )
        
        sketch_file = st.file_uploader(
            "🎨 Boceto Inicial (opcional)",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Sube un boceto o croquis inicial para destacar tu propuesta"
        )
    else:
        sketch_file = None

    
    # Configurar tarifas al cliente
    st.markdown("---")
    st.markdown("### 💸 Tarifas al Cliente")
    
    # Formato de entrega
    delivery_format = st.radio(
        "📦 Formato de Entrega",
        ["📄 PDF Básico (+€1,200)", "🖥️ AutoCAD/DWG (+€1,800)"],
        horizontal=True,
        help="Tarifa adicional por formato de entrega profesional"
    )
    delivery_price = 1200 if "PDF" in delivery_format else 1800
    
    # Servicios adicionales
    st.markdown("#### Servicios Opcionales")
    col_serv1, col_serv2 = st.columns(2)
    
    with col_serv1:
        include_supervision = st.checkbox("🏗️ Dirección de Obra", help="Supervisión técnica durante construcción")
        if include_supervision:
            supervision_fee = st.number_input("Honorarios Dirección (€)", min_value=0, value=15000, step=500)
        else:
            supervision_fee = 0
    
    with col_serv2:
        include_visa = st.checkbox("📋 Visado Colegial", help="Trámite visado colegio arquitectos")
        if include_visa:
            visa_fee = st.number_input("Coste Visado (€)", min_value=0, value=800, step=50)
        else:
            visa_fee = 0
    
    # Calcular totales
    subtotal = estimated_budget + delivery_price + supervision_fee + visa_fee
    commission = subtotal * subscription['commission_rate']
    total_cliente = subtotal + commission
    net_revenue = subtotal - commission
    
    st.markdown("---")
    st.markdown("#### � Resumen para el Cliente")
    
    # Desglose detallado
    st.caption(f"**Proyecto base:** €{estimated_budget:,.0f}")
    st.caption(f"**Formato entrega** ({delivery_format.split('(')[0].strip()}): +€{delivery_price:,.0f}")
    if supervision_fee > 0:
        st.caption(f"**Dirección de Obra:** +€{supervision_fee:,.0f}")
    if visa_fee > 0:
        st.caption(f"**Visado Colegial:** +€{visa_fee:,.0f}")
    st.caption(f"**Comisión ARCHIRAPID ({subscription['commission_rate']*100:.0f}%):** +€{commission:,.0f}")
    
    st.markdown("---")
    
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.metric("💰 TOTAL CLIENTE", f"€{total_cliente:,.0f}", help="Precio final que pagará el propietario")
    with dcol2:
        st.metric("💵 Tu Ingreso Neto", f"€{net_revenue:,.0f}", delta=f"+{net_revenue:,.0f}", help="Tu beneficio después de comisión ARCHIRAPID")
    
    st.markdown("---")
    
    if st.button("✅ Enviar Propuesta", type="primary", width='stretch'):
        if not proposal_text or len(proposal_text) < 50:
            st.error("⚠️ La propuesta debe tener al menos 50 caracteres")
        else:
            # Guardar boceto si existe
            sketch_path = None
            if sketch_file:
                sketch_path = save_file(sketch_file, prefix="sketch")
            
            # Crear propuesta con datos económicos completos
            proposal_id = str(uuid.uuid4())
            proposal_data = {
                'id': proposal_id,
                'architect_id': architect_id,
                'plot_id': plot_id,
                'proposal_text': proposal_text,
                'estimated_budget': estimated_budget,
                'deadline_days': deadline_days,
                'sketch_image_path': sketch_path,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'responded_at': None,
                'delivery_format': delivery_format,
                'delivery_price': delivery_price,
                'supervision_fee': supervision_fee,
                'visa_fee': visa_fee,
                'total_cliente': total_cliente,
                'commission': commission,
                'project_id': selected_project['id'] if selected_project else None
            }
            
            insert_proposal(proposal_data)
            
            st.success(f"✅ Propuesta enviada correctamente a {plot.get('owner_name', 'el propietario')}")
            st.balloons()
            st.session_state['send_proposal_to'] = None
            st.rerun()

# =====================================================
# MODAL: CREAR PROYECTO (Portfolio Arquitecto)
# =====================================================
@st.dialog("➕ Nuevo Proyecto", width="small")
def show_create_project_modal(architect_id, architect_name):
    """Modal para crear proyecto en portfolio del arquitecto"""
    
    st.markdown("### 📋 Información Básica")
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("🏗️ Nombre del Proyecto*", placeholder="Villa Mediterránea 3 Dormitorios")
        tipo_proyecto = st.selectbox("📐 Tipo", ["vivienda_unifamiliar", "vivienda_plurifamiliar", "nave_industrial", "local_comercial", "rehabilitacion"])
        style = st.selectbox("🎨 Estilo", ["moderno", "mediterraneo", "industrial", "rustico", "minimalista", "clasico"])
    with col2:
        m2_construidos = st.number_input("📏 m² Construidos*", min_value=30, value=150, step=10)
        price = st.number_input("💰 Precio Estimado (€)*", min_value=10000, value=200000, step=5000)
        certificacion = st.selectbox("⚡ Certificación Energética", ["A", "B", "C", "D", "E", "F", "G", "Sin certificar"])
    
    st.markdown("---")
    st.markdown("### 🎯 Compatibilidad con Parcelas")
    st.caption("Define el rango de parcela ideal para este proyecto")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        m2_parcela_min = st.number_input("Parcela Mínima (m²)*", min_value=50, value=200, step=50)
    with col_p2:
        m2_parcela_max = st.number_input("Parcela Máxima (m²)*", min_value=m2_parcela_min, value=800, step=50)
    with col_p3:
        max_height = st.number_input("Altura Máxima (m)", min_value=3.0, value=7.0, step=0.5)
    
    st.markdown("---")
    st.markdown("### 🏠 Especificaciones Técnicas")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        habitaciones = st.number_input("🛏️ Dormitorios", min_value=1, value=3, step=1)
    with col_s2:
        banos = st.number_input("🚿 Baños", min_value=1, value=2, step=1)
    with col_s3:
        plantas = st.number_input("📐 Plantas", min_value=1, value=2, step=1)
    with col_s4:
        garaje = st.number_input("🚗 Plazas Garaje", min_value=0, value=2, step=1)
    
    description = st.text_area(
        "📝 Descripción Detallada*",
        placeholder="Describe el proyecto: distribución, materiales, orientación, características destacadas...",
        height=100
    )
    
    st.markdown("---")
    st.markdown("### 📸 Archivos y Multimedia")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        foto_principal = st.file_uploader("🖼️ Foto Principal*", type=['jpg', 'jpeg', 'png'], help="Imagen destacada del proyecto")
        galeria = st.file_uploader("📷 Galería Adicional", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
        modelo_3d = st.file_uploader("🎮 Modelo 3D (.glb)", type=['glb'], help="Modelo 3D para visualización interactiva")
    with col_f2:
        planos_pdf = st.file_uploader("📄 Planos PDF", type=['pdf'])
        planos_dwg = st.file_uploader("📐 Planos DWG/DXF", type=['dwg', 'dxf'])
        memoria = st.file_uploader("📋 Memoria Técnica", type=['pdf'])
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("✅ Crear Proyecto", type="primary", width='stretch'):
            if not title or not description or m2_construidos == 0:
                st.error("❌ Completa los campos obligatorios (*)")
            elif not foto_principal:
                st.error("❌ Debes subir al menos una foto principal")
            else:
                with st.spinner("Guardando proyecto..."):
                    # Save files
                    foto_path = save_file(foto_principal, "project_main") if foto_principal else None
                    
                    galeria_paths = []
                    if galeria:
                        for img in galeria:
                            galeria_paths.append(save_file(img, "project_gallery"))
                    
                    modelo_path = save_file(modelo_3d, "project_model") if modelo_3d else None
                    planos_pdf_path = save_file(planos_pdf, "project_plans_pdf") if planos_pdf else None
                    planos_dwg_path = save_file(planos_dwg, "project_plans_dwg") if planos_dwg else None
                    memoria_path = save_file(memoria, "project_memoria") if memoria else None
                    
                    # Create project
                    project_id = str(uuid.uuid4())
                    insert_project({
                        'id': project_id,
                        'title': title,
                        'architect_name': architect_name,
                        'architect_id': architect_id,
                        'area_m2': m2_construidos,
                        'max_height': max_height,
                        'style': style,
                        'price': price,
                        'description': description,
                        'created_at': datetime.now().isoformat(),
                        'm2_construidos': m2_construidos,
                        'm2_parcela_minima': m2_parcela_min,
                        'm2_parcela_maxima': m2_parcela_max,
                        'habitaciones': habitaciones,
                        'banos': banos,
                        'garaje': garaje,
                        'plantas': plantas,
                        'certificacion_energetica': certificacion,
                        'tipo_proyecto': tipo_proyecto,
                        'foto_principal': foto_path,
                        'galeria_fotos': json.dumps(galeria_paths),
                        'modelo_3d_glb': modelo_path,
                        'planos_pdf': planos_pdf_path,
                        'planos_dwg': planos_dwg_path,
                        'memoria_pdf': memoria_path,
                        'file_path': foto_path  # backward compatibility
                    })
                    
                    st.success("🎉 ¡Proyecto creado exitosamente!")
                    st.balloons()
                    st.session_state['show_project_modal'] = False
                    st.rerun()
    
    with col_btn2:
        if st.button("❌ Cancelar", width='stretch'):
            st.session_state['show_project_modal'] = False
            st.rerun()

# =====================================================
# MODAL: DETALLE PROYECTO (Vista completa)
# =====================================================
@st.dialog("🏗️ Detalle del Proyecto", width="small")
def show_project_detail_modal(project):
    """Modal para ver detalles completos de un proyecto"""
    
    st.markdown(f"## {project['title']}")
    st.caption(f"Por {project['architect_name']} • {project['created_at'][:10]}")
    
    # Tabs para organizar información
    tab1, tab2, tab3, tab4 = st.tabs(["📸 Galería", "📊 Especificaciones", "📄 Documentación", "🎮 Modelo 3D"])
    
    with tab1:
        # Foto principal
        if project.get('foto_principal') and os.path.exists(project['foto_principal']):
            st.image(project['foto_principal'], width='stretch', caption="Foto Principal")
        
        # Galería adicional
        if project.get('galeria_fotos'):
            try:
                galeria = json.loads(project['galeria_fotos'])
                if galeria:
                    st.markdown("#### Galería Adicional")
                    cols = st.columns(3)
                    for idx, img_path in enumerate(galeria):
                        if os.path.exists(img_path):
                            with cols[idx % 3]:
                                st.image(img_path, width='stretch')
            except:
                pass
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 m² Construidos", project.get('m2_construidos', '-'))
            st.metric("🛏️ Dormitorios", project.get('habitaciones', '-'))
            st.metric("🚿 Baños", project.get('banos', '-'))
        with col2:
            st.metric("📐 Plantas", project.get('plantas', '-'))
            st.metric("🚗 Garaje", f"{project.get('garaje', 0)} plazas")
            st.metric("⚡ Certificación", project.get('certificacion_energetica', 'N/A'))
        with col3:
            st.metric("💰 Precio Estimado", f"€{project.get('price', 0):,.0f}")
            # Fix: Validar que tipo_proyecto no sea None antes de replace
            tipo = project.get('tipo_proyecto') or '-'
            tipo_display = tipo.replace('_', ' ').title() if tipo != '-' else '-'
            st.metric("� Tipo", tipo_display)
            # Fix: Validar que style no sea None antes de title
            style = project.get('style') or '-'
            style_display = style.title() if style != '-' else '-'
            st.metric("🎨 Estilo", style_display)
        
        st.markdown("---")
        st.markdown("#### 📝 Descripción")
        st.write(project.get('description', 'Sin descripción'))
        
        st.markdown("---")
        st.markdown("#### 🎯 Compatibilidad de Parcela")
        comp_col1, comp_col2, comp_col3 = st.columns(3)
        with comp_col1:
            st.metric("Parcela Mínima", f"{project.get('m2_parcela_minima', 0)} m²")
        with comp_col2:
            st.metric("Parcela Máxima", f"{project.get('m2_parcela_maxima', 0)} m²")
        with comp_col3:
            st.metric("Altura Máxima", f"{project.get('max_height', 0)} m")
    
    with tab3:
        st.markdown("#### 📦 Archivos Técnicos")
        
        doc_col1, doc_col2 = st.columns(2)
        
        with doc_col1:
            if project.get('planos_pdf') and os.path.exists(project['planos_pdf']):
                with open(project['planos_pdf'], 'rb') as f:
                    st.download_button(
                        "📄 Descargar Planos PDF",
                        f.read(),
                        file_name=f"{project['title']}_planos.pdf",
                        mime="application/pdf",
                        width='stretch'
                    )
            else:
                st.info("📄 No hay planos PDF disponibles")
        
        with doc_col2:
            if project.get('planos_dwg') and os.path.exists(project['planos_dwg']):
                with open(project['planos_dwg'], 'rb') as f:
                    fname = os.path.basename(project['planos_dwg'])
                    st.download_button(
                        "📐 Descargar Planos DWG",
                        f.read(),
                        file_name=fname,
                        width='stretch'
                    )
            else:
                st.info("📐 No hay planos DWG disponibles")
        
        if project.get('memoria_pdf') and os.path.exists(project['memoria_pdf']):
            with open(project['memoria_pdf'], 'rb') as f:
                st.download_button(
                    "📋 Descargar Memoria Técnica",
                    f.read(),
                    file_name=f"{project['title']}_memoria.pdf",
                    mime="application/pdf",
                    width='stretch'
                )
    
    with tab4:
        if project.get('modelo_3d_glb') and os.path.exists(project['modelo_3d_glb']):
            with open(project['modelo_3d_glb'], 'rb') as f:
                glb_data = f.read()
            
            import base64 as b64
            glb_b64 = b64.b64encode(glb_data).decode()
            
            st.markdown("#### 🎮 Visualización Interactiva 3D")
            st.components.v1.html(
                f'''
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer 
                    src="data:model/gltf-binary;base64,{glb_b64}" 
                    camera-controls 
                    auto-rotate 
                    style="width:100%;height:500px;background-color:#f0f0f0;"
                    shadow-intensity="1"
                    ar
                ></model-viewer>
                ''',
                height=520
            )
        else:
            st.info("🎮 No hay modelo 3D disponible")
    
    if st.button("✅ Cerrar", type="primary"):
        st.session_state['view_project_id'] = None
        st.rerun()


# Initialize DB
init_db()

# =====================================================
# 🎨 HEADER PROFESIONAL CON LOGO Y BRANDING
# =====================================================
logo_path = "assets/branding/logo.png"
logo_data_uri = get_image_base64(logo_path) if os.path.exists(logo_path) else None
if logo_data_uri:
    # Header con logo embebido (base64) para asegurar render en HTML personalizado
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:22px; max-width:880px; margin:8px auto 18px auto; padding:12px 28px; border-radius:14px; background:linear-gradient(95deg,#fdfefe,#ffffff); box-shadow:0 3px 10px rgba(0,0,0,0.06);'>
        <div style='flex:0 0 auto; display:flex; align-items:center;'>
            <img src='{logo_data_uri}' alt='Logo Archirapid' style='height:78px; max-width:260px; object-fit:contain; filter:drop-shadow(0 1px 2px rgba(0,0,0,0.12));'>
        </div>
        <div style='flex:1; min-width:0;'>
            <div style='font-size:23px; font-weight:600; color:#2d3748; line-height:1.15; margin:0;'>Arquitectura Inteligente + Datos</div>
            <div style='font-size:14px; color:#4a5568; margin-top:5px; line-height:1.3;'>Analizamos fincas, edificabilidad y viabilidad para decisiones más rápidas y seguras.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # KPIs debajo del header
    try:
        from src.db import cached_counts as counts_fn
        from src.logger import get_recent_events
        k = counts_fn()
        recent = get_recent_events(limit=50)
        has_errors = any(ev.get('level') == 'ERROR' for ev in recent)
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.markdown(f"<div class='ar-card'><h4>🏡 Fincas</h4><div class='ar-metric-value'>{k.get('plots',0)}</div></div>", unsafe_allow_html=True)
        kpi_col2.markdown(f"<div class='ar-card'><h4>📐 Proyectos</h4><div class='ar-metric-value'>{k.get('projects',0)}</div></div>", unsafe_allow_html=True)
        kpi_col3.markdown(f"<div class='ar-card'><h4>💳 Pagos</h4><div class='ar-metric-value'>{k.get('payments',0)}</div></div>", unsafe_allow_html=True)
        if has_errors:
            kpi_col4.markdown("<div class='ar-card' style='background:#fef2f2;border-color:#fecaca'><h4>⚠️ Errores</h4><div class='ar-metric-value' style='color:#dc2626'>Sí</div></div>", unsafe_allow_html=True)
        else:
            kpi_col4.markdown("<div class='ar-card' style='background:#f0fdf4;border-color:#bbf7d0'><h4>✔️ Errores</h4><div class='ar-metric-value' style='color:#16a34a'>0</div></div>", unsafe_allow_html=True)
    except Exception:
        pass
else:
    # Fallback sin logo: caja centrada con aviso de subida
    st.markdown("""
    <div style='max-width:880px; margin:8px auto 18px auto; padding:16px 30px; border-radius:14px; background:#ffffff; box-shadow:0 3px 10px rgba(0,0,0,0.05);'>
        <div style='font-size:23px; font-weight:600; color:#2d3748; line-height:1.15; margin:0;'>Archirapid</div>
        <div style='font-size:14px; color:#4a5568; margin-top:6px; line-height:1.3;'>Sube tu logo a <code>assets/branding/logo.png</code> para mostrarlo aquí.</div>
    </div>
    """, unsafe_allow_html=True)
    try:
        from src.db import cached_counts as counts_fn
        from src.logger import get_recent_events
        k = counts_fn()
        recent = get_recent_events(limit=50)
        has_errors = any(ev.get('level') == 'ERROR' for ev in recent)
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        kpi_col1.markdown(f"<div class='ar-card'><h4>🏡 Fincas</h4><div class='ar-metric-value'>{k.get('plots',0)}</div></div>", unsafe_allow_html=True)
        kpi_col2.markdown(f"<div class='ar-card'><h4>📐 Proyectos</h4><div class='ar-metric-value'>{k.get('projects',0)}</div></div>", unsafe_allow_html=True)
        kpi_col3.markdown(f"<div class='ar-card'><h4>💳 Pagos</h4><div class='ar-metric-value'>{k.get('payments',0)}</div></div>", unsafe_allow_html=True)
        if has_errors:
            kpi_col4.markdown("<div class='ar-card' style='background:#fef2f2;border-color:#fecaca'><h4>⚠️ Errores</h4><div class='ar-metric-value' style='color:#dc2626'>Sí</div></div>", unsafe_allow_html=True)
        else:
            kpi_col4.markdown("<div class='ar-card' style='background:#f0fdf4;border-color:#bbf7d0'><h4>✔️ Errores</h4><div class='ar-metric-value' style='color:#16a34a'>0</div></div>", unsafe_allow_html=True)
    except Exception:
        pass

# =====================================================
# 🌐 GLOBAL CSS THEME (cards, typography, buttons refinements)
# =====================================================
GLOBAL_CSS = """
<style>
html, body, [class*='css'] { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
.ar-card { background:#ffffff; border:1px solid #e5e7eb; padding:16px 18px; border-radius:14px; box-shadow:0 2px 4px rgba(0,0,0,.04); margin-bottom:14px; }
.ar-card h3, .ar-card h4 { margin-top:0; font-weight:600; color:#1f2937; }
.ar-badge { display:inline-block; background:#eef2ff; color:#4338ca; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:500; }
.ar-metric { display:flex; align-items:center; gap:10px; }
.ar-metric-value { font-size:20px; font-weight:600; color:#111827; }
.ar-btn-primary { background:#4f46e5; color:#fff; padding:10px 18px; border-radius:8px; text-decoration:none; display:inline-block; font-weight:600; }
.ar-btn-primary:hover { background:#4338ca; }
@media (max-width: 900px){ .ar-responsive-hide { display:none !important; } }
html { scroll-behavior:smooth; }
 /* Eventos recientes */
 .events-table { width:100%; border-collapse:collapse; font-size:12px; }
 .events-table th { background:#f3f4f6; text-align:left; padding:6px 8px; border-bottom:1px solid #e5e7eb; }
 .events-table td { padding:6px 8px; border-bottom:1px solid #f1f5f9; }
 .level-ERROR { color:#dc2626; font-weight:600; }
 .level-WARN { color:#d97706; font-weight:600; }
 .level-INFO { color:#2563eb; }
 .level-DEBUG { color:#64748b; }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# =====================================================
# 📡 PANEL DE EVENTOS (Observabilidad)
# =====================================================
from src.logger import get_recent_events
with st.sidebar.expander("📡 Eventos recientes", expanded=False):
    limit = st.number_input("Máx eventos", min_value=5, max_value=200, value=30, step=5, key="events_limit")
    if st.button("Refrescar eventos", key="refresh_events"):
        st.session_state['_events_refresh'] = datetime.utcnow().isoformat()
    events = get_recent_events(limit=limit)
    if not events:
        st.caption("No hay eventos en el log todavía.")
    else:
        rows = []
        for ev in events:
            ts = ev.get('ts', ev.get('raw', '—'))
            level = ev.get('level', 'INFO')
            event_name = ev.get('event', ev.get('raw', ''))
            extra = {k:v for k,v in ev.items() if k not in {'ts','level','event','raw'}}
            extra_str = ', '.join(f"{k}={v}" for k,v in extra.items()) if extra else ''
            rows.append(f"<tr><td>{ts}</td><td class='level-{level}'>{level}</td><td>{event_name}</td><td style='white-space:nowrap'>{extra_str}</td></tr>")
        table_html = """
        <table class='events-table'>
            <thead><tr><th>Timestamp (UTC)</th><th>Nivel</th><th>Evento</th><th>Extra</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """.replace('{rows}', ''.join(rows))
        st.markdown(table_html, unsafe_allow_html=True)

# =====================================================
# 🏥 PANEL DE DIAGNÓSTICO (Health Check)
# =====================================================
with st.sidebar.expander("🏥 Diagnóstico del Sistema", expanded=False):
    if st.button("🔄 Actualizar Health", key="refresh_health"):
        st.session_state['_health_refresh'] = datetime.utcnow().isoformat()

    try:
        import json, subprocess, os
        health_script = os.path.join(BASE, "health.py")
        if not os.path.isfile(health_script):
            st.error("health.py no encontrado en el directorio base")
        else:
            # Ejecutar script con ruta absoluta para evitar WinError 123 por cwd/relativo
            result = subprocess.run(
                [sys.executable, health_script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                try:
                    health_data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    st.error("Salida inválida de health.py (no es JSON)")
                    st.code(result.stdout[:500])
                else:
                    # Métricas clave
                    st.metric("🐍 Python", health_data.get('python_version', 'N/A'))
                    st.metric("💾 Memoria Proceso", f"{health_data.get('process_memory_bytes', 0) / (1024**2):.1f} MB")

                    disk = health_data.get('disk', {})
                    disk_pct = disk.get('percent', 0)
                    if disk_pct > 90:
                        st.error(f"💿 Disco: {disk_pct:.1f}% usado")
                    elif disk_pct > 75:
                        st.warning(f"💿 Disco: {disk_pct:.1f}% usado")
                    else:
                        st.success(f"💿 Disco: {disk_pct:.1f}% usado")

                    db = health_data.get('db', {})
                    st.metric("📊 BD Tamaño", f"{db.get('size_bytes', 0) / (1024**2):.2f} MB")
                    st.metric("📋 Tablas BD", db.get('tables', 0))

                    log = health_data.get('log', {})
                    st.metric("📝 Eventos escaneados", log.get('scanned_events', 0))
                    st.metric("⚠️ Errores", log.get('error_events', 0))
                    st.metric("🔀 Mismatches", log.get('mismatch_events', 0))

                    latest_mm = log.get('latest_mismatch')
                    if latest_mm:
                        st.warning(f"⚠️ Último mismatch: {latest_mm.get('ts', 'N/A')[:19]}")
                        with st.expander("Ver detalles"):
                            st.json(latest_mm)
            else:
                st.error("❌ Error ejecutando health.py")
                stderr_trim = (result.stderr or "").strip()[:800]
                if stderr_trim:
                    st.code(stderr_trim)
    except Exception as e:
        st.error(f"❌ Error interno panel health: {e}")


# =====================================================
# 🌓 THEME TOGGLE (Claro/Oscuro)
# =====================================================
theme_choice = st.sidebar.selectbox('Tema', ['Claro','Oscuro'], index=0, key='theme_choice')
if theme_choice == 'Oscuro':
    DARK_CSS = """
    <style>
    body, .stApp { background:#0f172a; color:#f1f5f9; }
    .ar-card { background:#1e293b !important; border:1px solid #334155 !important; }
    .ar-card h4, .ar-card h3 { color:#f1f5f9 !important; }
    .ar-metric-value { color:#f1f5f9 !important; }
    nav { background:#1e293b !important; }
    a { color:#93c5fd !important; }
    </style>
    """
    st.markdown(DARK_CSS, unsafe_allow_html=True)

# Navigation bar
st.markdown("""
<nav style='background:#f8f9fa;padding:8px;border-radius:6px;margin-bottom:12px;'>
  <a href='/?page=Home' style='margin-right:12px;'>🏠 Inicio</a>
  <a href='/?page=plots' style='margin-right:12px;'>🏡 Registro Fincas</a>
  <a href='/?page=architects' style='margin-right:12px;'>🏛️ Arquitectos</a>
  <a href='/?page=constructores' style='margin-right:12px;'>🏗️ Constructores</a>
  <a href='/?page=clientes' style='margin-right:12px;'>👤 Clientes</a>
  <a href='/?page=servicios' style='margin-right:12px;'>⚙️ Servicios</a>
</nav>
""", unsafe_allow_html=True)

# =====================================================
# ⏱️ PANEL RENDIMIENTO (Sidebar)
# =====================================================
import time
class PerfTimer:
    def __init__(self, label):
        self.label = label
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, exc_type, exc, tb):
        duration = (time.perf_counter() - self.start) * 1000
        st.session_state.setdefault('perf_metrics', []).append({'label': self.label, 'ms': duration})

def render_perf_panel():
    metrics = st.session_state.get('perf_metrics', [])
    if not metrics:
        return
    with st.sidebar.expander('⚡ Rendimiento (sesión)', expanded=False):
        total = sum(m['ms'] for m in metrics)
        st.write(f"Total registrado: {total:.0f} ms")
        for m in metrics[-8:]:
            st.write(f"• {m['label']}: {m['ms']:.1f} ms")

render_perf_panel()

# Get current page from query params (robust resolver)
raw_page = st.query_params.get('page', 'Home')
if isinstance(raw_page, list):
    raw_page = raw_page[0]
page = str(raw_page) if raw_page is not None else 'Home'
# Normalize common short values that sometimes appear
norm = page.strip().lower()
if norm in ['home', 'inicio', 'h']:
    page = 'Home'
elif norm in ['plots', 'plot', 'p', 'fincas']:
    page = 'plots'
elif norm in ['architects', 'architect', 'a', 'arquitectos']:
    page = 'architects'
elif norm in ['constructores', 'constructor', 'c']:
    page = 'constructores'
elif norm in ['clientes', 'cliente', 'cl']:
    page = 'clientes'
elif norm in ['servicios', 'servicio', 's']:
    page = 'servicios'
else:
    # leave page as-is if it matches expected values; otherwise default to Home
    if page not in ['Home', 'plots', 'architects', 'constructores', 'clientes', 'servicios']:
        page = 'Home'

if page == 'Home':
    st.title('ARCHIRAPID — Home')
    st.write('Busca fincas con los filtros horizontales y visualízalas en el mapa interactivo.')

    # =====================================================
    # Persistencia robusta de selección de finca
    # =====================================================
    # Si tras un rerun desaparece selected_plot pero tenemos copia, restaurar.
    if 'selected_plot' not in st.session_state and 'selected_plot_persist' in st.session_state:
        st.session_state['selected_plot'] = st.session_state['selected_plot_persist']
    # Mantener copia viva cada ciclo
    if 'selected_plot' in st.session_state:
        st.session_state['selected_plot_persist'] = st.session_state['selected_plot']

    # --- HORIZONTAL FILTERS: 2 rows × 4 columns (Airbnb/Idealista style) ---
    st.subheader("🔍 Filtros de Búsqueda")
    
    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        min_m2 = st.number_input("Min m²", min_value=0, value=0, key="filter_min_m2")
    with col2:
        max_m2 = st.number_input("Max m²", min_value=0, value=100000, key="filter_max_m2")
    with col3:
        type_sel = st.selectbox("Tipo", options=["any", "rural", "urban", "industrial"], key="filter_type")
    with col4:
        province = st.text_input("Provincia", value="", key="filter_province")
    
    # Row 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        min_price = st.number_input("Min precio (€)", min_value=0, value=0, key="filter_min_price")
    with col6:
        max_price = st.number_input("Max precio (€)", min_value=0, value=10000000, key="filter_max_price")
    with col7:
        q = st.text_input("Buscar texto", "", key="filter_search_text")
    with col8:
        st.write("")  # Spacer
    if st.button("📋 Registrar nueva finca", width='stretch'):
            st.query_params.update({"page": "plots"})
            st.rerun()

    st.markdown("---")  # Separator

    # --- MAP + PREVIEW: 50/50 split ---
    df_plots = get_all_plots()
    df = df_plots.copy()
    # Filtrar fincas con coordenadas válidas (lat/lon no nulos y tipo float)
    df = df[df["lat"].apply(lambda x: isinstance(x, (float, int)) and not pd.isnull(x))]
    df = df[df["lon"].apply(lambda x: isinstance(x, (float, int)) and not pd.isnull(x))]
    # Filtrar duplicados por id
    df = df.drop_duplicates(subset=["id"])
    # Aplicar filtros
    if df.shape[0] > 0:
        df = df[(df["m2"] >= min_m2) & (df["m2"] <= max_m2) & (df["price"] >= min_price) & (df["price"] <= max_price)]
        if province.strip() != "":
            df = df[df["province"].str.contains(province, case=False, na=False)]
        if type_sel != "any":
            df = df[df["type"] == type_sel]
        if q.strip() != "":
            df = df[df.apply(lambda row: q.lower() in str(row["title"]).lower() or q.lower() in str(row.get("province","")), axis=1)]

    # build map
    m = folium.Map(location=[40.0, -4.0], zoom_start=6, tiles="CartoDB positron")
    if df.shape[0] > 0:
        for _, r in df.iterrows():
            # small thumbnail in popup
            img_html = ""
            if r.get("image_path") and os.path.exists(r["image_path"]):
                img_b64 = get_image_base64(r["image_path"])
                if img_b64:
                    img_html = f'<img src="{img_b64}" width="160" style="border-radius:8px;display:block;margin:0 auto 6px;"/>'

            popup_html = f"""
            <div style="width:240px;font-family:'Segoe UI',Roboto,sans-serif;background:#fff;border-radius:12px;padding:8px;text-align:center;box-shadow:0 3px 8px rgba(0,0,0,0.15);">
                {img_html}
                <h4 style='margin:6px 0;font-size:15px;color:#004080;'>{r['title']}</h4>
                <div style='font-size:13px;color:#444;'><b>{int(r.get('m2',0)):,} m²</b> · €{int(r.get('price',0)):,}</div>
                <div style='font-size:12px;color:#666;margin-top:4px;'>📍 {r.get('province','')} {r.get('locality','')}</div>
                <div style='font-size:11px;color:#999;margin-top:8px;'>👉 Haz clic en el marcador para ver detalles completos</div>
            </div>
            """

            folium.Marker(
                location=[r["lat"], r["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=r["title"],
                icon=folium.Icon(color="cadetblue", icon="home", prefix="fa")
            ).add_to(m)

    # --- 50/50 SPLIT: Map (left) + Preview Panel (right) ---
    map_col, panel_col = st.columns([1, 1])
    with map_col:
        st.subheader("🗺️ Mapa Interactivo")
        map_data = st_folium(m, width="100%", height=650, key="folium_map")

    # detect incoming plot_id from URL (robust handling)
    qp = st.query_params
    if "plot_id" in qp:
        plot_id_value = qp["plot_id"]
        if isinstance(plot_id_value, list):
            plot_id_value = plot_id_value[0]
        st.session_state["selected_plot"] = plot_id_value
        # Limpiar parámetro sin forzar rerun (evita perder selección en ciclo siguiente)
        new_qp = {k: v for k, v in qp.items() if k != "plot_id"}
        if len(new_qp) > 0:
            st.query_params.update(new_qp)
        else:
            st.query_params.clear()

    # Detect marker click from map
    if map_data and map_data.get("last_object_clicked") is not None:
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        # Find the plot with these exact coordinates
        for _, r in df.iterrows():
            if abs(r["lat"] - clicked_lat) < 0.0001 and abs(r["lon"] - clicked_lon) < 0.0001:
                st.session_state["selected_plot"] = r["id"]
                break

    # --- RIGHT: detail panel ---
    selected_plot = None
    if "selected_plot" in st.session_state:
        pid = st.session_state["selected_plot"]
        selected_plot = get_plot_by_id(pid)

        # Pre-cálculo análisis edificabilidad (cache) si no existe para esta finca
        if selected_plot:
            from archirapid_extract.compute_edificability import build_report
            try:
                report = build_report()  # usa cache interna
                st.session_state.setdefault('analysis_cache', {})[selected_plot['id']] = report
            except Exception:
                pass

    with panel_col:
        st.subheader("📋 Preview de Finca")
        if selected_plot is None:
            st.info("👈 Selecciona una finca en el mapa para ver detalles rápidos aquí.")
        else:
            st.markdown(f"### {selected_plot.get('title','Detalle finca')}")
            if selected_plot.get("image_path") and os.path.exists(selected_plot["image_path"]):
                st.image(selected_plot["image_path"], width='stretch')
            else:
                st.info("Imagen no disponible")

            st.markdown(f"**{selected_plot.get('description','-')}**")
            st.write(f"**Superficie:** {int(selected_plot.get('m2',0)):,} m²")
            st.write(f"**Precio:** €{int(selected_plot.get('price',0)):,}")
            st.write(f"**Tipo:** {selected_plot.get('type','-')}")
            st.write(f"**Ubicación:** {selected_plot.get('province','-')} / {selected_plot.get('locality','-')}")

            # =====================================================
            # 📄 NOTA CATASTRAL Y ANÁLISIS (antes de opciones pago)
            # =====================================================
            if selected_plot.get("registry_note_path") and os.path.exists(selected_plot.get("registry_note_path")):
                st.markdown("---")
                st.subheader("📄 Documentación Catastral")
                
                with open(selected_plot["registry_note_path"], 'rb') as f:
                    registry_data = f.read()
                st.download_button(
                    "📥 Descargar Nota Simple",
                    data=registry_data,
                    file_name=os.path.basename(selected_plot["registry_note_path"]),
                    mime="application/pdf",
                    width='stretch',
                    type="secondary"
                )

                # Análisis automático
                st.markdown("**🔍 Análisis Inteligente**")
                current_pid = selected_plot.get('id')
                has_cache = bool(st.session_state.get('analysis_cache', {}).get(current_pid))
                
                if has_cache:
                    if st.button("📊 VER RESULTADOS ANÁLISIS", key="view_results", type="primary", width='stretch'):
                        show_analysis_modal(current_pid)
                else:
                    if st.button("🔍 ANALIZAR NOTA CATASTRAL", key="analyze_catastral", type="primary", width='stretch'):
                        st.session_state['trigger_analysis'] = True
                        st.rerun()

            st.markdown("---")
            st.subheader("💰 Opciones de Adquisición")
            
            price = float(selected_plot.get("price", 0))
            
            col_res, col_buy = st.columns(2)
            
            # RESERVAR (10%)
            with col_res:
                amount_reserve = price * 0.10
                st.metric("🔒 Reservar", f"{amount_reserve:,.2f} €", "10% del precio")
                
                if st.button("📝 Reservar Finca", key="btn_reserve", width='stretch'):
                    st.session_state['trigger_reserve_payment'] = True
                    st.rerun()
            
            # COMPRAR (100%)
            with col_buy:
                st.metric("✅ Comprar", f"{price:,.2f} €", "100% del precio")
                
                if st.button("🏡 Comprar Finca", key="btn_buy", width='stretch', type="primary"):
                    st.session_state['trigger_buy_payment'] = True
                    st.rerun()
    
    # =====================================================
    # 🎯 POST-PAGO: CONFIRMACIÓN COMPLETA PARA TODOS
    # =====================================================
    # SALIR del contexto panel_col para renderizar a full width
    if selected_plot and st.session_state.get('payment_completed'):
        from src.payment_simulator import show_payment_success
        
        payment_data = st.session_state.get('last_payment')
        if payment_data:
            from src.payment_flow import finalize_payment
            result = finalize_payment(selected_plot, payment_data, Path(DB_PATH))
            payment_type = result['payment_type']
            
            # === CONFIRMACIÓN COMPLETA CON TODOS LOS DATOS ===
            st.markdown("---")
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<script>window.scrollTo({top:0,behavior:'smooth'});</script>", unsafe_allow_html=True)
            
            # Centrar contenido
            _, center_col, _ = st.columns([1, 3, 1])
            
            with center_col:
                # TÍTULO CON TIPO DE OPERACIÓN
                if payment_type == 'purchase':
                    st.success("🎉 ¡COMPRA COMPLETADA CON ÉXITO!")
                else:
                    st.success("✅ ¡RESERVA COMPLETADA CON ÉXITO!")
                
                st.markdown("---")
                
                # DATOS DE LA FINCA COMPRADA/RESERVADA
                st.markdown("### 🏡 Detalles de tu Finca")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.metric("📍 Ubicación", f"{selected_plot.get('locality', 'N/A')}, {selected_plot.get('province', 'N/A')}")
                    st.metric("📏 Superficie", f"{selected_plot.get('m2', 0):,.0f} m²")
                with col_f2:
                    st.metric("💰 Precio Total", f"{selected_plot.get('price', 0):,.2f} €")
                    if payment_type == 'purchase':
                        st.metric("✅ Pagado", f"{payment_data['amount']:,.2f} €", delta="100%")
                    else:
                        st.metric("💳 Reserva (10%)", f"{payment_data['amount']:,.2f} €")
                
                st.markdown("---")
                
                # RECIBO COMPLETO DEL PAGO
                st.markdown("### 🧾 Recibo de Pago")
                show_payment_success(payment_data, download_receipt=True)
                
                st.markdown("---")
                st.markdown("### 🎯 Próximos Pasos")
                
                if payment_type == 'purchase':
                    st.info("""**¡Tu finca ya es tuya!**\n\nAccede al **Panel de Clientes** para:\n- 🏗️ **Diseñar tu casa** con IA\n- 📦 **Ver proyectos arquitectónicos** compatibles\n- 📋 Recibir propuestas de arquitectos\n- 📊 Descargar análisis catastral completo""")
                else:
                    st.info("""**Tu finca está reservada**\n\nAccede al **Panel de Clientes** para:\n- 📋 Ver propuestas de arquitectos\n- 🏗️ Diseñar tu casa con IA\n- 📦 Explorar proyectos compatibles\n- 📊 Descargar análisis catastral""")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # BOTONES DE ACCIÓN
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("🚀 IR AL PANEL DE CLIENTES", use_container_width=True, type="primary", key="goto_clients"):
                        st.session_state["page"] = "clientes"
                        try:
                            st.query_params.update(page='clientes')
                        except Exception:
                            pass
                        st.session_state["client_email_prefill"] = payment_data.get("buyer_email")
                        st.session_state["auto_login_email"] = payment_data.get("buyer_email")
                        # Guardar datos para mostrar en portal
                        st.session_state['last_payment_receipt'] = payment_data
                        st.session_state['purchased_plot'] = selected_plot
                        # Limpiar flags
                        st.session_state['payment_completed'] = False
                        st.session_state['last_payment'] = None
                        st.rerun()
                with btn_col2:
                    if st.button("🏠 Volver al Inicio", use_container_width=True, key="goto_home"):
                        st.session_state["selected_plot_id"] = None
                        st.session_state['payment_completed'] = False
                        st.session_state['last_payment'] = None
                        st.rerun()
    
    # =====================================================
    # 📋 PREVIEW NORMAL: PROYECTOS Y PROPUESTAS
    # =====================================================
    if selected_plot:
        with panel_col:
            # =====================================================
            # PROYECTOS COMPATIBLES (Matching automático)
            # =====================================================
            st.markdown("---")
            st.markdown("### 🏗️ Proyectos Compatibles con esta Parcela")
            st.caption("Proyectos arquitectónicos que encajan perfectamente con tus m² disponibles")
            
            current_m2 = selected_plot.get('m2', 0)
            current_type = selected_plot.get('type', 'vivienda')
            compatible_projects_df = get_compatible_projects(current_m2, current_type)

            
            if compatible_projects_df.shape[0] == 0:
                st.info("📭 No hay proyectos compatibles disponibles todavía")
            else:
                # Mostrar top 3 proyectos
                top_projects = compatible_projects_df.head(3)
                
                st.success(f"✅ Encontrados {compatible_projects_df.shape[0]} proyecto(s) compatible(s)")
                
                cols_proj = st.columns(3)
                for idx, (col, (_, proj)) in enumerate(zip(cols_proj, top_projects.iterrows())):
                    with col:
                        # Badge de compatibilidad
                        match_score = proj.get('match_score', 0)
                        if match_score == 100:
                            st.success("🎯 MATCH PERFECTO")
                        elif match_score >= 50:
                            st.warning("⚠️ Compatible con ajustes")
                        else:
                            st.info("💡 Requiere adaptación")
                        
                        st.markdown(f"### {proj['title']}")
                        
                        # Foto
                        if proj.get('foto_principal') and os.path.exists(proj['foto_principal']):
                            st.image(proj['foto_principal'], width='stretch')
                        else:
                            st.image("https://via.placeholder.com/300x200?text=Proyecto", width='stretch')
                        
                        # Specs
                        st.metric("m² Construidos", proj.get('m2_construidos', '-'))
                        st.caption(f"🛏️ {proj.get('habitaciones', '?')} hab • 🚿 {proj.get('banos', '?')} baños")
                        st.caption(f"💰 €{int(proj.get('price', 0)):,}")
                        
                        # Rango de parcela
                        if proj.get('m2_parcela_minima') and proj.get('m2_parcela_maxima'):
                            st.caption(f"📐 Parcela: {proj['m2_parcela_minima']}-{proj['m2_parcela_maxima']} m²")
                        
                        # Botón ver detalle
                        if st.button("👁️ Ver Detalles", key=f"view_compat_proj_{proj['id']}", width='stretch'):
                            st.session_state['view_project_id'] = proj['id']
                            st.rerun()
            
            # =====================================================
            # PROPUESTAS RECIBIDAS (Arquitectos → Propietario)
            # =====================================================
            st.markdown("---")
            st.markdown("### 📨 Propuestas de Arquitectos")

            
            # Asegurar variable current_pid definida (ya establecida en sección anterior)
            current_pid_safe = selected_plot.get('id')
            df_proposals = get_proposals_for_plot(current_pid_safe) if current_pid_safe else pd.DataFrame([])
            
            if df_proposals.shape[0] == 0:
                st.info("📭 No has recibido propuestas todavía")
            else:
                st.success(f"✅ Has recibido {df_proposals.shape[0]} propuesta(s)")
                
                for idx, prop in df_proposals.iterrows():
                    status_color = {
                        'pending': '🟡',
                        'accepted': '🟢',
                        'rejected': '🔴'
                    }
                    
                    with st.expander(f"{status_color.get(prop['status'], '📨')} {prop['architect_name']} - {prop['status'].upper()}", expanded=(prop['status']=='pending')):
                        col_arch, col_details = st.columns([1, 2])
                        
                        with col_arch:
                            st.markdown(f"**👤 Arquitecto:** {prop['architect_name']}")
                            if prop.get('architect_company'):
                                st.caption(f"🏢 {prop['architect_company']}")
                            st.caption(f"📧 {prop['architect_email']}")
                        
                        with col_details:
                            st.metric("💰 Presupuesto", f"€{int(prop['estimated_budget']):,}")
                            st.metric("📅 Plazo", f"{prop['deadline_days']} días")
                        
                        st.markdown("**📝 Propuesta:**")
                        st.write(prop['proposal_text'])
                        
                        if prop.get('sketch_image_path') and os.path.exists(prop['sketch_image_path']):
                            st.image(prop['sketch_image_path'], caption="Boceto inicial", width='stretch')
                        
                        st.caption(f"📅 Recibida: {prop['created_at'][:10]}")
                        
                        if prop['status'] == 'pending':
                            col_accept, col_reject = st.columns(2)
                            with col_accept:
                                if st.button("✅ Aceptar Propuesta", key=f"accept_{prop['id']}", type="primary", width='stretch'):
                                    update_proposal_status(prop['id'], 'accepted')
                                    st.success("✅ Propuesta aceptada. El arquitecto será notificado.")
                                    st.rerun()
                            with col_reject:
                                if st.button("❌ Rechazar", key=f"reject_{prop['id']}", width='stretch'):
                                    update_proposal_status(prop['id'], 'rejected')
                                    st.info("Propuesta rechazada.")
                                    st.rerun()
                        elif prop['status'] == 'accepted':
                            st.success("✅ Propuesta aceptada")
                            st.caption(f"Respondida: {prop.get('responded_at', '')[:10]}")
                        else:
                            st.error("❌ Propuesta rechazada")
                
            st.markdown("---")
            if st.button("Close preview"):
                st.session_state.pop("selected_plot", None)
                st.rerun()  # Fixed: removed deprecated experimental_rerun()
    
    # Disparar modales de pago fuera del panel lateral
    if st.session_state.get('trigger_reserve_payment') and selected_plot:
        from src.payment_simulator import payment_modal
        
        amount_reserve = float(selected_plot.get("price", 0)) * 0.10
        concept = f"Reserva finca {selected_plot.get('title', 'Sin título')} - {selected_plot.get('id', '')[:8]}"
        buyer_name = st.session_state.get('client_name', '')
        buyer_email = st.session_state.get('client_email', '')
        
        payment_modal(amount_reserve, concept, buyer_name, buyer_email)
        st.session_state['trigger_reserve_payment'] = False
    
    if st.session_state.get('trigger_buy_payment') and selected_plot:
        from src.payment_simulator import payment_modal
        
        price = float(selected_plot.get("price", 0))
        concept = f"Compra finca {selected_plot.get('title', 'Sin título')} - {selected_plot.get('id', '')[:8]}"
        buyer_name = st.session_state.get('client_name', '')
        buyer_email = st.session_state.get('client_email', '')
        
        payment_modal(price, concept, buyer_name, buyer_email)
        st.session_state['trigger_buy_payment'] = False

    # ============================================================================
    # DISPATCHER: Análisis Catastral
    # ============================================================================
    if st.session_state.get('trigger_analysis'):
        plot_id = st.session_state.get('selected_plot')
        plot = get_plot_by_id(plot_id) if isinstance(plot_id, str) else plot_id
        
        if plot:
            import shutil, subprocess, sys, json
            from pathlib import Path
            
            with st.spinner("🔍 Analizando nota catastral..."):
                try:
                    extract_dir = Path("archirapid_extract")
                    shutil.copy(plot["registry_note_path"], extract_dir / "Catastro.pdf")
                    
                    result = subprocess.run(
                        [sys.executable, "run_pipeline_simple.py"],
                        cwd=str(extract_dir),
                        capture_output=True,
                        text=True,
                        timeout=180,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
                    )
                    
                    if result.returncode == 0:
                        output_dir = extract_dir / "catastro_output"
                        with open(output_dir / "edificability.json", 'r', encoding='utf-8') as f:
                            edata = json.load(f)
                        
                        vdata = None
                        if (output_dir / "validation_report.json").exists():
                            with open(output_dir / "validation_report.json", 'r', encoding='utf-8') as f:
                                vdata = json.load(f)
                        
                        st.session_state.setdefault('analysis_cache', {})
                        st.session_state['analysis_cache'][plot['id']] = {
                            'output_dir': str(output_dir),
                            'edata': edata,
                            'vdata': vdata
                        }
                        
                        st.success("✅ Análisis completado")
                        show_analysis_modal(plot['id'])
                    else:
                        st.error("❌ Error en análisis")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.session_state['trigger_analysis'] = False

    # ============================================================================
    # DISPATCHER: Diseñador 3D
    # ============================================================================
    if st.session_state.get('design_requested'):
        params = st.session_state['design_requested']
        plot_id = params['plot_id']
        design_key = f"design_result_{plot_id}"
        
        if not st.session_state.get(design_key):
            with st.spinner("🏗️ Generando diseño 3D..."):
                try:
                    from archirapid_extract.generate_design import build_project
                    cache = st.session_state.get('analysis_cache', {}).get(plot_id)
                    
                    if cache:
                        res = build_project(
                            catastro_path=cache['output_dir'],
                            output_dir="archirapid_extract/design_output",
                            num_bedrooms=params['bedrooms'],
                            num_floors=params['floors'],
                            setback_m=params['setback']
                        )
                        st.session_state[design_key] = res
                    else:
                        st.session_state[design_key] = {"success": False}
                except Exception as e:
                    st.session_state[design_key] = {"success": False, "error": str(e)}
        
        st.session_state['design_requested'] = None
        st.rerun()

    # ============================================================================
    # DISPATCHER: Envío de Propuesta
    # ============================================================================
    if st.session_state.get('send_proposal_to'):
        plot_id = st.session_state['send_proposal_to']
        arch_id = st.session_state.get('arch_id')
        
        if arch_id:
            show_proposal_modal(plot_id, arch_id)
        else:
            st.warning("⚠️ Debes iniciar sesión como arquitecto")
            st.session_state['send_proposal_to'] = None

elif page == 'plots':
    st.title('Registro y Gestión de Fincas')
    tab = st.radio('Panel:', ['Registrar Nueva Finca', 'Ver Fincas'])
    if tab == 'Registrar Nueva Finca':
        # Radio para propósito de la finca (ANTES del formulario)
        st.markdown("---")
        st.subheader("¿Qué deseas hacer con tu finca?")
        plot_purpose = st.radio(
            "Selecciona tu objetivo principal:",
            ["🏡 Vender la finca", "🏗️ Construir mi casa aquí"],
            help="Si eliges 'Construir', crearemos tu cuenta de cliente automáticamente y podrás recibir propuestas de arquitectos o diseñar tu propia casa con asistencia de IA."
        )
        st.markdown("---")
        
        with st.form('registro_finca'):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input('Título/Nombre de la Finca*')
                province = st.text_input('Provincia*')
                locality = st.text_input('Localidad')
                type_prop = st.selectbox('Tipo*', ['rural','urban','industrial'])
                m2 = st.number_input('Superficie (m²)*', min_value=1, value=100)
            with col2:
                height = st.number_input('Altura máxima (m)', min_value=0.0, value=6.0)
                price = st.number_input('Precio (€)*', min_value=0, value=100000)
                st.markdown('**Coordenadas geográficas**')
                st.caption("Formato admitido: decimal (ej: 36.5123) o grados/minutos/segundos (ej: 36º25'10''). Se convertirán automáticamente.")
                lat_input = st.text_input('Latitud*', value='')
                lon_input = st.text_input('Longitud*', value='')
                owner_name = st.text_input('Nombre del Propietario*')
                owner_email = st.text_input('Email del Propietario*')
            description = st.text_area('Descripción')
            images = st.file_uploader('Imágenes', accept_multiple_files=True, type=['jpg','jpeg','png'])
            registry_note = st.file_uploader('Nota Simple (PDF)', type=['pdf'])
            submitted = st.form_submit_button('Registrar Finca')

            if submitted:
                # Validar coordenadas (soporta N/S/E/W y O=Oeste)
                def gms_to_decimal(coord, is_lon=False):
                    import re
                    # Ejemplo: 36º25'10'' o 36 25 10 o 36°25'10" o 36d25m10s
                    # Intenta múltiples formatos
                    patterns = [
                        r"([\d.]+)[º°d][\s]*(\d+)['\s][\s]*(\d+)[\"s]?",  # 36º 25' 10"
                        r"([\d.]+)[º°d][\s]*(\d+)[\s]*(\d+)",  # 36 25 10
                    ]
                    text = str(coord or '').strip()
                    # Detectar hemisferio o signo explícito
                    hemi = text.upper()
                    sign = 1
                    if '-' in text:
                        sign = -1
                    else:
                        if any(h in hemi for h in ['S']):
                            sign = -1
                        if any(h in hemi for h in ['W','O']):  # O = Oeste
                            sign = -1

                    # Limpiar letras para el parse
                    clean = re.sub(r"[NnSsEeWwOo]", "", text)

                    for pattern in patterns:
                        match = re.search(pattern, clean)
                        if match:
                            deg, min_, sec = map(float, match.groups())
                            return sign * (deg + min_/60 + sec/3600)
                    try:
                        val = float(clean.replace(',', '.').strip())
                        return sign * val
                    except Exception:
                        return None

                lat = gms_to_decimal(lat_input, is_lon=False)
                lon = gms_to_decimal(lon_input, is_lon=True)
                if not all([title, province, m2, price, lat, lon, owner_name, owner_email]):
                    st.error('Campos obligatorios incompletos o coordenadas inválidas')
                else:
                    image_path = None
                    registry_path = None
                    
                    try:
                        # Validar y guardar imagen con límites
                        if images:
                            image_path = save_file(
                                images[0], 
                                prefix='plot',
                                max_size_mb=5,
                                allowed_mime_types=['image/jpeg', 'image/png', 'image/jpg']
                            )
                        
                        # Validar y guardar PDF
                        if registry_note:
                            registry_path = save_file(
                                registry_note, 
                                prefix='registry',
                                max_size_mb=10,
                                allowed_mime_types=['application/pdf']
                            )
                    except ValueError as e:
                        st.error(f'❌ Error en archivo: {str(e)}')
                        st.stop()
                    
                    # Determinar propósito según radio
                    purpose_value = 'construir' if '🏗️' in plot_purpose else 'vender'
                    
                    pdata = {
                        'id': uuid.uuid4().hex,
                        'title': title,
                        'description': description,
                        'lat': lat,
                        'lon': lon,
                        'm2': int(m2),
                        'height': float(height),
                        'price': float(price),
                        'type': type_prop,
                        'province': province,
                        'locality': locality,
                        'owner_name': owner_name,
                        'owner_email': owner_email,
                        'image_path': image_path,
                        'registry_note_path': registry_path,
                        'plot_purpose': purpose_value,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_plot(pdata)
                    
                    # Si eligió "Construir", auto-crear cuenta de cliente
                    if purpose_value == 'construir':
                        from src.client_manager import ClientManager
                        cm = ClientManager(DB_PATH)
                        
                        # Verificar si cliente ya existe
                        existing_client = cm.get_client(email=owner_email)
                        if existing_client:
                            st.success(f'✅ Finca registrada con éxito. Ya tienes cuenta de cliente.')
                            st.info(f"🔐 Puedes acceder al panel de clientes con tu email: {owner_email}")
                        else:
                            # Crear cliente
                            client_data = {
                                'name': owner_name,
                                'email': owner_email,
                                'phone': '',
                                'address': f"{locality}, {province}" if locality else province
                            }
                            success, result = cm.register_client(client_data)
                            if success:
                                st.success(f'✅ Finca registrada y cuenta de cliente creada con éxito!')
                                st.balloons()
                                st.info(f"""
                                **🎉 Tu cuenta está lista**
                                
                                **Email:** {owner_email}
                                
                                **Próximos pasos:**
                                1. 📧 Accede al **Panel de Clientes** con tu email
                                2. 📬 Recibe propuestas de arquitectos para tu proyecto
                                3. 🏗️ O diseña tu propia casa con asistencia de IA
                                
                                **Opciones disponibles:**
                                - 📋 **Recibir propuestas**: Los arquitectos podrán enviarte propuestas para tu finca
                                - 🎨 **Diseñar tu casa**: Usa nuestro diseñador con IA que valida según los datos de tu finca
                                - 📦 **Descargar proyectos**: Filtra proyectos compatibles (m², habitaciones, estilo) y descarga vistas previas
                                """)
                            else:
                                st.warning(f'✅ Finca registrada. ⚠️ Error creando cuenta de cliente: {result}')
                    else:
                        st.success('✅ Finca registrada con éxito para venta')
    else:
        st.title('Fincas Registradas')
        df = get_all_plots()
        # Filtrar duplicados por id y registros válidos
        df = df.drop_duplicates(subset=["id"])
        df = df[df["title"].notnull() & (df["title"] != "")]
        if df.shape[0] == 0:
            st.info('No hay fincas registradas')
        else:
            for idx, r in df.iterrows():
                with st.expander(f"{r['title']} — {r.get('province','')} — {r.get('m2',0)} m²"):
                    if r.get('image_path') and os.path.exists(r['image_path']):
                        st.image(r['image_path'], width=300)
                    st.write(r.get('description',''))
                    if r.get('registry_note_path') and os.path.exists(r['registry_note_path']):
                        # Fixed: proper file handling with context manager
                        with open(r['registry_note_path'],'rb') as f:
                            registry_data = f.read()
                        st.download_button('Descargar Nota Simple', 
                                        data=registry_data,
                                        file_name=os.path.basename(r['registry_note_path']),
                                        mime='application/pdf')

elif page == 'architects':
    st.title('🏛️ Portal de Arquitectos')
    
    # Sistema de tabs para navegación
    if 'arch_id' not in st.session_state:
        # No hay sesión → Mostrar registro/login
        tab = st.radio('', ['🔐 Iniciar Sesión', '📝 Registrarse'], horizontal=True)
        
        if tab == '📝 Registrarse':
            st.subheader("Únete a ARCHIRAPID")
            st.caption("Accede a fincas listas para proyectar y conecta con propietarios")
            
            with st.form('registro_arquitecto'):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input('Nombre completo *')
                    email = st.text_input('Email *')
                    telefono = st.text_input('Teléfono')
                with col2:
                    empresa = st.text_input('Empresa/Estudio')
                    nif = st.text_input('NIF/CIF *')
                    colegiado = st.text_input('Nº Colegiado (opcional)')
                
                acepto_terminos = st.checkbox('Acepto los términos y condiciones')
                submitted = st.form_submit_button('✅ Registrarse', width='stretch')
                
                if submitted:
                    if not nombre or not email or not nif:
                        st.error('⚠️ Nombre, email y NIF son obligatorios')
                    elif not acepto_terminos:
                        st.error('⚠️ Debes aceptar los términos y condiciones')
                    else:
                        # Crear arquitecto
                        arch_id = str(uuid.uuid4())
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        try:
                            c.execute('''INSERT INTO architects (id, name, email, phone, company, nif, created_at)
                                         VALUES (?,?,?,?,?,?,?)''', 
                                      (arch_id, nombre, email, telefono, empresa, nif, datetime.now().isoformat()))
                            conn.commit()
                            st.success(f'✅ Registro completado. Bienvenido/a, {nombre}!')
                            st.session_state['arch_id'] = arch_id
                            st.session_state['arch_name'] = nombre
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error('❌ Este email ya está registrado')
                        finally:
                            conn.close()
        
        else:  # Iniciar Sesión
            st.subheader("Accede a tu cuenta")
            email_login = st.text_input('📧 Email registrado')
            if st.button('🔓 Iniciar Sesión', width='stretch'):
                if email_login:
                    conn = sqlite3.connect(DB_PATH)
                    df = pd.read_sql_query("SELECT * FROM architects WHERE email = ?", conn, params=(email_login,))
                    conn.close()
                    
                    if df.shape[0] > 0:
                        arch = df.iloc[0].to_dict()
                        st.success(f"✅ Bienvenido/a, {arch['name']}")
                        st.session_state['arch_id'] = arch['id']
                        st.session_state['arch_name'] = arch['name']
                        st.rerun()
                    else:
                        st.error('❌ Email no encontrado. ¿Necesitas registrarte?')
                else:
                    st.warning('⚠️ Introduce tu email')
    
    else:
        # ARQUITECTO LOGUEADO → Dashboard principal
        arch_id = st.session_state['arch_id']
        arch_name = st.session_state.get('arch_name', 'Arquitecto')
        
        # Load architect full data
        conn = sqlite3.connect(DB_PATH)
        df_arch = pd.read_sql_query("SELECT * FROM architects WHERE id = ?", conn, params=(arch_id,))
        conn.close()
        arch = df_arch.iloc[0].to_dict() if df_arch.shape[0] > 0 else {'name': arch_name, 'email': ''}
        
        # Obtener suscripción activa
        subscription = get_architect_subscription(arch_id)
        
        # Si hay flag de refresh, asegurarse de recargar
        if st.session_state.get('subscription_refresh'):
            del st.session_state['subscription_refresh']
            subscription = get_architect_subscription(arch_id)  # Recargar explícitamente
        
        # Header con nombre y cerrar sesión
        col_name, col_logout = st.columns([3, 1])
        with col_name:
            st.header(f"👋 Hola, {arch_name}")
        with col_logout:
            if st.button('🚪 Cerrar Sesión'):
                del st.session_state['arch_id']
                del st.session_state['arch_name']
                st.rerun()
        
        st.markdown("---")
        
        # ============================================================================
        # PROCESAR PAGO EXITOSO (ANTES DE TABS - CRÍTICO)
        # ============================================================================
        if st.session_state.get('payment_completed'):
            pending = st.session_state.get('pending_subscription')
            last_payment = st.session_state.get('last_payment')
            
            if pending and last_payment:
                # Show success message
                st.success(f"🎉 ¡Pago confirmado! Plan {pending['plan_name']} activado")
                show_payment_success(last_payment, download_receipt=True)
                
                # Create subscription in DB
                sub_id = str(uuid.uuid4())
                from datetime import datetime, timedelta
                start = datetime.now()
                end = start + timedelta(days=30)
                
                # Cancel previous subscription if exists
                existing_sub = get_architect_subscription(pending['architect_id'])
                if existing_sub:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("UPDATE subscriptions SET status = 'cancelled' WHERE id = ?", (existing_sub['id'],))
                    conn.commit()
                    conn.close()
                
                # Insert new subscription
                insert_subscription({
                    'id': sub_id,
                    'architect_id': pending['architect_id'],
                    'plan_type': pending['plan_name'],
                    'price': pending['plan_data']['price'],
                    'monthly_proposals_limit': pending['plan_data']['proposals_limit'],
                    'commission_rate': pending['plan_data']['commission'],
                    'status': 'active',
                    'start_date': start.isoformat(),
                    'end_date': end.isoformat(),
                    'created_at': start.isoformat()
                })
                
                # CRÍTICO: Recargar subscription en session_state para que esté disponible
                st.session_state['subscription_refresh'] = True
                
                st.success("✅ Plan activado correctamente")
                st.info("📂 Abriendo tu panel de proyectos...")
                
                # IMPORTANTE: Limpiar flags ANTES de rerun
                st.session_state['payment_completed'] = False
                st.session_state['trigger_plan_payment'] = False
                st.session_state['pending_subscription'] = None
                st.session_state['last_payment'] = None
                st.session_state['default_arch_tab'] = '📂 Mis Proyectos'
                
                # Forzar rerun INMEDIATO (sin sleep que bloquea)
                st.rerun()
        
        # ============================================================================
        # NAVEGACIÓN TABS
        # ============================================================================
        # Navegación interna del arquitecto
        tabs_options = ['📊 Mi Suscripción', '📂 Mis Proyectos', '🏡 Fincas Disponibles', '📨 Mis Propuestas']
        default_tab = st.session_state.get('default_arch_tab', '📊 Mi Suscripción')
        try:
            default_index = tabs_options.index(default_tab)
        except:
            default_index = 0
        
        arch_tab = st.radio('', tabs_options, horizontal=True, index=default_index, key='arch_tab_radio')
        
        # ============================================================================
        # CONTENIDO TABS
        # ============================================================================
        
        if arch_tab == '📊 Mi Suscripción':
            st.subheader("💎 Planes de Suscripción")
            
            if subscription:
                # Ya tiene suscripción activa
                st.success(f"✅ Plan activo: **{subscription['plan_type']}**")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 Precio Mensual", f"{subscription['price']}€")
                with col2:
                    st.metric("📤 Propuestas/Mes", subscription['monthly_proposals_limit'])
                with col3:
                    proposals_sent = get_proposals_sent_this_month(arch_id)
                    remaining = max(0, subscription['monthly_proposals_limit'] - proposals_sent)
                    st.metric("📊 Disponibles", f"{remaining}/{subscription['monthly_proposals_limit']}")
                with col4:
                    st.metric("💸 Comisión", f"{subscription['commission_rate']*100:.0f}%")
                
                st.caption(f"📅 Fecha inicio: {subscription['start_date'][:10]}")
                
                st.markdown("---")
                st.markdown("### 🔄 Cambiar Plan")
            
            # Mostrar todos los planes
            plans = get_subscription_plans()
            cols = st.columns(3)
            
            for i, (plan_name, plan_data) in enumerate(plans.items()):
                with cols[i]:
                    is_current = subscription and subscription['plan_type'] == plan_name
                    
                    if is_current:
                        st.success(f"### ✅ {plan_name}")
                    else:
                        st.info(f"### {plan_name}")
                    
                    st.metric("Precio", f"{plan_data['price']}€/mes")
                    st.write("**Incluye:**")
                    for feature in plan_data['features']:
                        st.write(f"• {feature}")
                    
                    if not is_current:
                        if st.button(f"💳 Contratar {plan_name}", key=f"sub_{plan_name}", width='stretch'):
                            # Trigger payment modal
                            st.session_state['pending_subscription'] = {
                                'plan_name': plan_name,
                                'plan_data': plan_data,
                                'architect_id': arch_id
                            }
                            st.session_state['trigger_plan_payment'] = True
                            st.rerun()
                    else:
                        st.caption("✓ Plan actual")
            
            # Payment modal dispatcher (outside cards loop)
            # CRITICAL: Solo mostrar modal si NO se ha completado el pago
            should_show_modal = (
                st.session_state.get('trigger_plan_payment', False) and 
                not st.session_state.get('payment_completed', False)
            )
            
            if should_show_modal:
                pending = st.session_state.get('pending_subscription')
                if pending:
                    payment_modal(
                        amount=pending['plan_data']['price'],
                        concept=f"Suscripción Plan {pending['plan_name']} - 1 mes",
                        buyer_name=arch['name'],
                        buyer_email=arch['email']
                    )
                # IMPORTANTE: No poner stop() aquí, dejar que fluya
        
        elif arch_tab == '📂 Mis Proyectos':
            # Clear default tab flag (llegamos al destino correcto)
            if 'default_arch_tab' in st.session_state:
                del st.session_state['default_arch_tab']
            
            st.subheader("🏗️ Portfolio de Proyectos")
            
            # DEBUG: Mostrar estado subscription
            if st.session_state.get('subscription_refresh'):
                st.info(f"🔄 Subscription recargada: {subscription is not None}")
            
            # Check subscription
            if not subscription:
                st.warning("⚠️ Necesitas una suscripción activa para gestionar tu portfolio")
                st.info("👈 Ve a 'Mi Suscripción' y elige un plan")
            else:
                # Header con botón crear
                col_h1, col_h2 = st.columns([3, 1])
                with col_h1:
                    st.caption(f"Gestiona tu catálogo de proyectos para enviar propuestas profesionales")
                with col_h2:
                    if st.button("➕ Nuevo Proyecto", type="primary", width='stretch'):
                        st.session_state['show_project_modal'] = True
                        st.rerun()
                
                # Get existing projects
                projects_df = get_architect_projects(arch_id)
                
                if projects_df.shape[0] == 0:
                    st.info("📂 Aún no has subido proyectos. ¡Comienza tu portfolio!")
                    st.markdown("""
                    **¿Por qué subir proyectos?**
                    - Envía propuestas profesionales con renders y planos
                    - Aparece en búsquedas de compatibilidad automática
                    - Aumenta tu confianza con propietarios
                    - Matching inteligente con fincas disponibles
                    """)
                else:
                    # Grid de proyectos (3 columnas)
                    st.markdown(f"**{projects_df.shape[0]} proyecto(s) en tu portfolio**")
                    
                    for idx in range(0, len(projects_df), 3):
                        cols = st.columns(3)
                        for col_idx, col in enumerate(cols):
                            if idx + col_idx < len(projects_df):
                                proj = projects_df.iloc[idx + col_idx]
                                with col:
                                    # Card del proyecto
                                    st.markdown(f"### {proj['title']}")
                                    
                                    # Mostrar foto principal si existe
                                    if proj.get('foto_principal') and os.path.exists(proj['foto_principal']):
                                        st.image(proj['foto_principal'], width='stretch')
                                    else:
                                        st.image("https://via.placeholder.com/300x200?text=Sin+Imagen", width='stretch')
                                    
                                    # Specs
                                    spec_cols = st.columns(2)
                                    with spec_cols[0]:
                                        st.metric("m² Construidos", proj.get('m2_construidos', '-'))
                                        st.caption(f"💰 {proj.get('price', 0):,.0f}€")
                                    with spec_cols[1]:
                                        st.metric("🛏️ Hab", proj.get('habitaciones', '-'))
                                        st.caption(f"📐 {proj.get('plantas', '-')} plantas")
                                    
                                    # Acciones
                                    act_col1, act_col2 = st.columns(2)
                                    with act_col1:
                                        if st.button("👁️ Ver", key=f"view_proj_{proj['id']}", width='stretch'):
                                            st.session_state['view_project_id'] = proj['id']
                                            st.rerun()
                                    with act_col2:
                                        if st.button("🗑️", key=f"del_proj_{proj['id']}", help="Eliminar"):
                                            delete_project(proj['id'])
                                            st.success("✅ Proyecto eliminado")
                                            st.rerun()
                
                # Modal crear proyecto
                if st.session_state.get('show_project_modal'):
                    show_create_project_modal(arch_id, arch_name)
                
                # Modal ver proyecto
                if st.session_state.get('view_project_id'):
                    project_data = get_project_by_id(st.session_state['view_project_id'])
                    if project_data:
                        show_project_detail_modal(project_data)



        
        elif arch_tab == '🏡 Fincas Disponibles':
            if not subscription:
                st.warning("⚠️ Necesitas una suscripción activa para ver fincas disponibles")
                st.info("👈 Ve a 'Mi Suscripción' y elige un plan")
            else:
                st.subheader("Fincas Listas para Proyectar")
                
                # Filtros
                fcol1, fcol2, fcol3, fcol4 = st.columns(4)
                with fcol1:
                    filter_province = st.text_input("🗺️ Provincia", "", key="arch_filter_prov")
                with fcol2:
                    filter_type = st.selectbox("🏗️ Tipo", ["Todas", "urban", "rural", "industrial"], key="arch_filter_type")
                with fcol3:
                    filter_min_m2 = st.number_input("📏 Min m²", 0, value=0, key="arch_filter_min")
                with fcol4:
                    filter_max_price = st.number_input("💰 Max €", 0, value=1000000, key="arch_filter_max")
                
                # Obtener fincas
                df_plots = get_all_plots()
                
                # Aplicar filtros
                if filter_province:
                    df_plots = df_plots[df_plots['province'].str.contains(filter_province, case=False, na=False)]
                if filter_type != "Todas":
                    df_plots = df_plots[df_plots['type'] == filter_type]
                df_plots = df_plots[df_plots['m2'] >= filter_min_m2]
                df_plots = df_plots[df_plots['price'] <= filter_max_price]
                
                # Límite para plan BÁSICO
                if subscription['plan_type'] == 'BÁSICO':
                    df_plots = df_plots[df_plots['m2'] <= 500]
                    st.caption("ℹ️ Plan BÁSICO: solo fincas hasta 500m². Actualiza a PRO para ver todas.")
                
                st.markdown(f"**{df_plots.shape[0]} fincas encontradas**")
                
                # Mostrar fincas en cards
                for idx, row in df_plots.iterrows():
                    with st.expander(f"🏡 {row['title']} - {row['province']}", expanded=False):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            if row.get('image_path') and os.path.exists(row['image_path']):
                                st.image(row['image_path'], width=200)
                        with c2:
                            st.write(f"**📏 Superficie:** {int(row['m2']):,} m²")
                            st.write(f"**💰 Precio:** €{int(row['price']):,}")
                            st.write(f"**🏗️ Tipo:** {row['type'].upper()}")
                            st.write(f"**📍 Ubicación:** {row['locality']}, {row['province']}")
                            
                            # Botón enviar propuesta
                            if st.button(f"📨 Enviar Propuesta", key=f"prop_{row['id']}"):
                                st.session_state['send_proposal_to'] = row['id']
                                st.rerun()
        
        else:  # Mis Propuestas
            st.subheader("📨 Propuestas Enviadas")
            
            conn = sqlite3.connect(DB_PATH)
            df_props = pd.read_sql_query("""
                SELECT p.*, pl.title as plot_title, pl.province, pl.price as plot_price
                FROM proposals p
                LEFT JOIN plots pl ON p.plot_id = pl.id
                WHERE p.architect_id = ?
                ORDER BY p.created_at DESC
            """, conn, params=(arch_id,))
            conn.close()
            
            if df_props.shape[0] == 0:
                st.info("📭 No has enviado propuestas todavía")
            else:
                for idx, prop in df_props.iterrows():
                    status_emoji = {"pending": "⏳", "accepted": "✅", "rejected": "❌"}
                    with st.expander(f"{status_emoji.get(prop['status'], '📨')} {prop['plot_title']} - {prop['status'].upper()}", expanded=False):
                        st.write(f"**📍 Finca:** {prop['plot_title']}, {prop['province']}")
                        st.write(f"**💰 Presupuesto:** €{int(prop['estimated_budget']):,}")
                        st.write(f"**📅 Plazo:** {prop['deadline_days']} días")
                        st.write(f"**📝 Propuesta:**")
                        st.write(prop['proposal_text'])
                        st.caption(f"Enviada: {prop['created_at'][:10]}")
                        
                        if prop['status'] != 'pending':
                            st.caption(f"Respondida: {prop.get('responded_at', '')[:10] if prop.get('responded_at') else 'N/A'}")

elif page == 'clientes':
    from src.client_manager import ClientManager
    client_manager = ClientManager(DB_PATH)
    
    st.title('🎯 Portal de Clientes')
    st.markdown("Accede a tu cuenta o regístrate para buscar tu finca ideal y diseñar tu casa.")
    
    # AUTO-LOGIN si viene de pago con email
    auto_login_email = st.session_state.get('auto_login_email')
    if auto_login_email and 'client_id' not in st.session_state:
        # Buscar cliente por email
        conn_auto = sqlite3.connect(DB_PATH)
        df_client = pd.read_sql_query("SELECT * FROM clients WHERE email = ? LIMIT 1", conn_auto, params=(auto_login_email,))
        conn_auto.close()
        
        if df_client.shape[0] > 0:
            client_data = df_client.iloc[0].to_dict()
            st.session_state['client_id'] = client_data['id']
            st.session_state['client_name'] = client_data['name']
            st.session_state['client_email'] = client_data['email']
            # Limpiar flag para evitar auto-login repetido
            st.session_state.pop('auto_login_email', None)
            st.success(f"✅ ¡Bienvenido/a {client_data['name']}!")
            st.rerun()
    
    # Mostrar resumen de compra/reserva si existe
    if st.session_state.get('last_payment_receipt') and st.session_state.get('purchased_plot'):
        payment_receipt = st.session_state['last_payment_receipt']
        plot_data = st.session_state['purchased_plot']
        
        st.markdown('---')
        st.success("🎉 ¡Operación completada con éxito!")
        
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            st.markdown(f"### 🏡 {plot_data.get('title', 'Tu Finca')}")
            st.write(f"**📍 Ubicación:** {plot_data.get('locality', 'N/A')}, {plot_data.get('province', 'N/A')}")
            st.write(f"**📏 Superficie:** {plot_data.get('m2', 0):,.0f} m²")
            st.write(f"**💰 Precio:** {plot_data.get('price', 0):,.2f} €")
        with col_s2:
            st.metric("💳 Pagado", f"{payment_receipt['amount']:,.2f} €")
            st.caption(f"Transacción: {payment_receipt['payment_id'][:12].upper()}")
        
        st.markdown("---")
        st.markdown("### 🎯 ¿Qué quieres hacer ahora?")
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("🏗️ DISEÑAR MI CASA CON IA", use_container_width=True, type="primary", key="design_house"):
                st.session_state['action_design_house'] = True
                st.info("🚧 Funcionalidad de diseño con IA próximamente disponible")
        with action_col2:
            if st.button("📦 VER PROYECTOS COMPATIBLES", use_container_width=True, key="view_projects"):
                st.session_state['action_view_projects'] = True
                st.info("🚧 Búsqueda de proyectos arquitectónicos próximamente disponible")
        
        # Botón para ocultar resumen
        if st.button("❌ Ocultar resumen", key="hide_summary"):
            st.session_state.pop('last_payment_receipt', None)
            st.session_state.pop('purchased_plot', None)
            st.session_state.pop('receipt_shown_in_client_panel', None)
            st.rerun()
        
        st.markdown('---')
    
    # Contador de clientes para info
    conn_check = sqlite3.connect(DB_PATH)
    total_clients = pd.read_sql_query("SELECT COUNT(*) as total FROM clients", conn_check).iloc[0]['total']
    conn_check.close()
    
    st.caption(f"👥 {total_clients} clientes registrados en ARCHIRAPID")
    
    # ⚡ UX FIX: Ocultar "Mi Panel" si no hay sesión activa
    is_logged_in = 'client_id' in st.session_state
    
    if is_logged_in:
        tab_options = ['🔑 Acceso', '📝 Registro', '📊 Mi Panel']
    else:
        tab_options = ['🔑 Acceso', '📝 Registro']
    
    tab = st.radio('Seleccione una opción:', tab_options, horizontal=True)
    
    if tab == '📝 Registro':
        st.subheader('Crear nueva cuenta')
        with st.form('registro_cliente_form'):
            nombre = st.text_input('Nombre completo*')
            email = st.text_input('Email*')
            telefono = st.text_input('Teléfono')
            direccion = st.text_input('Dirección')
            submitted = st.form_submit_button('Registrar')
            
            if submitted:
                if not nombre or not email:
                    st.error('Nombre y email son obligatorios')
                else:
                    success, result = client_manager.register_client({
                        'name': nombre,
                        'email': email,
                        'phone': telefono,
                        'address': direccion
                    })
                    if success:
                        st.success('✅ ¡Registro completado con éxito!')
                        st.session_state['client_id'] = result
                        st.session_state['client_name'] = nombre
                        st.info(f'Tu ID de cliente: {result[:8]}...')
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f'❌ Error: {result}')
    
    elif tab == '🔑 Acceso':
        st.subheader('Iniciar sesión')
        st.info("💡 Si es tu primera vez, ve a la pestaña '📝 Registro' primero")
        
        # Auto-login si viene de pago
        prefilled_email = st.session_state.get('client_email_prefill', '')
        if prefilled_email and 'client_id' not in st.session_state:
            client = client_manager.get_client(email=prefilled_email)
            if client:
                st.session_state['client_id'] = client['id']
                st.session_state['client_name'] = client['name']
                st.session_state.pop('client_email_prefill', None)  # Limpiar
                st.success(f"✅ Sesión iniciada automáticamente: {client['name']}")
                time.sleep(1)
                st.rerun()
        
        email_login = st.text_input('Email registrado', key='client_login_email', placeholder="ejemplo@email.com", value=prefilled_email)
        if st.button('🔓 Acceder', key='client_login_btn'):
            if email_login:
                client = client_manager.get_client(email=email_login)
                if client:
                    st.success(f"✅ Bienvenido/a, {client['name']}")
                    st.session_state['client_id'] = client['id']
                    st.session_state['client_name'] = client['name']
                    st.balloons()
                    time.sleep(1)
                    # Forzar recarga para mostrar el panel
                    st.rerun()
                else:
                    st.error('❌ Email no encontrado en nuestra base de datos')
                    st.warning('⚠️ ¿Primera vez aquí? Ve a la pestaña "📝 Registro" para crear tu cuenta')
            else:
                st.warning('⚠️ Introduce tu email')
    
    else:  # Mi Panel
        if 'client_id' not in st.session_state:
            st.warning('⚠️ Debes iniciar sesión primero')
        else:
            client = client_manager.get_client(client_id=st.session_state['client_id'])
            if not client:
                st.error('Error al cargar los datos')
            else:
                st.header(f"👋 Hola, {client['name']}")
                
                # Cerrar sesión
                col_logout1, col_logout2 = st.columns([4, 1])
                with col_logout2:
                    if st.button('🚪 Cerrar Sesión', key='client_logout'):
                        del st.session_state['client_id']
                        del st.session_state['client_name']
                        st.rerun()
                
                st.markdown('---')
                
                # Tabs del panel cliente
                client_tab = st.radio('', ['📊 Mi Perfil', '📨 Propuestas Recibidas', '🗺️ Buscar Fincas'], horizontal=True, key='client_tab_radio')
                
                if client_tab == '📊 Mi Perfil':
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📧 **Email:** {client['email']}")
                        if client.get('phone'):
                            st.info(f"📱 **Teléfono:** {client['phone']}")
                    
                    with col2:
                        st.success('✅ **Estado:** Cuenta Activa')
                        st.metric('Fincas Guardadas', 0)  # Placeholder para futuro
                    
                    st.markdown('---')
                    st.subheader('🚀 Acciones Rápidas')
                    
                    acol1, acol2, acol3 = st.columns(3)
                    with acol1:
                        if st.button('🗺️ Ver Mapa Fincas', width='stretch'):
                            st.query_params.update(page='Home')
                            st.rerun()
                    
                    with acol2:
                        if st.button('📨 Mis Propuestas', width='stretch'):
                            st.session_state['client_tab_default'] = '📨 Propuestas Recibidas'
                            st.rerun()
                    
                    with acol3:
                        if st.button('🤖 Diseñar con IA', width='stretch'):
                            st.info('Selecciona primero una finca en el mapa')
                
                elif client_tab == '📨 Propuestas Recibidas':
                    st.subheader('📬 Propuestas de Arquitectos')
                    
                    # Obtener propuestas del cliente
                    proposals_df = get_client_proposals(client['email'])
                    
                    if proposals_df.shape[0] == 0:
                        st.info('📭 Aún no has recibido propuestas de arquitectos')
                        st.caption('💡 Publica una finca en el mapa para que arquitectos te envíen diseños')
                    else:
                        # Filtros
                        filter_status = st.selectbox('Filtrar por estado:', ['Todas', 'Pendientes', 'Aceptadas', 'Rechazadas'])
                        
                        if filter_status != 'Todas':
                            status_map = {'Pendientes': 'pending', 'Aceptadas': 'accepted', 'Rechazadas': 'rejected'}
                            proposals_df = proposals_df[proposals_df['status'] == status_map[filter_status]]
                        
                        st.caption(f"📊 {len(proposals_df)} propuestas encontradas")
                        
                        # Mostrar propuestas en cards
                        for idx, prop in proposals_df.iterrows():
                            with st.container():
                                st.markdown("---")
                                
                                # Header con foto de proyecto y datos básicos
                                pcol1, pcol2 = st.columns([1, 2])
                                
                                with pcol1:
                                    if prop.get('project_photo') and pd.notna(prop['project_photo']) and os.path.exists(prop['project_photo']):
                                        st.image(prop['project_photo'], width='stretch', caption=prop.get('project_title', 'Proyecto'))
                                    else:
                                        st.image('https://via.placeholder.com/300x200?text=Proyecto', width='stretch')
                                
                                with pcol2:
                                    # Título y arquitecto
                                    if prop.get('project_title'):
                                        st.markdown(f"### 🏛️ {prop['project_title']}")
                                    else:
                                        st.markdown(f"### ✍️ Propuesta Personalizada")
                                    
                                    st.caption(f"👤 Arquitecto: **{prop['architect_name']}**")
                                    if prop.get('architect_company'):
                                        st.caption(f"🏢 {prop['architect_company']}")
                                    
                                    # Finca asociada
                                    st.caption(f"📍 Para tu finca: **{prop['plot_title']}** ({prop['plot_province']}, {int(prop['plot_m2']):,} m²)")
                                    
                                    # Estado
                                    status_emoji = {'pending': '⏳', 'accepted': '✅', 'rejected': '❌'}
                                    status_text = {'pending': 'Pendiente', 'accepted': 'Aceptada', 'rejected': 'Rechazada'}
                                    status_color = {'pending': 'orange', 'accepted': 'green', 'rejected': 'red'}
                                    
                                    st.markdown(f"**Estado:** :{status_color[prop['status']]}[{status_emoji[prop['status']]} {status_text[prop['status']]}]")
                                
                                # Detalles técnicos y económicos
                                st.markdown("#### 📋 Detalles de la Propuesta")
                                
                                dcol1, dcol2, dcol3, dcol4 = st.columns(4)
                                
                                with dcol1:
                                    if prop.get('project_m2'):
                                        st.metric("🏠 m² Construidos", f"{int(prop['project_m2']):,}")
                                    else:
                                        st.metric("🏠 m² Estimados", "-")
                                
                                with dcol2:
                                    if prop.get('project_rooms'):
                                        st.metric("🛏️ Habitaciones", int(prop['project_rooms']))
                                    else:
                                        st.metric("🛏️ Habitaciones", "-")
                                
                                with dcol3:
                                    st.metric("📅 Plazo Entrega", f"{prop['deadline_days']} días")
                                
                                with dcol4:
                                    st.metric("💰 TOTAL", f"€{prop['total_cliente']:,.0f}", help="Precio final incluyendo todos los servicios")
                                
                                # Desglose económico
                                with st.expander("💵 Ver desglose económico"):
                                    st.caption(f"**Proyecto base:** €{prop['estimated_budget']:,.0f}")
                                    st.caption(f"**Formato entrega:** {prop['delivery_format']} (+€{prop['delivery_price']:,.0f})")
                                    if prop['supervision_fee'] > 0:
                                        st.caption(f"**Dirección de Obra:** +€{prop['supervision_fee']:,.0f}")
                                    if prop['visa_fee'] > 0:
                                        st.caption(f"**Visado Colegial:** +€{prop['visa_fee']:,.0f}")
                                    st.caption(f"**Comisión plataforma:** +€{prop['commission']:,.0f}")
                                    st.markdown(f"**TOTAL CLIENTE:** €{prop['total_cliente']:,.0f}")
                                
                                # Mensaje del arquitecto
                                with st.expander("💬 Leer mensaje del arquitecto"):
                                    st.write(prop['proposal_text'])
                                
                                # Botones de acción (solo si está pendiente)
                                if prop['status'] == 'pending':
                                    bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
                                    
                                    with bcol1:
                                        if st.button(f"✅ Aceptar", key=f"client_accept_{prop['id']}", type="primary", width='stretch'):
                                            update_proposal_status(prop['id'], 'accepted')
                                            st.session_state['pending_payment_proposal'] = prop['id']
                                            st.success("✅ Propuesta aceptada. Procede al pago...")
                                            st.rerun()
                                    
                                    with bcol2:
                                        if st.button(f"❌ Rechazar", key=f"client_reject_{prop['id']}", width='stretch'):
                                            update_proposal_status(prop['id'], 'rejected')
                                            st.success("Propuesta rechazada")
                                            st.rerun()
                                
                                elif prop['status'] == 'accepted':
                                    st.success("✅ Propuesta aceptada - Proyecto en curso")
                                
                                elif prop['status'] == 'rejected':
                                    st.error("❌ Propuesta rechazada")
                        
                        # Modal de pago si hay propuesta pendiente de pago
                        if st.session_state.get('pending_payment_proposal'):
                            from src.payment_simulator import payment_modal
                            
                            # Obtener datos de la propuesta
                            pending_prop_id = st.session_state['pending_payment_proposal']
                            pending_prop = proposals_df[proposals_df['id'] == pending_prop_id].iloc[0] if pending_prop_id in proposals_df['id'].values else None
                            
                            if pending_prop is not None:
                                payment_modal(
                                    amount=pending_prop['total_cliente'],
                                    concept=f"Proyecto arquitectónico - {pending_prop.get('project_title', 'Propuesta personalizada')}",
                                    buyer_name=client['name'],
                                    buyer_email=client['email']
                                )
                                
                                # Si el pago se completó
                                if st.session_state.get('payment_completed'):
                                    from src.payment_simulator import show_payment_success
                                    
                                    st.success("🎉 ¡Pago procesado exitosamente!")
                                    show_payment_success(st.session_state.get('last_payment'), download_receipt=True)
                                    
                                    # Registrar pago en BD
                                    payment_id = str(uuid.uuid4())
                                    conn = sqlite3.connect(DB_PATH)
                                    c = conn.cursor()
                                    c.execute('''INSERT INTO payments (
                                        id, proposal_id, client_id, amount, payment_method, card_last4, 
                                        status, transaction_id, created_at
                                    ) VALUES (?,?,?,?,?,?,?,?,?)''', (
                                        payment_id,
                                        pending_prop_id,
                                        client['id'],
                                        pending_prop['total_cliente'],
                                        st.session_state['last_payment'].get('method', 'Tarjeta'),
                                        st.session_state['last_payment'].get('card_last4', '1111'),
                                        'completed',
                                        st.session_state['last_payment']['payment_id'],
                                        datetime.now().isoformat()
                                    ))
                                    conn.commit()
                                    
                                    # Registrar comisión para el arquitecto
                                    commission_id = str(uuid.uuid4())
                                    c.execute('''INSERT INTO commissions (
                                        id, proposal_id, architect_id, client_id, amount, paid, created_at
                                    ) VALUES (?,?,?,?,?,?,?)''', (
                                        commission_id,
                                        pending_prop_id,
                                        pending_prop['architect_id'],
                                        client['id'],
                                        pending_prop['commission'],
                                        False,  # No pagado aún
                                        datetime.now().isoformat()
                                    ))
                                    conn.commit()
                                    conn.close()
                                    
                                    st.info("💼 El arquitecto recibirá su pago tras la finalización del proyecto")
                                    
                                    # Limpiar flags
                                    del st.session_state['pending_payment_proposal']
                                    st.session_state['payment_completed'] = False
                                    st.session_state['last_payment'] = None
                                    
                                    time.sleep(3)
                                    st.rerun()
                
                elif client_tab == '🗺️ Buscar Fincas':
                    st.info('🗺️ Redirigiendo al mapa de fincas...')
                    if st.button('Ir al Mapa', type='primary'):
                        st.query_params.update(page='Home')
                        st.rerun()


elif page == 'constructores':
    from src.contractor_manager import ContractorManager
    contractor_manager = ContractorManager(DB_PATH)
    
    st.title('🏗️ Portal de Constructores y Servicios')
    st.markdown("Regístrate para ofrecer tus servicios a clientes que buscan construir su hogar.")
    
    tab = st.radio('Seleccione una opción:', ['📝 Registro', '🔑 Acceso', '📊 Mi Panel'], horizontal=True)
    
    if tab == '📝 Registro':
        st.subheader('Registrar empresa/profesional')
        
        CATEGORIES = [
            'Construcción General',
            'Fontanería',
            'Electricidad',
            'Carpintería',
            'Albañilería',
            'Energías Renovables',
            'Decoración e Interiorismo',
            'Climatización',
            'Reformas',
            'Materiales de Construcción',
            'Otro'
        ]
        
        with st.form('registro_contractor_form'):
            empresa = st.text_input('Nombre de la empresa*')
            contacto = st.text_input('Nombre contacto*')
            email = st.text_input('Email*')
            telefono = st.text_input('Teléfono*')
            cif = st.text_input('CIF/NIF')
            categoria = st.selectbox('Categoría principal*', CATEGORIES)
            especialidad = st.text_input('Especialidad (opcional)', placeholder='Ej: Casas pasivas, reformas integrales...')
            zona = st.text_input('Zona de actuación', placeholder='Ej: Madrid, Comunidad Valenciana...')
            descripcion = st.text_area('Descripción de servicios', placeholder='Describe brevemente tu experiencia y servicios...')
            
            submitted = st.form_submit_button('Registrar Empresa')
            
            if submitted:
                if not empresa or not contacto or not email or not telefono:
                    st.error('Empresa, contacto, email y teléfono son obligatorios')
                else:
                    success, result = contractor_manager.register_contractor({
                        'company_name': empresa,
                        'contact_name': contacto,
                        'email': email,
                        'phone': telefono,
                        'cif': cif,
                        'category': categoria,
                        'specialty': especialidad,
                        'zone': zona,
                        'description': descripcion
                    })
                    if success:
                        st.success('✅ ¡Empresa registrada con éxito!')
                        st.session_state['contractor_id'] = result
                        st.balloons()
                    else:
                        st.error(f'❌ Error: {result}')
    
    elif tab == '🔑 Acceso':
        st.subheader('Iniciar sesión')
        email_login = st.text_input('Email registrado', key='contractor_login_email')
        if st.button('🔓 Acceder', key='contractor_login_btn'):
            if email_login:
                contractor = contractor_manager.get_contractor(email=email_login)
                if contractor:
                    st.success(f"✅ Bienvenido/a, {contractor['contact_name']} ({contractor['company_name']})")
                    st.session_state['contractor_id'] = contractor['id']
                else:
                    st.error('❌ Email no encontrado')
            else:
                st.warning('Introduce tu email')
    
    else:  # Mi Panel
        if 'contractor_id' not in st.session_state:
            st.warning('⚠️ Debes iniciar sesión primero')
        else:
            contractor = contractor_manager.get_contractor(contractor_id=st.session_state['contractor_id'])
            if not contractor:
                st.error('Error al cargar los datos')
            else:
                st.header(f"🏢 {contractor['company_name']}")
                st.subheader(f"👤 {contractor['contact_name']}")
                
                st.markdown('---')
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📧 **Email:** {contractor['email']}")
                    st.info(f"📱 **Teléfono:** {contractor['phone']}")
                    if contractor.get('cif'):
                        st.info(f"🆔 **CIF:** {contractor['cif']}")
                
                with col2:
                    st.success(f"🏷️ **Categoría:** {contractor['category']}")
                    if contractor.get('specialty'):
                        st.success(f"⭐ **Especialidad:** {contractor['specialty']}")
                    if contractor.get('zone'):
                        st.success(f"📍 **Zona:** {contractor['zone']}")
                
                if contractor.get('description'):
                    st.markdown('---')
                    st.markdown('**Descripción:**')
                    st.write(contractor['description'])
                
                st.markdown('---')
                st.info('🚀 **Próximamente:** Sistema de solicitudes de presupuesto, valoraciones de clientes y gestión de proyectos.')

elif page == 'servicios':
    from src.contractor_manager import ContractorManager
    contractor_manager = ContractorManager(DB_PATH)
    
    st.title('⚙️ Catálogo de Servicios')
    st.markdown("Encuentra profesionales para tu proyecto de construcción.")
    
    # Filtros
    st.sidebar.header('🔍 Filtros')
    
    categories = contractor_manager.get_categories()
    if not categories:
        categories = ['Todos']
    else:
        categories = ['Todos'] + sorted(categories)
    
    selected_category = st.sidebar.selectbox('Categoría', categories)
    
    # Obtener contractors
    if selected_category == 'Todos':
        df = contractor_manager.get_all_contractors()
    else:
        df = contractor_manager.get_all_contractors(category=selected_category)
    
    if df.empty:
        st.info('📭 No hay servicios registrados aún.')
        st.markdown('---')
        st.markdown('**¿Eres profesional del sector?**')
        if st.button('🏗️ Registra tu empresa'):
            st.query_params.update(page='constructores')
            st.rerun()
    else:
        st.success(f'📊 **{len(df)} servicios encontrados**')
        st.markdown('---')
        
        # Mostrar en cards
        for idx, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### 🏢 {row['company_name']}")
                    st.markdown(f"**👤 Contacto:** {row['contact_name']}")
                    if row.get('specialty'):
                        st.caption(f"⭐ {row['specialty']}")
                
                with col2:
                    st.markdown(f"**📧** {row['email']}")
                    st.markdown(f"**📱** {row['phone']}")
                    if row.get('zone'):
                        st.markdown(f"**📍** {row['zone']}")
                
                with col3:
                    st.markdown(f"**🏷️**")
                    st.info(row['category'])
                    if st.button('📞 Contactar', key=f"contact_{row['id']}"):
                        st.info(f"📧 Email: {row['email']}\n📱 Teléfono: {row['phone']}")
                        st.success('✉️ Próximamente: Envío automático de solicitud de presupuesto')
                
                if row.get('description'):
                    with st.expander('Ver descripción'):
                        st.write(row['description'])
                
                st.markdown('---')

else:
    st.error('Página no encontrada')
    st.write(f'page={page}')

# =====================================================
# 🏢 FOOTER PROFESIONAL (todas las páginas)
# =====================================================
st.markdown("---")
st.markdown("---")  # Doble línea para separación visual

footer_col1, footer_col2, footer_col3 = st.columns([2, 2, 1])

with footer_col1:
    st.markdown("### 📸 Galería de Fincas")
    # Obtener 3-4 fincas aleatorias para mini-gallery
    try:
        all_plots = get_all_plots()
        if all_plots and len(all_plots) > 0:
            import random
            sample_plots = random.sample(all_plots, min(4, len(all_plots)))
            
            gallery_cols = st.columns(len(sample_plots))
            for idx, (col, plot) in enumerate(zip(gallery_cols, sample_plots)):
                with col:
                    # Imagen placeholder o real
                    if plot.get('images') and len(plot['images']) > 0:
                        try:
                            st.image(plot['images'][0], width='stretch', caption=plot.get('title', ''))
                        except:
                            st.image("https://via.placeholder.com/150x100?text=Finca", width='stretch')
                    else:
                        st.image("https://via.placeholder.com/150x100?text=Finca", width='stretch')
                    
                    if st.button("Ver", key=f"footer_plot_{plot['id']}", width='stretch'):
                        st.session_state['selected_plot'] = plot['id']
                        st.session_state['page'] = 'home'
                        st.rerun()
        else:
            st.caption("🏗️ Próximamente: fincas disponibles")
    except Exception as e:
        st.caption("🏗️ Galería en construcción")

with footer_col2:
    st.markdown("### 📞 Contacto")
    st.markdown("""
    **ARCHIRAPID SL**  
    📧 Email: contacto@archirapid.com  
    📱 Teléfono: +34 XXX XXX XXX  
    📍 Madrid, España  
    
    💼 Soluciones inteligentes para arquitectos,  
    constructores y propietarios de fincas.
    """)
    st.caption("© 2024 ARCHIRAPID. Todos los derechos reservados.")

with footer_col3:
    st.markdown("### 🏢 Logo")
    # Logo profesional en footer
    logo_path = "assets/branding/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
        st.caption("_Powered by AI & Geospatial Tech_")
    else:
        # Fallback: Logo de texto
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; 
                    border-radius: 8px; 
                    text-align: center;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;'>
            ARCHIRAPID
        </div>
        """, unsafe_allow_html=True)
        st.caption("_Sube tu logo a `assets/branding/logo.png`_")