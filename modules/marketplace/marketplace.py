import streamlit as st
from modules.marketplace.utils import list_published_plots, save_upload, reserve_plot, list_projects, calculate_edificability
from src import db
import folium
import uuid
import base64
import os
import json
from pathlib import Path

# Función de navegación unificada
def navigate_to(page_name):
    """Navegación unificada usando query params y session state"""
    st.query_params["page"] = page_name
    st.session_state["selected_page"] = page_name
    st.rerun()

# Helper to read query params (compatible con varias versiones de Streamlit)
def get_query_params():
    """
    Obtiene los query params actuales.
    """
    return st.query_params

# Helper to set query params (compatible con varias versiones de Streamlit)
def set_query_param(key, value):
    """
    Establece un query param.
    """
    st.query_params[key] = str(value)

# Map plot ids to images
PLOT_IMAGES = {
    'finca_es_malaga': 'assets/fincas/image1.jpg',
    'finca_es_madrid': 'assets/fincas/image2.jpg',
    'finca_pt_lisboa': 'assets/fincas/image3.jpg',
}

def get_plot_image_path(plot):
    """Get the image path for a plot, preferring uploaded photos."""
    if plot.get('photo_paths'):
        try:
            paths = json.loads(plot['photo_paths'])
            if paths and isinstance(paths, list):
                # Añadir el prefijo uploads/ al nombre del archivo
                upload_path = f"uploads/{paths[0]}"
                # Verificar si el archivo existe
                if os.path.exists(upload_path):
                    return upload_path
        except (json.JSONDecodeError, TypeError):
            pass
    return PLOT_IMAGES.get(plot['id'], 'assets/fincas/image1.jpg')

def get_popup_image_url(plot):
    """
    Devuelve una URL absoluta file:// hacia la imagen de la finca,
    para que Folium pueda mostrarla en el popup aunque se ejecute en local.
    Si la imagen no existe, usa un placeholder en assets.
    """
    rel_path = get_plot_image_path(plot)  # 'uploads/...' o 'assets/...'
    rel_path = rel_path.lstrip('/').replace('\\', '/')

    # Construir ruta absoluta basada en el directorio actual del proyecto
    abs_path = Path(rel_path).resolve()

    if not abs_path.exists():
        # Fallback a placeholder
        abs_path = Path("assets/fincas/image1.jpg").resolve()

    # Construir URL file:// (ej. file:///C:/ARCHIRAPID_PROYECT25/uploads/imagen.jpg)
    return abs_path.as_uri()

def get_plot_detail_url(plot_id):
    """
    Construye la URL completa para ver detalles de la finca.
    Apunta a la app Streamlit principal para abrir página completa.
    """
    # Base URL de Streamlit (ajusta si es diferente)
    base_url = "http://localhost:8501"
    return f"{base_url}/?selected_plot={plot_id}"

def extract_cadastral_data(plot):
    """Extrae datos catastrales de la nota si existe."""
    cadastral_data = {}

    if plot.get('registry_note_path'):
        try:
            # Usar módulos de extracción existentes - simplificado por ahora
            # TODO: Integrar con extract_pdf.py y parse_project_memoria.py cuando estén disponibles
            cadastral_data.update({
                'surface_m2': plot.get('surface_m2'),
                'cadastral_ref': plot.get('cadastral_ref', 'Extraído de nota'),
                'shape': 'Rectangular',
                'dimensions': 'N/A',
                'buildable_m2': int(plot.get('surface_m2', 0) * 0.33)
            })
        except Exception as e:
            st.warning(f"No se pudieron extraer datos catastrales: {e}")

    # Fallback a datos básicos
    if not cadastral_data:
        cadastral_data = {
            'surface_m2': plot.get('surface_m2'),
            'cadastral_ref': plot.get('cadastral_ref', 'No disponible'),
            'shape': 'Rectangular (estimado)',
            'dimensions': 'N/A',
            'buildable_m2': int(plot.get('surface_m2', 0) * 0.33)
        }

    return cadastral_data

def setup_filters():
    """Configura y retorna los filtros del sidebar."""
    st.sidebar.header("Filtros")
    min_m = st.sidebar.number_input("Min m²", value=0)
    max_m = st.sidebar.number_input("Max m²", value=100000)
    q = st.sidebar.text_input("Buscar (provincia, título)")
    return min_m, max_m, q

def get_filtered_plots(min_surface, max_surface, search_query):
    """Obtiene las fincas filtradas según los criterios especificados.
    
    Nota: min_surface y max_surface ahora corresponden a superficie en m²,
    no a precio. La función db.list_fincas_filtradas filtra por precio,
    pero aquí asumimos que los valores son para superficie.
    """
    # Por ahora no filtramos por provincia
    prov_param = None
    # Si max_surface es 0 (valor por defecto), tratamos como sin máximo
    if max_surface == 0:
        max_surface = 999999  # Valor alto para representar sin límite
    plots_all = db.list_fincas_filtradas(prov_param, float(min_surface), float(max_surface))

    # Aplicar búsqueda de texto si existe (incluye provincia, título y referencia)
    if search_query:
        plots_all = [p for p in plots_all if search_query.lower() in
                    ((p.get("title", "") or "") + " " +
                     (p.get("province", "") or "") + " " +
                     str(p.get("cadastral_ref", "") or "")).lower()]

    return plots_all

def render_featured_plots(plots):
    """Renderiza la sección de fincas destacadas (Premium primero, luego últimas publicadas)."""
    st.header("Fincas Destacadas")

    if not plots:
        st.info("No hay fincas disponibles con los filtros actuales.")
        return

    # Separar fincas premium
    premium = [p for p in plots if p.get("featured") == 1]
    normal = [p for p in plots if p.get("featured") != 1]

    # Ordenar premium por fecha (más recientes primero)
    premium_sorted = sorted(
        premium,
        key=lambda p: str(p.get("created_at") or ""),
        reverse=True
    )

    # Ordenar normales por fecha
    normal_sorted = sorted(
        normal,
        key=lambda p: str(p.get("created_at") or ""),
        reverse=True
    )

    # Construir lista final: primero premium, luego normales
    featured = premium_sorted[:6]

    if len(featured) < 6:
        needed = 6 - len(featured)
        featured += normal_sorted[:needed]

    # Renderizar en grid 2 columnas
    cols = st.columns(2)
    for i, plot in enumerate(featured):
        with cols[i % 2]:
            img_path = get_plot_image_path(plot)
            st.image(img_path, width=120, caption=f"{plot['title'][:15]}...")

            if plot.get("featured") == 1:
                st.markdown("⭐ **Destacada Premium**")

            if st.button("Ver", key=f"mini_{plot['id']}", help=f"Ver detalles de {plot['title']}"):
                set_query_param("selected_plot", plot["id"])
                st.rerun()

def render_map(plots):
    """Renderiza el mapa interactivo con las fincas."""
    st.header("🗺️ Mapa de Fincas")

    # Filtrar solo plots con coordenadas válidas
    plots_with_coords = [p for p in plots if p.get('lat') is not None and p.get('lon') is not None]

    if not plots_with_coords:
        st.info("📍 No hay fincas con coordenadas disponibles para mostrar en el mapa.")
        return

    # Calcular centro del mapa
    lats = [float(p['lat']) for p in plots_with_coords]
    lons = [float(p['lon']) for p in plots_with_coords]
    center_lat = sum(lats) / len(lats) if lats else 40.1
    center_lon = sum(lons) / len(lons) if lons else -4.0
    zoom_level = 6 if len(plots_with_coords) > 1 else 12

    # Crear mapa con Folium
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="CartoDB positron")

    for plot in plots_with_coords:
        lat = float(plot['lat'])
        lon = float(plot['lon'])
        img_path = get_plot_image_path(plot)
        icon = folium.Icon(color='red', icon='home', prefix='fa')

        # Crear popup HTML con imagen y enlace a detalles
        img_src = get_popup_image_url(plot)  # URL completa o relativa para la imagen
        detail_url = get_plot_detail_url(plot['id'])

        popup_html = f'''
        <div style="width:160px; text-align:center;">
            <img src="{img_src}" style="width:100%; border-radius:5px;" alt="Imagen de {plot['title']}">
            <br><b>{plot['title']}</b><br>
            <small>{plot.get('m2', 'N/A')} m²</small><br>
            <a href="{detail_url}" target="_blank"
               style="margin-top:5px; padding:5px 10px; background:#ff4b4b; color:white; text-decoration:none; border-radius:3px; display:inline-block;">
                Ver más detalles
            </a>
        </div>
        '''

        marker = folium.Marker([lat, lon], icon=icon, popup=folium.Popup(popup_html, max_width=250))
        marker.add_to(m)

    # Renderizar mapa
    try:
        st.components.v1.html(m._repr_html_(), height=600)
    except Exception as e:
        st.error(f"No fue posible renderizar el mapa interactivo: {str(e)}")
        # Fallback: mostrar coordenadas como texto
        st.write("**Fincas encontradas:**")
        for plot in plots_with_coords:
            st.write(f"- {plot.get('title', 'Sin título')}: {plot.get('lat')}, {plot.get('lon')}")

    # Control nativo para navegación
    render_map_navigation(plots_with_coords)

def render_map_navigation(plots_with_coords):
    """Renderiza el control de navegación del mapa."""
    st.markdown("---")
    if not plots_with_coords:
        return

    # Crear opciones para el selectbox
    plot_options = {f"{p['title']} ({p.get('m2', 'N/A')} m²)": p['id'] for p in plots_with_coords}
    selected_option = st.selectbox(
        "Selecciona una finca del mapa para ver detalles:",
        options=[""] + list(plot_options.keys()),
        key="map_plot_selector_v3"
    )

    if st.button("🔍 IR A LA FICHA DETALLADA DE LA FINCA SELECCIONADA",
               use_container_width=True,
               disabled=not selected_option):
        if selected_option and selected_option in plot_options:
            selected_id = plot_options[selected_option]
            set_query_param("selected_plot", selected_id)

def render_client_panel():
    """Renderiza el panel de cliente cuando hay una transacción completada."""
    if not st.session_state.get("transaction_completed", False):
        return

    st.success("🎉 ¡Transacción completada exitosamente!")
    st.balloons()

    st.markdown("---")

    # Panel de cliente mejorado
    st.subheader("🏠 Panel de Cliente - ARCHIRAPID")
    st.info(f"**✅ Transacción completada:** {st.session_state.get('transaction_type', 'N/A').title()} - ID: {st.session_state.get('transaction_id', 'N/A')}")

    st.markdown("### 🎯 ¿Qué desea hacer ahora?")

    # Opciones principales en cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏡 DISEÑAR VIVIENDA")
        st.write("Cree su casa ideal con nuestros arquitectos")
        if st.button("🚀 Ir al Diseñador", key="go_designer", type="primary"):
            st.success("🎨 Redirigiendo al Diseñador de Vivienda...")
            st.info("Aquí se abriría el módulo de diseño de vivienda")

    with col2:
        st.markdown("#### 📐 GESTIONAR PROYECTOS")
        st.write("Vea proyectos compatibles con su finca")
        if st.button("📋 Ver Mis Proyectos", key="go_projects", type="primary"):
            st.success("📐 Redirigiendo a Gestión de Proyectos...")
            st.info("Aquí se mostrarían los proyectos disponibles para su finca")

    st.markdown("---")

    # Opciones adicionales
    st.markdown("### 🔧 Opciones Adicionales")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("📊 Ver Transacción", key="view_transaction", use_container_width=True):
            st.info(f"📋 **Detalles de la transacción:**\n"
                   f"- Tipo: {st.session_state.get('transaction_type', 'N/A')}\n"
                   f"- ID: {st.session_state.get('transaction_id', 'N/A')}\n"
                   f"- Cliente: {st.session_state.get('client_name', 'N/A')}\n"
                   f"- Email: {st.session_state.get('client_email', 'N/A')}")

    with col_b:
        if st.button("🏠 Volver al Marketplace", key="back_marketplace"):
            st.success("🏠 Volviendo al marketplace...")
            # Limpiar estado
            keys_to_clear = ["show_client_form", "transaction_completed", "transaction_type",
                           "transaction_id", "client_name", "client_email"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with col_c:
        if st.button("📧 Contactar Soporte", key="contact_support"):
            st.info("📧 Contactando con soporte técnico...")
            st.info("Un agente se pondrá en contacto con usted pronto")

def render_projects_section():
    """Renderiza la sección de proyectos arquitectónicos (actualmente desactivada)."""
    st.markdown("---")
    # Temporarily disabled: list_projects() currently raises DB error (no such column: p.characteristics_json)
    # Wrapping the entire projects block in `if False` until DB schema is fixed.
    if False:
        st.header("🏗️ Proyectos Arquitectónicos Disponibles")
        projects = list_projects()
        if projects:
            for proj in projects:
                # Botón visual con thumbnail
                col1, col2 = st.columns([1, 3])
                with col1:
                    fotos = proj['files'].get('fotos', [])
                    thumbnail = f"uploads/{os.path.basename(fotos[0])}" if fotos else "assets/fincas/image1.jpg"
                    st.image(thumbnail, width=100, caption="")
                    if st.button("Ver Proyecto", key=f"view_{proj['id']}"):
                        st.session_state.selected_proj = proj['id']
                with col2:
                    st.subheader(f"{proj['title']}")
                    st.write(f"**Arquitecto:** {proj['architect_name']} ({proj['company'] or 'Independiente'})")
                    st.write(f"**Precio:** €{proj['price']} | **Área:** {proj['area_m2']} m²")
                    st.write(f"**Descripción:** {proj['description'][:100]}...")

        else:
            st.info("No hay proyectos arquitectónicos disponibles aún. ¡Sé el primero en subir uno!")

    # Mostrar detalles del proyecto seleccionado (código desactivado)
    selected_proj_id = st.session_state.get('selected_proj')
    if selected_proj_id:
        # Código de detalles del proyecto aquí (desactivado)
        pass

def main():
    # 1. Verificar si hay una finca seleccionada en la URL
    params = get_query_params() or {}
    selected_plot_local = None
    if params.get("selected_plot"):
        selected_plot_local = params["selected_plot"][0] if isinstance(params["selected_plot"], list) else params["selected_plot"]

    # Si hay una finca seleccionada, mostrar página de detalles y salir
    if selected_plot_local:
        from modules.marketplace.plot_detail import show_plot_detail_page
        show_plot_detail_page(selected_plot_local)
        return

    # 2. Título principal
    st.title("🏠 ARCHIRAPID — Marketplace de Fincas y Proyectos")

    # Mensaje de bienvenida si está logueado
    if st.session_state.get('logged_in'):
        user_name = st.session_state.get('full_name', st.session_state.get('email', 'Usuario'))
        role = st.session_state.get('rol', '')
        if role == 'services':
            panel_name = "Panel de Proveedor"
        elif role == 'architect':
            panel_name = "Panel de Arquitecto"
        elif role == 'admin':
            panel_name = "Intranet"
        else:
            panel_name = "Panel de Cliente"
        
        st.success(f"👋 ¡Hola, {user_name}! | [Ir a Mi {panel_name}](?page={panel_name.replace(' ', '%20')})")

    # 3. Tres tarjetas de acceso directo (única fila de navegación)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏠 Tengo un Terreno")
        st.write("Publica tu finca y recibe propuestas de arquitectos")
        if st.button("Subir mi Finca", key="upload_plot", use_container_width=True):
            if st.session_state.get("logged_in") and st.session_state.get("role") == "client":
                navigate_to("🏠 Propietarios")
            else:
                st.session_state['login_role'] = 'client'
                st.session_state['viewing_login'] = True
                st.rerun()

    with col2:
        st.markdown("### 🏗️ Soy Arquitecto")
        st.write("Vende tus proyectos y conecta con clientes")
        if st.button("Mis Proyectos", key="architect_portal", use_container_width=True):
            navigate_to("Arquitectos (Marketplace)")

    with col3:
        st.markdown("### 🏡 Busco Casa")
        st.write("Explora proyectos disponibles en el marketplace")

        # Verificar si el usuario está logueado
        logged_in = st.session_state.get("logged_in", False)
        email = st.session_state.get("email", "")

        if logged_in and email:
            # Usuario logueado - mostrar Mis Favoritos
            if st.button("Mis Favoritos", key="browse_projects", use_container_width=True):
                navigate_to("👤 Panel de Cliente")
        else:
            # Usuario no logueado - mostrar mensaje de registro
            if st.button("Ver Proyectos", key="browse_projects", use_container_width=True):
                st.info("¡Bienvenido! Puedes explorar todos los proyectos abajo. Si quieres guardar tus favoritos o contactar con arquitectos, regístrate aquí.")
                if st.button("📝 Registrarme", key="register_from_marketplace"):
                    navigate_to("Registro de Usuario")

    # 4. Marketplace de proyectos (siempre visible debajo)
    st.markdown("---")

    # Configurar filtros del sidebar
    min_surface, max_surface, search_query = setup_filters()

    # Obtener fincas filtradas
    plots = get_filtered_plots(min_surface, max_surface, search_query)

    # Layout principal: dos columnas
    left_col, right_col = st.columns([1, 2])

    with left_col:
        render_featured_plots(plots)

    with right_col:
        render_map(plots)

    # Sección de proyectos adicionales
    render_projects_section()