# modules/marketplace/marketplace.py
import streamlit as st
from modules.marketplace.utils import list_published_plots, save_upload, reserve_plot
from streamlit_folium import st_folium
import folium
import uuid
import base64

# Map plot ids to images
PLOT_IMAGES = {
    'finca_es_malaga': 'assets/fincas/image1.jpg',
    'finca_es_madrid': 'assets/fincas/image2.jpg',
    'finca_pt_lisboa': 'assets/fincas/image3.jpg',
}

def get_image_base64(image_path):
    """Convert image to base64 for embedding in HTML."""
    try:
        with open(image_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except:
        return ""

def main():
    # Handle URL params for plot selection
    if "selected_plot" not in st.session_state:
        selected_from_url = st.query_params.get("selected_plot")
        if selected_from_url:
            st.session_state["selected_plot"] = selected_from_url
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
        st.header("Resultados")
        for p in plots:
            img_path = PLOT_IMAGES.get(p['id'], 'assets/fincas/image1.jpg')
            st.image(img_path, width=200)
            st.write(f"**{p['title']}** — {p.get('surface_m2')} m² — €{p.get('price')}")
            if st.button(f"Ver detalles {p['id']}", key=f"view_{p['id']}"):
                st.session_state["selected_plot"] = p["id"]

    with right:
        m = folium.Map(location=[40.1,-4.0], zoom_start=6, tiles="CartoDB positron")
        for p in plots:
            lat = p['lat'] or 40.1
            lon = p['lon'] or -4.0
            img_path = PLOT_IMAGES.get(p['id'], 'assets/fincas/image1.jpg')
            img_base64 = get_image_base64(img_path)
            icon = folium.CustomIcon(f'data:image/jpeg;base64,{img_base64}', icon_size=(60, 45))
            popup_html = f"""
            <div style='width:220px'>
                <h4>{p['title']}</h4>
                <div>{p.get('surface_m2')} m² · €{p.get('price')}</div>
                <a href='?selected_plot={p["id"]}' target='_self'>Ver detalles aquí</a>
            </div>
            """
            folium.Marker([lat,lon], icon=icon, popup=popup_html).add_to(m)
        st_folium(m, width=700, height=600)

    # details & reserve
    if "selected_plot" in st.session_state:
        pid = st.session_state["selected_plot"]
        st.markdown("---")
        st.subheader("Detalle finca")
        p = next((x for x in plots if x["id"]==pid), None)
        if p:
            img_path = PLOT_IMAGES.get(p['id'], 'assets/fincas/image1.jpg')
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