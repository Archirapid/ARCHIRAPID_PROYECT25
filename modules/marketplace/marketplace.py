# modules/marketplace/marketplace.py
import streamlit as st
from modules.marketplace.utils import list_published_plots, save_upload, reserve_plot
from streamlit_folium import st_folium
import folium
import uuid

def main():
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
            st.write(f"**{p['title']}** — {p.get('surface_m2')} m² — €{p.get('price')}")
            if st.button(f"Ver {p['id']}", key=f"view_{p['id']}"):
                st.session_state["selected_plot"] = p["id"]

    with right:
        m = folium.Map(location=[40.0,-4.0], zoom_start=6, tiles="CartoDB positron")
        for p in plots:
            lat = p['lat'] or 40.0
            lon = p['lon'] or -4.0
            popup_html = f"""
            <div style='width:220px'>
                <h4>{p['title']}</h4>
                <div>{p.get('surface_m2')} m² · €{p.get('price')}</div>
                <a href='?plot_id={p['id']}'>Ver detalles</a>
            </div>
            """
            folium.Marker([lat,lon], popup=popup_html).add_to(m)
        st_folium(m, width=700, height=600)

    # details & reserve
    if "selected_plot" in st.session_state:
        pid = st.session_state["selected_plot"]
        st.markdown("---")
        st.subheader("Detalle finca")
        p = next((x for x in plots if x["id"]==pid), None)
        if p:
            st.write(p)
            st.write("Opciones:")
            if st.button("Reservar 10%"):
                amount = (p.get("price") or 0) * 0.10
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="reservation")
                st.success(f"Reserva simulada: {rid} — {amount}€")
            if st.button("Comprar (100%)"):
                amount = (p.get("price") or 0)
                rid = reserve_plot(pid, "Demo buyer", "demo@example.com", amount, kind="purchase")
                st.success(f"Compra simulada: {rid} — {amount}€")