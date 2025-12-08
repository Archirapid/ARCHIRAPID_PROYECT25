# modules/marketplace/client_panel.py
import streamlit as st
from modules.marketplace.utils import db_conn
import json

def main():
    st.title("👤 Panel de Cliente - ARCHIRAPID")
    
    # Login simple por email
    if "client_logged_in" not in st.session_state:
        st.session_state["client_logged_in"] = False
    
    if not st.session_state["client_logged_in"]:
        st.subheader("🔐 Acceso al Panel de Cliente")
        st.info("Introduce el email que usaste al realizar tu compra/reserva")
        
        email = st.text_input("Email de cliente", placeholder="tu@email.com")
        
        if st.button("Acceder", type="primary"):
            if email:
                # Verificar si el email tiene transacciones
                conn = db_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reservations WHERE buyer_email=?", (email,))
                transactions = cursor.fetchall()
                conn.close()
                
                if transactions:
                    st.session_state["client_logged_in"] = True
                    st.session_state["client_email"] = email
                    st.success(f"✅ Acceso concedido para {email}")
                    st.rerun()
                else:
                    st.error("No se encontraron transacciones para este email")
            else:
                st.error("Por favor introduce tu email")
        
        st.markdown("---")
        st.info("💡 **Nota:** Si acabas de realizar una compra, usa el email que proporcionaste en el formulario de datos personales.")
        st.stop()
    
    # Panel de cliente logueado
    client_email = st.session_state.get("client_email")
    
    # Botón de cerrar sesión en sidebar
    with st.sidebar:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["client_logged_in"] = False
            if "client_email" in st.session_state:
                del st.session_state["client_email"]
            st.rerun()
    
    st.success(f"🎉 Bienvenido/a {client_email}")
    
    # Obtener transacciones del cliente
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.plot_id, r.buyer_name, r.amount, r.kind, r.created_at, 
               p.title, p.surface_m2, p.price, p.photo_paths
        FROM reservations r
        LEFT JOIN plots p ON r.plot_id = p.id
        WHERE r.buyer_email = ?
        ORDER BY r.created_at DESC
    """, (client_email,))
    
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        st.warning("No tienes transacciones registradas")
        st.stop()
    
    # Mostrar resumen de transacciones
    st.subheader("📋 Mis Transacciones")
    
    for trans in transactions:
        trans_id, plot_id, buyer_name, amount, kind, created_at, plot_title, surface_m2, price, photo_paths = trans
        
        with st.expander(f"🏠 {plot_title} - {kind.upper()}", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Mostrar imagen de la finca
                if photo_paths:
                    try:
                        paths = json.loads(photo_paths)
                        if paths and isinstance(paths, list):
                            img_path = f"uploads/{paths[0]}"
                            if os.path.exists(img_path):
                                st.image(img_path, width=200)
                    except:
                        st.image("assets/fincas/image1.jpg", width=200)
                else:
                    st.image("assets/fincas/image1.jpg", width=200)
            
            with col2:
                st.markdown(f"**📋 ID Transacción:** `{trans_id}`")
                st.markdown(f"**🏠 Finca:** {plot_title}")
                st.markdown(f"**📏 Superficie:** {surface_m2} m²")
                st.markdown(f"**💰 Precio Total:** €{price}")
                st.markdown(f"**💵 Cantidad Pagada:** €{amount}")
                st.markdown(f"**📅 Fecha:** {created_at}")
                st.markdown(f"**✅ Tipo:** {kind.upper()}")
    
    st.markdown("---")
    
    # Opciones de acción
    st.subheader("🎯 ¿Qué deseas hacer?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏡 DISEÑAR VIVIENDA")
        st.write("Crea tu casa ideal con nuestros arquitectos")
        if st.button("🚀 Ir al Diseñador", key="go_designer_panel", use_container_width=True, type="primary"):
            st.success("🎨 Redirigiendo al Diseñador de Vivienda...")
            st.info("En esta sección podrás diseñar tu vivienda personalizada")
    
    with col2:
        st.markdown("#### 📐 VER PROYECTOS")
        st.write("Explora proyectos compatibles con tu finca")
        if st.button("📋 Ver Proyectos", key="go_projects_panel", use_container_width=True, type="primary"):
            st.success("📐 Mostrando proyectos disponibles...")
            st.info("Aquí verás todos los proyectos arquitectónicos compatibles")
    
    st.markdown("---")
    
    # Opciones adicionales
    st.subheader("🔧 Opciones Adicionales")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🗺️ Volver al Marketplace", key="back_to_marketplace", use_container_width=True):
            st.success("🏠 Volviendo al marketplace...")
            st.info("Puedes seguir explorando más fincas y proyectos")
    
    with col_b:
        if st.button("📧 Contactar Soporte", key="contact_support_panel", use_container_width=True):
            st.info("📧 Contacto con soporte:")
            st.write("**Email:** soporte@archirapid.com")
            st.write("**Teléfono:** +34 900 123 456")
    
    with col_c:
        if st.button("📄 Descargar Documentación", key="download_docs", use_container_width=True):
            st.info("📄 Descarga disponible próximamente")
            st.write("Pronto podrás descargar todos los documentos de tu transacción")

# Añadir import necesario
import os
