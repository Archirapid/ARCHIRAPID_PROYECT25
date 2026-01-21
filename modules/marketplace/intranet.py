# modules/marketplace/intranet.py - GESTIÓN INTERNA DE LA EMPRESA
import streamlit as st
from modules.marketplace.utils import db_conn, list_published_plots, list_projects
import json

def main():
    st.title("🔐 Intranet — Gestión Interna de ARCHIRAPID")

    # Verificar si ya está logueado como admin
    if st.session_state.get("rol") == "admin":
        st.success("✅ Acceso autorizado a Intranet (sesión activa)")
    else:
        # SOLO ACCESO CON CONTRASEÑA DE ADMIN
        password = st.text_input("Contraseña de Acceso Administrativo", type="password")
        if password != "admin123":  # Contraseña de admin
            st.warning("🔒 Acceso restringido. Solo personal autorizado de ARCHIRAPID.")
            st.info("Si eres cliente o profesional, utiliza los botones de la página principal.")
            return
        st.success("✅ Acceso autorizado a Intranet")

    # PANEL DE GESTIÓN INTERNA
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Gestión de Fincas", "🏗️ Gestión de Proyectos", "💰 Ventas y Transacciones", "📞 Consultas"])

    with tab1:
        try:
            st.header("Gestión de Fincas Publicadas")
            plots = list_published_plots()
            if plots:
                for p in plots:
                    with st.expander(f"Finca: {p['title']}"):
                        st.write(f"**ID:** {p['id']}")
                        st.write(f"**Superficie:** {p['surface_m2']} m²")
                        st.write(f"**Precio:** €{p['price']}")
                        st.write(f"**Status:** {p.get('status', 'Pendiente')}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Aprobar {p['id']}", key=f"approve_plot_{p['id']}"):
                                st.success("Finca aprobada (Admin)")
                        with col2:
                            if st.button(f"Rechazar {p['id']}", key=f"reject_plot_{p['id']}"):
                                st.info("Funcionalidad próximamente")
            else:
                st.info("No hay fincas publicadas")
        except Exception as e:
            st.error(f"Error en Gestión de Fincas: {e}")

    with tab2:
        try:
            st.header("Gestión de Proyectos Arquitectónicos")
            projects = list_projects()
            if projects:
                for proj in projects:
                    with st.expander(f"Proyecto: {proj['title']}"):
                        # Imagen principal o fallback
                        img_path = proj['foto_principal'] if proj['foto_principal'] else "assets/fincas/image1.jpg"
                        st.image(img_path, width=120, caption="Imagen principal")
                        st.write(f"**Arquitecto:** {proj['architect_name']}")
                        st.write(f"**Precio:** €{proj['price']}")
                        st.write(f"**Área:** {proj['area_m2']} m²")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Aprobar Proyecto {proj['id']}", key=f"approve_proj_{proj['id']}"):
                                st.success("Proyecto aprobado (Admin)")
                        with col2:
                            if st.button(f"Rechazar Proyecto {proj['id']}", key=f"reject_proj_{proj['id']}"):
                                st.info("Funcionalidad próximamente")
            else:
                st.info("Próximamente. No hay proyectos.")
        except Exception as e:
            st.error(f"Error en Gestión de Proyectos: {e}")

    with tab3:
        try:
            st.header("Ventas y Transacciones")
            st.info("📊 Módulo de analítica en preparación. Próximamente verás aquí el flujo de caja.")
            conn = db_conn(); c = conn.cursor()
            c.execute("SELECT * FROM reservations ORDER BY created_at DESC")
            reservations = c.fetchall()
            conn.close()
            if reservations:
                for r in reservations:
                    st.write(f"**Reserva ID:** {r[0]} | **Finca:** {r[1]} | **Comprador:** {r[2]} | **Monto:** €{r[4]} | **Tipo:** {r[5]}")
                    if st.button(f"Confirmar {r[0]}", key=f"confirm_{r[0]}"):
                        st.success("Reserva confirmada (Admin)")
            else:
                st.info("Próximamente. No hay reservas.")
        except Exception as e:
            st.error(f"Error en Ventas y Transacciones: {e}")

    with tab4:
        try:
            st.header("Consultas y Soporte")
            st.info("📊 Módulo de analítica en preparación. Próximamente verás aquí el flujo de caja.")
            st.info("Próximamente. Panel de consultas y soporte.")
        except Exception as e:
            st.error(f"Error en Consultas y Soporte: {e}")