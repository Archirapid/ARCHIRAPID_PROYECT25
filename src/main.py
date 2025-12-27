"""
Views for showing plot details and handling plot registration.
"""
import streamlit as st
import folium
import uuid
from datetime import datetime
from src.db import insert_plot, get_all_plots, get_plot_by_id
from src.utils_validation import validate_email, file_size_ok
from src.logger import log

# =====================================================
# STUBS PARA EVITAR ERRORES (Funciones provistas en app principal)
# =====================================================
import sqlite3, pandas as pd, os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data.db')

def save_file(uploaded_file, kind: str):
    """Save uploaded file to uploads/ directory. Returns relative path."""
    from pathlib import Path
    uploads_dir = Path('uploads')
    uploads_dir.mkdir(exist_ok=True)
    ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'bin'
    filename = f"{kind}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = uploads_dir / filename
    filepath.write_bytes(uploaded_file.read())
    return str(filepath)

def match_projects_for_plot(plot: dict):
    # Lógica placeholder: devuelve lista vacía
    return []

def insert_reservation(reservation: dict):
    # Placeholder para auditoría; usar implementación real en app principal
    pass

def get_image_base64(image_path: str):
    try:
        with open(image_path, 'rb') as f:
            import base64
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    except Exception:
        return None

def show_plot_form():
    """Muestra el formulario de registro de fincas"""
    st.title("Registro de Finca")
    
    with st.form("plot_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Título", key="plot_title")
            description = st.text_area("Descripción", key="plot_description")
            m2 = st.number_input("Metros cuadrados", min_value=1, key="plot_m2")
            height = st.number_input("Altura máxima permitida (metros)", min_value=1.0, key="plot_height")
            price = st.number_input("Precio (€)", min_value=0.0, key="plot_price")
            
        with col2:
            type = st.selectbox("Tipo", ["Urbano", "Rústico"], key="plot_type")
            province = st.selectbox("Provincia", ["Madrid", "Barcelona", "Valencia"], key="plot_province")
            locality = st.text_input("Localidad", key="plot_locality")
            owner_name = st.text_input("Nombre del propietario", key="plot_owner_name")
            owner_email = st.text_input("Email del propietario", key="plot_owner_email")
            
        # Campos de coordenadas
        st.subheader("Coordenadas de ubicación")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            lat = st.number_input("Latitud", value=40.4168, format="%.6f", key="plot_lat")
        with col_lon:
            lon = st.number_input("Longitud", value=-3.7038, format="%.6f", key="plot_lon")
        
        # Mapa de referencia (solo visualización)
        st.subheader("Mapa de referencia")
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup="Ubicación seleccionada").add_to(m)
        try:
            st.components.v1.html(m._repr_html_(), height=400)
        except Exception:
            st.error("No fue posible renderizar el mapa interactivo.")
        
        # Campos para imágenes
        st.subheader("Archivos")
        plot_image = st.file_uploader("Imagen de la finca", type=['png', 'jpg', 'jpeg'])
        registry_note = st.file_uploader("Nota simple registral (PDF)", type=['pdf'])
        
        submitted = st.form_submit_button("Registrar Finca")
        
        if submitted:
            try:
                # Validar datos obligatorios
                if not all([title, description, m2, height, price, type, province, 
                           owner_name, owner_email, lat, lon]):
                    st.error("Por favor completa todos los campos obligatorios")
                    return
                
                # Procesar archivos subidos
                image_path = None
                if plot_image:
                    if not file_size_ok(plot_image):
                        st.error("Imagen demasiado grande (máx 10MB)")
                        return
                    image_path = save_file(plot_image, "plot")
                
                registry_path = None    
                if registry_note:
                    if not file_size_ok(registry_note):
                        st.error("PDF demasiado grande (máx 10MB)")
                        return
                    registry_path = save_file(registry_note, "registry")
                    
                # Crear registro
                plot_data = {
                    'id': uuid.uuid4().hex,
                    'title': title,
                    'description': description,
                    'lat': float(lat),
                    'lon': float(lon), 
                    'm2': int(m2),
                    'height': float(height),
                    'price': float(price),
                    'type': type,
                    'province': province,
                    'locality': locality,
                    'owner_name': owner_name,
                    'owner_email': owner_email,
                    'image_path': image_path,
                    'registry_note_path': registry_path,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                # Insertar en DB
                insert_plot(plot_data)
                log('plot_insert', plot_id=plot_data['id'], m2=plot_data['m2'], price=plot_data['price'])
                
                st.success("¡Finca registrada exitosamente!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error al registrar la finca: {str(e)}")

def show_plots():
    """Muestra el listado y mapa de fincas"""
    st.title("Fincas Disponibles")
    
    # Obtener datos
    df = get_all_plots()
    if df.shape[0] == 0:
        st.warning("No hay fincas registradas")
        return
        
    # Crear mapa base
    m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)
    
    # Agregar marcadores
    for idx, row in df.iterrows():
        # Preparar popup HTML
        popup_html = f"""
        <div style="width:200px">
            <h4>{row['title']}</h4>
            <p><b>Área:</b> {row['m2']}m²</p>
            <p><b>Precio:</b> {row['price']}€</p>
            """
            
        if row['image_path']:
            img_b64 = get_image_base64(row['image_path'])
            if img_b64:
                popup_html += f'<img src="{img_b64}" style="width:100%">'
                
        popup_html += f"""
            <p><a href="?plot={row['id']}" target="_self">Ver detalles</a></p>
        </div>
        """
        
        folium.Marker(
            [row['lat'], row['lon']], 
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['title']
        ).add_to(m)
    
    # Mostrar mapa
    try:
        st.components.v1.html(m._repr_html_(), height=500)
    except Exception:
        st.error("No fue posible renderizar el mapa interactivo.")
    
    # Mostrar listado
    st.subheader("Listado de Fincas")
    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="plot-card">
                <h3>{row['title']}</h3>
                <p><b>Localización:</b> {row['province']}</p>
                <p><b>Área:</b> {row['m2']}m² | <b>Precio:</b> {row['price']}€</p>
                <p><a href="?plot={row['id']}" target="_self">Ver detalles</a></p>
            </div>
            """, unsafe_allow_html=True)

def show_plot_detail(plot_id):
    """Muestra el detalle de una finca"""
    plot = get_plot_by_id(plot_id)
    if not plot:
        st.error("Finca no encontrada")
        return
        
    st.title(plot['title'])
    
    # Detalles principales
    col1, col2 = st.columns(2)
    
    with col1:
        if plot['image_path']:
            st.image(plot['image_path'])
            
    from src.utils_validation import html_safe
    with col2:
        area = html_safe(plot['m2'])
        height = html_safe(plot['height'])
        price = html_safe(plot['price'])
        ptype = html_safe(plot['type'])
        prov = html_safe(plot['province'])
        locality = html_safe(plot['locality']) if plot['locality'] else ''
        desc = html_safe(plot['description'])
        st.markdown(f"""
        ### Detalles
        - **Área:** {area} m²
        - **Altura máxima:** {height} m
        - **Precio:** {price} €
        - **Tipo:** {ptype}
        - **Ubicación:** {prov} {f"({locality})" if locality else ''}
        
        ### Descripción
        {desc}
        """)
        
    # Mapa individual
    m = folium.Map(location=[plot['lat'], plot['lon']], zoom_start=15)
    folium.Marker([plot['lat'], plot['lon']], popup=plot['title']).add_to(m)
    try:
        st.components.v1.html(m._repr_html_(), height=400)
    except Exception:
        st.error("No fue posible renderizar el mapa interactivo.")
    
    # Proyectos compatibles
    st.subheader("Proyectos Arquitectónicos Compatibles")
    matches = match_projects_for_plot(plot)
    if matches:
        for project in matches:
            with st.container():
                title = html_safe(project['title'])
                arch = html_safe(project['architect_name'])
                area_p = html_safe(project['area_m2'])
                maxh = html_safe(project['max_height'])
                style = html_safe(project['style'])
                price_p = html_safe(project['price'])
                desc_p = html_safe(project['description'])
                st.markdown(f"""
                <div class="plot-card">
                    <h4>{title}</h4>
                    <p><b>Arquitecto:</b> {arch}</p>
                    <p><b>Área:</b> {area_p}m² | <b>Altura:</b> {maxh}m | <b>Estilo:</b> {style}</p>
                    <p><b>Precio del proyecto:</b> {price_p}€</p>
                    <p>{desc_p}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay proyectos compatibles disponibles actualmente")
    
    # Formulario de reserva
    with st.form("reserve_form"):
        st.subheader("Reservar esta finca")
        buyer_name = st.text_input("Tu nombre")
        buyer_email = st.text_input("Tu email")
        kind = st.selectbox("Tipo de reserva", ["Completa", "Parcial"])
        amount = st.number_input("Monto de la reserva (€)", min_value=0.0)
        
        submitted = st.form_submit_button("Enviar Reserva")
        if submitted:
            try:
                if not all([buyer_name, buyer_email, amount]):
                    st.error("Por favor completa todos los campos")
                    return
                    
                # Crear reserva
                reservation = {
                    'id': uuid.uuid4().hex,
                    'plot_id': plot_id,
                    'buyer_name': buyer_name,
                    'buyer_email': buyer_email,
                    'amount': float(amount),
                    'kind': kind,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                insert_reservation(reservation)
                st.success("¡Reserva enviada exitosamente!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error al procesar la reserva: {str(e)}")