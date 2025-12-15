import streamlit as st
from modules.marketplace.utils import list_published_plots, save_upload, reserve_plot, list_projects, calculate_edificability
from src.query_params import get_query_params
from streamlit_folium import st_folium
import folium
import uuid
import base64
import os
import json
from pathlib import Path

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

def get_image_base64(image_path):
    """Convert image to base64 for embedding in HTML."""
    full_path = os.path.join(os.getcwd(), image_path)
    try:
        with open(full_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except Exception as e:
        return ""

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

def main():
    # Handle URL params for plot selection (use compatibility helper)
    qp = get_query_params() or {}
    selected_from_url = qp.get("selected_plot")
    if selected_from_url:
        if isinstance(selected_from_url, list):
            selected_from_url = selected_from_url[0]
        st.session_state["selected_plot"] = selected_from_url
    selected_plot_local = st.session_state.get("selected_plot")
    st.title("ARCHIRAPID — Marketplace de Fincas y Proyectos")

    st.sidebar.header("Filtros")
    min_m = st.sidebar.number_input("Min m²", value=0)
    max_m = st.sidebar.number_input("Max m²", value=100000)
    q = st.sidebar.text_input("Buscar (provincia, título)")

    plots_all = list_published_plots()
    # simple filters - pero mantener todas para detalles
    plots_filtered = [p for p in plots_all if (p["surface_m2"] is None or (p["surface_m2"]>=min_m and p["surface_m2"]<=max_m))]
    if q:
        plots_filtered = [p for p in plots_filtered if q.lower() in (p.get("title","")+" "+str(p.get("cadastral_ref",""))).lower()]

    # Usar plots_filtered para mostrar en mapa y miniaturas, pero plots_all para detalles
    plots = plots_filtered

    left,right = st.columns([1,2])
    with left:
        st.header("Fincas Destacadas")
        if plots:
            # Grid 2x3 para miniaturas (máximo 6, pero con 4 existentes)
            cols = st.columns(2)
            for i, p in enumerate(plots[:6]):  # Max 6
                with cols[i % 2]:
                    img_path = get_plot_image_path(p)
                    if st.button("Ver", key=f"mini_{p['id']}", help=f"Ver detalles de {p['title']}"):
                        st.session_state["selected_plot"] = p["id"]
                    st.image(img_path, width=120, caption=f"{p['title'][:15]}...")

    with right:
        m = folium.Map(location=[40.1,-4.0], zoom_start=6, tiles="CartoDB positron")
        for p in plots:
            lat = p['lat'] or (40.1 + hash(p['id']) % 10 * 0.01)
            lon = p['lon'] or (-4.0 + hash(p['id']) % 10 * 0.01)
            img_path = get_plot_image_path(p)
            img_base64 = get_image_base64(img_path)
            icon = folium.Icon(color='red', icon='map-marker', prefix='fa')
            popup_html = f"""
            <div style='width:220px'>
                <h4>{p['title']}</h4>
                <img src='{img_base64}' width='200' style='margin-bottom:10px;'>
                <div>{p.get('surface_m2')} m² · €{p.get('price')}</div>
                <button onclick="window.location.href = window.location.pathname + '?selected_plot={p['id']}'" style='display:block; margin-top:10px; padding:5px; background:#4CAF50; color:white; border:none; border-radius:3px; text-align:center; width:100%; cursor:pointer;'>Ver detalles aquí</button>
            </div>
            """
            marker = folium.Marker([lat,lon], icon=icon, popup=popup_html)
            marker.add_to(m)
            # Asignar ID al marker para identificación
            marker._id = p['id']
        map_data = st_folium(m, width=700, height=600)

        # NO detectar clics aquí - usar solo el botón del popup que cambia URL

    # Detalles de finca seleccionada - MODAL DESACTIVADO TEMPORALMENTE
    # Para resolver conflicto de múltiples dialogs en Streamlit
    """
    if selected_plot_local and not st.session_state.get("show_client_form", False):
        pid = selected_plot_local
        st.session_state["selected_plot"] = pid  # sync

        # Modal grande horizontal
        @st.dialog("Detalle de Finca Seleccionada", width="large")
        def show_plot_details(plots_data, plot_id):
            try:
                p = next((x for x in plots_data if x["id"]==plot_id), None)
                if p:
                    cadastral_data = extract_cadastral_data(p)

                    # Layout horizontal con columnas
                    col_left, col_right = st.columns([1, 1])

                    with col_left:
                        st.subheader("📋 Datos Catastrales")
                        img_path = get_plot_image_path(p)
                        if os.path.exists(img_path):
                            st.image(img_path, width=300, caption=p['title'])
                        else:
                            st.image("assets/fincas/image1.jpg", width=300, caption=p['title'])

                        st.markdown(f"**🏠 Título:** {p['title']}")
                        st.markdown(f"**📏 Superficie:** {cadastral_data.get('surface_m2', p.get('surface_m2', 'N/A'))} m²")
                        st.markdown(f"**🏗️ Máx. Construible:** {cadastral_data.get('buildable_m2', int(p.get('surface_m2', 0) * 0.33))} m²")
                        st.markdown(f"**💰 Precio:** €{p.get('price', 'N/A')}")
                        st.markdown(f"**📋 Ref. Catastral:** {cadastral_data.get('cadastral_ref', p.get('cadastral_ref', 'N/A'))}")
                        st.markdown(f"**📍 Ubicación:** {p.get('lat', 'N/A')}, {p.get('lon', 'N/A')}")

                        if cadastral_data.get('shape'):
                            st.markdown(f"**🔷 Forma:** {cadastral_data['shape']}")
                        if cadastral_data.get('dimensions'):
                            st.markdown(f"**📐 Dimensiones:** {cadastral_data['dimensions']}")

                    with col_right:
                        # Acciones generales de la finca
                        st.subheader("🛠️ Acciones")
                        
                        col_res_finca, col_comp_finca = st.columns(2)
                        with col_res_finca:
                            if st.button("💰 Reservar Finca (10%)", key=f"reserve_finca_10_{p['id']}", use_container_width=True, help="Reservar finca con 10% del precio"):
                                amount = (p.get("price") or 0) * 0.10
                                rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="reservation")
                                st.success(f"✅ Reserva de finca simulada: {rid} — {amount}€")
                                st.session_state["show_client_form"] = True
                                st.session_state["transaction_type"] = "reservation"
                                st.session_state["transaction_id"] = rid
                                st.rerun()
                        with col_comp_finca:
                            if st.button("🏠 Comprar Finca (100%)", key=f"purchase_finca_100_{p['id']}", use_container_width=True, help="Comprar finca completa"):
                                amount = p.get("price") or 0
                                rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="purchase")
                                st.success(f"✅ Compra de finca simulada: {rid} — {amount}€")
                                st.session_state["show_client_form"] = True
                                st.session_state["transaction_type"] = "purchase"
                                st.session_state["transaction_id"] = rid
                                st.rerun()
                        
                        # Herramientas avanzadas
                        st.markdown("---")
                        col_analizar, col_informe = st.columns(2)
                        with col_analizar:
                            if st.button("🔍 Analizar Nota Castral", key=f"analyze_note_{p['id']}", use_container_width=True, help="Analizar documento catastral"):
                                st.info("🔄 Analizando nota catastral...")
                                # Aquí iría la lógica de análisis de nota
                                st.success("✅ Análisis completado - Datos extraídos de la nota")
                        with col_informe:
                            if st.button("📋 Generar Informe PDF", key=f"generate_report_{p['id']}", use_container_width=True, help="Generar informe completo en PDF"):
                                st.info("🔄 Generando informe PDF...")
                                # Aquí iría la lógica de generación de PDF
                                st.success("✅ Informe PDF generado y descargado")
                        
                        # Edificabilidad
                        if st.button("🏗️ Examinar Edificabilidad", key=f"check_edificability_{p['id']}", use_container_width=True, help="Análisis detallado de edificabilidad"):
                            edificabilidad_detallada = calculate_edificability(cadastral_data.get('surface_m2', p.get('surface_m2', 0)))
                            st.info(f"🏗️ **Análisis de Edificabilidad:**\n\n"
                                   f"- Superficie total: {cadastral_data.get('surface_m2', p.get('surface_m2', 0)):.0f} m²\n"
                                   f"- Coeficiente de edificabilidad: 33%\n"
                                   f"- Área máxima construible: {edificabilidad_detallada:.0f} m²\n"
                                   f"- Área disponible: {edificabilidad_detallada:.0f} m²")
                        
                        st.markdown("---")

                        # Proyectos compatibles
                        edificabilidad = calculate_edificability(cadastral_data.get('surface_m2', p.get('surface_m2', 0)))
                        projects_all_list = list_projects()
                        # Eliminar duplicados por ID
                        unique_projects = []
                        seen_ids = set()
                        for proj in projects_all_list:
                            if proj['id'] not in seen_ids:
                                unique_projects.append(proj)
                                seen_ids.add(proj['id'])
                        compatible_projects = [proj for proj in unique_projects if proj['area_m2'] <= edificabilidad]

                        st.subheader("🔍 Proyectos Arquitectónicos Compatibles")
                        if compatible_projects:
                            st.success(f"Edificabilidad máxima: {edificabilidad:.0f} m² (33% de superficie)")
                            for proj in compatible_projects[:5]:
                                with st.expander(f"🏗️ {proj['title']} - {proj['area_m2']} m² - €{proj['price']}"):
                                    st.write(f"**📝 Descripción:** {proj['description']}")
                                    st.write(f"**👷 Arquitecto:** {proj['architect_name']}")
                                    if proj['company']:
                                        st.write(f"**🏢 Empresa:** {proj['company']}")

                                    # Botones de acción
                                    col_res, col_comp = st.columns(2)
                                    with col_res:
                                        if st.button(f"📋 Reservar 10%", key=f"reserve_10_{proj['id']}_{p['id']}", use_container_width=True):
                                            amount = (p.get("price") or 0) * 0.10
                                            rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="reservation")
                                            st.success(f"✅ Reserva simulada: {rid} — {amount}€")
                                            st.session_state["show_client_form"] = True
                                            st.session_state["transaction_type"] = "reservation"
                                            st.session_state["transaction_id"] = rid
                                            st.rerun()
                                    with col_comp:
                                        if st.button(f"💰 Comprar (100%)", key=f"purchase_100_{proj['id']}_{p['id']}", use_container_width=True):
                                            amount = p.get("price") or 0
                                            rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="purchase")
                                            st.success(f"✅ Compra simulada: {rid} — {amount}€")
                                            st.session_state["show_client_form"] = True
                                            st.session_state["transaction_type"] = "purchase"
                                            st.session_state["transaction_id"] = rid
                                            st.rerun()
                        else:
                            st.info("No hay proyectos compatibles para esta finca.")

                        # Información adicional
                        if st.button("📊 Mostrar Información Adicional", key=f"info_{p['id']}", help="Ver datos técnicos completos"):
                            st.json({**p, **cadastral_data})
                else:
                    st.error(f"No se encontró la finca con ID: {plot_id}")
            except Exception as e:
                st.error(f"Error al cargar detalles de la finca: {str(e)}")
                st.exception(e)

        show_plot_details(plots_all, pid)
    """

    # Formulario de datos personales después de reserva/compra - DESACTIVADO TEMPORALMENTE
    # Para evitar conflicto de múltiples dialogs en Streamlit
    """
    if st.session_state.get("show_client_form", False):
        # Limpiar el estado de la modal de detalles para evitar conflictos
        if "selected_plot" in st.session_state:
            del st.session_state["selected_plot"]

        # @st.dialog("Complete sus datos personales")  # DESACTIVADO: Conflicto con múltiples dialogs
        def show_client_form():
            st.subheader("📝 Datos Personales")
            st.write("Por favor complete sus datos para finalizar la transacción:")

            with st.form("client_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre = st.text_input("Nombre *", placeholder="Su nombre")
                    apellidos = st.text_input("Apellidos *", placeholder="Sus apellidos")
                    email = st.text_input("Email *", placeholder="+34 600 000 000")
                with col2:
                    telefono = st.text_input("Teléfono *", placeholder="+34 600 000 000")
                    direccion = st.text_area("Dirección completa *", placeholder="Calle, número, CP, ciudad, provincia")
                    observaciones = st.text_area("Observaciones", placeholder="Comentarios adicionales (opcional)")

                submitted = st.form_submit_button("✅ Confirmar y Finalizar")

                if submitted:
                    if not nombre or not apellidos or not email or not telefono or not direccion:
                        st.error("Por favor complete todos los campos obligatorios (*)")
                    else:
                        # Procesar la transacción
                        transaction_type = st.session_state.get("transaction_type", "reservation")
                        transaction_id = st.session_state.get("transaction_id", "")

                        # Aquí iría la lógica para guardar los datos del cliente
                        st.success(f"✅ {transaction_type.title()} completada exitosamente!")
                        st.success(f"📧 Recibirás un email de confirmación en {email}")
                        st.success(f"🆔 ID de transacción: {transaction_id}")

                        # Limpiar estado
                        st.session_state["show_client_form"] = False
                        if "transaction_type" in st.session_state:
                            del st.session_state["transaction_type"]
                        if "transaction_id" in st.session_state:
                            del st.session_state["transaction_id"]

                        st.balloons()
                        st.rerun()

        # show_client_form()  # DESACTIVADO: Conflicto con múltiples dialogs
    """

    # Panel de cliente fuera del dialog
    if st.session_state.get("transaction_completed", False):
        
        # Panel de cliente fuera del dialog
        if st.session_state.get("transaction_completed", False):
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
                if st.button("🚀 Ir al Diseñador", key="go_designer", use_container_width=True, type="primary"):
                    st.success("🎨 Redirigiendo al Diseñador de Vivienda...")
                    st.info("Aquí se abriría el módulo de diseño de vivienda")
                    # Aquí iría la navegación real al diseñador
            
            with col2:
                st.markdown("#### 📐 GESTIONAR PROYECTOS") 
                st.write("Vea proyectos compatibles con su finca")
                if st.button("📋 Ver Mis Proyectos", key="go_projects", use_container_width=True, type="primary"):
                    st.success("📐 Redirigiendo a Gestión de Proyectos...")
                    st.info("Aquí se mostrarían los proyectos disponibles para su finca")
                    # Aquí iría la navegación real a gestión de proyectos
            
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
                if st.button("🏠 Volver al Marketplace", key="back_marketplace", use_container_width=True):
                    st.success("🏠 Volviendo al marketplace...")
                    # Limpiar estado
                    for key in ["show_client_form", "transaction_completed", "transaction_type", "transaction_id", "client_name", "client_email"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            with col_c:
                if st.button("📧 Contactar Soporte", key="contact_support", use_container_width=True):
                    st.info("📧 Contactando con soporte técnico...")
                    st.info("Un agente se pondrá en contacto con usted pronto")

    # Proyectos Arquitectónicos
    st.markdown("---")
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

    # Mostrar detalles del proyecto seleccionado
    selected_proj_id = st.session_state.get('selected_proj')
    if selected_proj_id:
        if projects:
            proj = next((p for p in projects if p['id'] == selected_proj_id), None)
            if proj:
                with st.expander("Detalles Completos del Proyecto", expanded=True):
                    tab_fotos, tab_3d, tab_rv, tab_datos, tab_ia, tab_comprar = st.tabs(["Fotos", "3D", "RV", "Datos", "IA", "Comprar"])
                    
                    with tab_fotos:
                        files = proj['files']
                        if 'fotos' in files and files['fotos']:
                            # Imagen principal con popup
                            img_path = f"uploads/{os.path.basename(files['fotos'][0])}"
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                with st.popover("Ver"):
                                    st.image(img_path, width=600, caption="Vista completa")
                            with col2:
                                st.image(img_path, width=400, caption="Vista principal del proyecto")
                            
                            if len(files['fotos']) > 1:
                                st.subheader("Galería de Fotos")
                                cols = st.columns(min(len(files['fotos'])-1, 3))
                                for i, foto in enumerate(files['fotos'][1:], start=1):
                                    with cols[(i-1) % len(cols)]:
                                        img_path = f"uploads/{os.path.basename(foto)}"
                                        with st.popover(f"Ver Foto {i+1}"):
                                            st.image(img_path, width=600, caption=f"Foto {i+1} completa")
                                        st.image(img_path, width=200, caption=f"Foto {i+1}")
                        else:
                            st.image("assets/fincas/image1.jpg", width=400, caption="Proyecto sin imagen")
                
                    with tab_3d:
                        files = proj['files']
                        if 'glb' in files and files['glb']:
                            glb_path = os.path.basename(files['glb'][0])
                            st.subheader("Modelo 3D Interactivo")
                            # Simulación MVP: SVG simple de casa 3D
                            svg_3d = f"""
                            <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                                <!-- Base de la casa -->
                                <rect x="150" y="200" width="100" height="80" fill="#8B4513" stroke="#654321" stroke-width="2"/>
                                <!-- Techo -->
                                <polygon points="140,200 200,150 260,200" fill="#DC143C" stroke="#B22222" stroke-width="2"/>
                                <!-- Puerta -->
                                <rect x="185" y="240" width="30" height="40" fill="#654321"/>
                                <!-- Ventanas -->
                                <rect x="160" y="220" width="20" height="20" fill="#87CEEB"/>
                                <rect x="220" y="220" width="20" height="20" fill="#87CEEB"/>
                                <!-- Chimenea -->
                                <rect x="210" y="160" width="10" height="30" fill="#696969"/>
                                <!-- Texto -->
                                <text x="200" y="290" text-anchor="middle" font-family="Arial" font-size="12" fill="#000">Vista 3D Simulada</text>
                                <text x="200" y="305" text-anchor="middle" font-family="Arial" font-size="10" fill="#666">Proyecto: {proj['title'][:20]}...</text>
                            </svg>
                            """
                            st.components.v1.html(svg_3d, height=320)
                            st.write("**Representación 3D:**")
                            st.write(f"- Modelo GLB disponible: {glb_path}")
                            st.write("- Incluye: Estructura completa, divisiones de habitaciones y baños, jardín.")
                            st.write("- Funcionalidad completa próximamente con visor 3D avanzado.")
                            st.download_button(f"Descargar Modelo 3D ({glb_path})", data=open(f"uploads/{glb_path}", 'rb'), file_name=glb_path, key=f"dl_glb_{proj['id']}")
                        else:
                            st.warning("Modelo 3D no disponible. Mostrando representación esquemática.")
                            # SVG esquemático
                            svg_schema = f"""
                            <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
                                <rect x="150" y="200" width="100" height="80" fill="#D3D3D3" stroke="#A9A9A9" stroke-width="2"/>
                                <polygon points="140,200 200,150 260,200" fill="#F0F0F0" stroke="#C0C0C0" stroke-width="2"/>
                                <text x="200" y="240" text-anchor="middle" font-family="Arial" font-size="14" fill="#000">Casa</text>
                                <text x="200" y="290" text-anchor="middle" font-family="Arial" font-size="12" fill="#000">Esquema Básico</text>
                            </svg>
                            """
                            st.components.v1.html(svg_schema, height=320)
                            st.write("**Esquema Básico:**")
                            st.write(f"- Superficie: {proj['area_m2']} m²")
                            st.write(f"- Habitaciones: {proj['characteristics'].get('habitaciones', 0)}")
                            st.write(f"- Baños: {proj['characteristics'].get('banos', 0)}")
                            st.write("- Diseño: Moderna con jardín integrado.")
                            st.info("Sube un archivo GLB para ver el modelo 3D real.")
                        
                        # Otros archivos 3D
                        if 'glb' in files and len(files['glb']) > 1:
                            st.subheader("Modelos Adicionales")
                            for glb in files['glb'][1:]:
                                fname = os.path.basename(glb)
                                st.download_button(f"Descargar {fname}", data=open(f"uploads/{fname}", 'rb'), file_name=fname, key=f"glb_extra_{proj['id']}_{fname}")
                
                    with tab_rv:
                        files = proj['files']
                        if 'rv' in files and files['rv']:
                            rv_path = os.path.basename(files['rv'])
                            st.subheader("Experiencia de Realidad Virtual")
                            # Viewer RV inline con A-Frame (mock básico)
                            rv_viewer_html = """
                            <script src="https://aframe.io/releases/1.2.0/aframe.min.js"></script>
                            <a-scene embedded style="width: 100%; height: 400px;">
                                <a-box position="-1 0.5 -3" rotation="0 45 0" color="#4CC3D9"></a-box>
                                <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E"></a-sphere>
                                <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D"></a-cylinder>
                                <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4"></a-plane>
                                <a-sky color="#ECECEC"></a-sky>
                            </a-scene>
                            """
                            st.components.v1.html(rv_viewer_html, height=450)
                            st.caption("Vista RV básica (Próximamente: Cargar escena real desde archivo)")
                            st.download_button(f"Descargar Archivo RV ({rv_path})", data=open(f"uploads/{rv_path}", 'rb'), file_name=rv_path, key=f"dl_rv_{proj['id']}")
                        else:
                            st.info("No hay experiencia RV disponible para este proyecto.")
                
                    with tab_datos:
                        st.subheader("Información Detallada del Proyecto")
                        st.write(f"**Descripción:** {proj['description']}")
                        st.write(f"**Superficie Construida:** {proj['area_m2']} m²")
                        st.write(f"**Precio del Proyecto:** €{proj['price']}")
                        st.write(f"**Arquitecto:** {proj['architect_name']}")
                        if proj['company']:
                            st.write(f"**Empresa:** {proj['company']}")
                        
                        chars = proj['characteristics']
                        st.write(f"**Tipo de Construcción:** {chars.get('tipo_construccion', 'N/A')}")
                        st.write(f"**Estilo Arquitectónico:** {chars.get('estilo', 'N/A')}")
                        st.write(f"**Habitaciones:** {chars.get('habitaciones', 0)}")
                        st.write(f"**Baños:** {chars.get('banos', 0)}")
                        st.write(f"**Garage:** {chars.get('garage', 'Sí')}")
                        st.write(f"**Piscina:** {chars.get('piscina', 'Opcional')}")
                        st.write(f"**Parcela Construida:** {proj['area_m2'] * 1.5:.0f} m² (aprox.)")
                        st.write(f"**Alturas:** {chars.get('alturas', '2 plantas')}")
                        
                        # Costes y presupuesto
                        presupuesto_construccion = proj['price'] * 0.8  # Asumiendo que el precio incluye diseño + construcción
                        st.write(f"**Presupuesto Estimado de Construcción:** €{presupuesto_construccion:.0f}")
                        st.write(f"**Coste por m²:** €{presupuesto_construccion / proj['area_m2']:.0f}/m²")
                        st.write("**Incluye:** Diseño arquitectónico, planos técnicos, permisos, construcción básica.")
                        
                        # Tecnologías
                        st.subheader("Tecnologías y Sostenibilidad")
                        st.write("**Gemelo Digital:** Sí - Modelo 3D interactivo incluido.")
                        st.write("**Energías Alternativas:** Paneles solares opcionales, calefacción eficiente.")
                        st.write("**Certificaciones:** Preparado para LEED o similar (consultar).")
                        
                        # Planos técnicos
                        files = proj['files']
                        if 'dwg' in files and files['dwg']:
                            st.subheader("Planos Técnicos Disponibles")
                            for dwg in files['dwg']:
                                fname = os.path.basename(dwg)
                                st.write(f"📁 {fname}")
                                st.download_button(f"Descargar {fname}", data=open(f"uploads/{fname}", 'rb'), file_name=fname, key=f"dwg_{proj['id']}_{fname}")
                
                    with tab_ia:
                        st.subheader("Asistente IA para Consultas sobre el Proyecto")
                        st.write("Pregunta a la IA sobre modificaciones, costes adicionales, viabilidad, etc.")
                        query = st.text_input("Escribe tu pregunta:", key=f"ia_query_{proj['id']}")
                        if st.button("Consultar IA", key=f"ia_btn_{proj['id']}"):
                            if query.strip():
                                # Simulación de respuesta IA (MVP)
                                if "coste" in query.lower() or "precio" in query.lower():
                                    response = f"Basado en el proyecto '{proj['title']}', el coste estimado por m² es de €{proj['price'] / proj['area_m2']:.0f}. Para modificaciones, añade un 10-20% al presupuesto base."
                                elif "habitacion" in query.lower():
                                    response = f"El proyecto tiene {proj['characteristics'].get('habitaciones', 0)} habitaciones. Puedo sugerir agregar una más por €15,000 adicionales."
                                elif "energia" in query.lower():
                                    response = "Se puede integrar paneles solares por €10,000, reduciendo costes energéticos en un 30%."
                                else:
                                    response = f"Gracias por tu pregunta sobre '{query}'. Este proyecto es ideal para familias. Contacta al arquitecto para detalles personalizados."
                                st.success("Respuesta de la IA:")
                                st.write(response)
                            else:
                                st.warning("Por favor, escribe una pregunta.")
                
                    with tab_comprar:
                        st.subheader("¡Contrata tu Proyecto Ahora!")
                        st.write(f"**Precio Total del Proyecto:** €{proj['price']}")
                        st.write("**Lo que Incluye:**")
                        st.markdown("- ✅ Planos técnicos completos (DWG)\n- ✅ Modelo 3D interactivo\n- ✅ Asesoría inicial con arquitecto\n- ✅ Gemelo digital\n- ✅ Preparación para permisos")
                        
                        # Ofertas especiales
                        descuento = proj['price'] * 0.1  # 10% descuento
                        precio_descuento = proj['price'] - descuento
                        st.success(f"🎉 Oferta Especial: 10% de descuento si contratas hoy - **€{precio_descuento:.0f}** en lugar de €{proj['price']}")
                        
                        st.write("**Financiación Disponible:** Hasta 60 meses sin intereses (consultar condiciones).")
                        st.write("**Garantía:** 2 años en construcción, asesoría post-venta.")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Contratar con Descuento (€{precio_descuento:.0f})", key=f"hire_discount_{proj['id']}"):
                                st.success("¡Proyecto contratado con descuento! (Simulación MVP)")
                                st.balloons()
                                st.info("Recibirás un email con los detalles y contrato.")
                        with col2:
                            if st.button(f"Contratar Precio Normal (€{proj['price']})", key=f"hire_normal_{proj['id']}"):
                                st.success("¡Proyecto contratado! (Simulación MVP)")
                                st.info("Próximamente: Integración con pagos seguros.")
                        
                        st.caption("Nota: Esta es una simulación para el MVP. El proceso real incluirá contratos legales y pagos seguros.")

    # details & reserve
    if selected_plot_local:
        pid = selected_plot_local
        st.session_state["selected_plot"] = pid  # sync
        st.markdown("---")
        st.subheader("Detalle finca")
        p = next((x for x in plots if x["id"]==pid), None)
        if p:
            img_path = get_plot_image_path(p)
            st.image(img_path, width=400)
            st.write(f"**Título:** {p['title']}")
            st.write(f"**Superficie:** {p.get('surface_m2')} m²")
            st.write(f"**Precio:** €{p.get('price')}")
            st.write(f"**Referencia catastral:** {p.get('cadastral_ref', 'N/A')}")
            
            # Additional actions
            st.subheader("🔧 Acciones Disponibles")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Extraer Datos Catastrales", key=f"extract_{pid}"):
                    st.info("Funcionalidad de extracción catastral - Implementada en módulo separado")
            with col2:
                if st.button("🔍 Examinar Edificabilidad", key=f"edificability_{pid}"):
                    st.info("Análisis de edificabilidad disponible en Design Assistant")
            with col3:
                if st.button("📋 Generar Informe", key=f"report_{pid}"):
                    st.info("Generando informe detallado...")
            
            st.subheader("💰 Opciones de Compra")
            if st.button("Reservar 10%", key=f"reserve_10_detail_{pid}"):
                amount = (p.get("price") or 0) * 0.10
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="reservation")
                st.success(f"Reserva simulada: {rid} — {amount}€")
            if st.button("Comprar (100%)", key=f"purchase_100_detail_{pid}"):
                amount = (p.get("price") or 0)
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="purchase")
                st.success(f"Compra simulada: {rid} — {amount}€")