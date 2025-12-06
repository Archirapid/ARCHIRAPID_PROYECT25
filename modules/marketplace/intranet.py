# modules/marketplace/intranet.py
import streamlit as st
from modules.marketplace.utils import db_conn, list_published_plots, list_projects
import json

def main():
    st.title("🔐 Intranet — Panel de Control (MVP)")

    # Simple auth for demo
    password = st.text_input("Contraseña de Acceso", type="password")
    if password != "admin123":  # demo password
        st.warning("Introduce la contraseña correcta para acceder al panel de control.")
        return

    st.success("✅ Acceso autorizado")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Fincas", "🏗️ Proyectos", "💰 Reservas/Ventas", "📞 Consultas"])

    with tab1:
        st.header("Gestión de Fincas")
        plots = list_published_plots()
        if plots:
            for p in plots:
                with st.expander(f"Finca: {p['title']}"):
                    st.write(f"**ID:** {p['id']}")
                    st.write(f"**Superficie:** {p['surface_m2']} m²")
                    st.write(f"**Precio:** €{p['price']}")
                    st.write(f"**Status:** {p['status']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Aprobar {p['id']}", key=f"approve_plot_{p['id']}"):
                            # In MVP, already approved
                            st.success("Finca ya aprobada (MVP)")
                    with col2:
                        if st.button(f"Rechazar {p['id']}", key=f"reject_plot_{p['id']}"):
                            st.info("Funcionalidad de rechazo próximamente")
        else:
            st.info("No hay fincas publicadas")

    with tab2:
        st.header("Gestión de Proyectos Arquitectónicos")
        projects = list_projects()
        if projects:
            for proj in projects:
                with st.expander(f"Proyecto: {proj['title']}"):
                    st.write(f"**Arquitecto:** {proj['architect_name']}")
                    st.write(f"**Precio:** €{proj['price']}")
                    st.write(f"**Área:** {proj['area_m2']} m²")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Aprobar Proyecto {proj['id']}", key=f"approve_proj_{proj['id']}"):
                            st.success("Proyecto aprobado (MVP)")
                    with col2:
                        if st.button(f"Rechazar Proyecto {proj['id']}", key=f"reject_proj_{proj['id']}"):
                            st.info("Funcionalidad de rechazo próximamente")
        else:
            st.info("No hay proyectos")

    with tab3:
        st.header("Reservas y Ventas")
        conn = db_conn(); c = conn.cursor()
        c.execute("SELECT * FROM reservations ORDER BY created_at DESC")
        reservations = c.fetchall()
        conn.close()
        if reservations:
            for r in reservations:
                st.write(f"**Reserva ID:** {r[0]} | **Finca:** {r[1]} | **Comprador:** {r[2]} | **Monto:** €{r[4]} | **Tipo:** {r[5]}")
                if st.button(f"Confirmar {r[0]}", key=f"confirm_{r[0]}"):
                    st.success("Reserva confirmada (MVP)")
        else:
            st.info("No hay reservas")

    with tab4:
        st.header("Consultas y Contactos")
        st.info("Funcionalidad de consultas próximamente. En MVP, todo se autoriza automáticamente.")