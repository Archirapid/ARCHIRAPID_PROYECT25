import streamlit as st
from modules.marketplace.utils import list_published_plots, save_upload, reserve_plot, list_projects
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
                return paths[0]
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

def main():
    # Handle URL params for plot selection
    selected_from_url = st.query_params.get("selected_plot")
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

    plots = list_published_plots()
    # simple filters
    plots = [p for p in plots if (p["surface_m2"] is None or (p["surface_m2"]>=min_m and p["surface_m2"]<=max_m))]
    if q:
        plots = [p for p in plots if q.lower() in (p.get("title","")+" "+str(p.get("cadastral_ref",""))).lower()]

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
                <a href='?selected_plot={p["id"]}' target='_self'>Ver detalles aquí</a>
            </div>
            """
            folium.Marker([lat,lon], icon=icon, popup=popup_html, id=p['id'], onclick=f"window.location.href = window.location.pathname + '?selected_plot={p['id']}'").add_to(m)
        map_data = st_folium(m, width=700, height=600)

    # Detalles de finca seleccionada
    if selected_plot_local:
        pid = selected_plot_local
        st.session_state["selected_plot"] = pid  # sync
        st.markdown("---")
        st.subheader("Detalle de Finca Seleccionada")
        p = next((x for x in plots if x["id"]==pid), None)
        if p:
            img_path = get_plot_image_path(p)
            st.image(img_path, width=400)
            st.write(f"**Título:** {p['title']}")
            st.write(f"**Superficie:** {p.get('surface_m2')} m²")
            st.write(f"**Precio:** €{p.get('price')}")
            st.write(f"**Referencia catastral:** {p.get('cadastral_ref', 'N/A')}")
            
            # Proyectos compatibles
            from modules.marketplace.utils import calculate_edificability
            edificabilidad = calculate_edificability(p.get('surface_m2', 0))
            projects_all = list_projects()
            compatible_projects = [proj for proj in projects_all if proj['area_m2'] <= edificabilidad]
            
            st.subheader("🔍 Proyectos Arquitectónicos Compatibles")
            if compatible_projects:
                st.write(f"Edificabilidad máxima: {edificabilidad:.0f} m² (33% de superficie)")
                for proj in compatible_projects[:5]:
                    with st.expander(f"🏗️ {proj['title']} - {proj['area_m2']} m² - €{proj['price']}"):
                        st.write(f"**Descripción:** {proj['description']}")
                        st.write(f"**Arquitecto:** {proj['architect_name']}")
                        if proj['company']:
                            st.write(f"**Empresa:** {proj['company']}")
                        if st.button(f"Ver Detalles Completos", key=f"view_proj_{proj['id']}"):
                            st.session_state.selected_proj = proj['id']
            else:
                st.info("No hay proyectos compatibles para esta finca.")
            
            # Additional actions
            st.subheader("💰 Opciones de Compra")
            if st.button("Reservar 10%"):
                amount = (p.get("price") or 0) * 0.10
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="reservation")
                st.success(f"Reserva simulada: {rid} — {amount}€")
            if st.button("Comprar (100%)"):
                amount = (p.get("price") or 0)
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="purchase")
                st.success(f"Compra simulada: {rid} — {amount}€")

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
                if st.button("📊 Extraer Datos Catastrales"):
                    st.info("Funcionalidad de extracción catastral - Implementada en módulo separado")
            with col2:
                if st.button("🔍 Examinar Edificabilidad"):
                    st.info("Análisis de edificabilidad disponible en Design Assistant")
            with col3:
                if st.button("📋 Generar Informe"):
                    st.info("Generando informe detallado...")
            
            st.subheader("💰 Opciones de Compra")
            if st.button("Reservar 10%"):
                amount = (p.get("price") or 0) * 0.10
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="reservation")
                st.success(f"Reserva simulada: {rid} — {amount}€")
            if st.button("Comprar (100%)"):
                amount = (p.get("price") or 0)
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="purchase")
                st.success(f"Compra simulada: {rid} — {amount}€")