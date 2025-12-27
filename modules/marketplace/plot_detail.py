# modules/marketplace/plot_detail.py
"""
Página de detalles completa de una finca
Muestra toda la información necesaria para que el cliente decida comprar
"""
import streamlit as st
import os
import json
import base64
from pathlib import Path
from modules.marketplace.utils import calculate_edificability, reserve_plot
from modules.marketplace.catastro_api import fetch_by_ref_catastral
from modules.marketplace.marketplace import get_plot_image_path
from src import db

def get_all_plot_images(plot):
    """Obtener todas las imágenes de la finca"""
    images = []
    if plot.get('photo_paths'):
        try:
            paths = json.loads(plot['photo_paths']) if isinstance(plot.get('photo_paths'), str) else plot.get('photo_paths')
            if paths and isinstance(paths, list):
                for path in paths:
                    img_path = f"uploads/{path}"
                    if os.path.exists(img_path):
                        images.append(img_path)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Fallback a imagen única
    if not images:
        single_img = get_plot_image_path(plot)
        if single_img and os.path.exists(single_img):
            images.append(single_img)
    
    return images if images else ['assets/fincas/image1.jpg']

def show_plot_detail_page(plot_id: str):
    """Muestra la página completa de detalles de una finca"""
    
    # Obtener datos de la finca
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plots WHERE id = ?", (plot_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        st.error("❌ Finca no encontrada")
        if st.button("← Volver al mapa"):
            if 'selected_plot' in st.session_state:
                del st.session_state['selected_plot']
            st.rerun()
        return
    
    # Convertir row a dict
    plot = dict(row)
    
    # Título principal
    st.title(f"🏡 {plot.get('title', 'Finca sin título')}")
    
    # Botón volver
    if st.button("← Volver al mapa", key="back_to_map"):
        if 'selected_plot' in st.session_state:
            del st.session_state['selected_plot']
        st.rerun()
    
    st.markdown("---")
    
    # Galería de imágenes
    st.subheader("📸 Galería de Imágenes")
    images = get_all_plot_images(plot)
    
    if len(images) > 0:
        # Mostrar primera imagen grande
        col_img_main, col_img_thumb = st.columns([2, 1])
        with col_img_main:
            st.image(images[0], use_container_width=True, caption=plot.get('title', ''))
        
        with col_img_thumb:
            if len(images) > 1:
                st.caption("Más imágenes:")
                for i, img_path in enumerate(images[1:4]):  # Máximo 3 thumbnails
                    st.image(img_path, width=150)
    
    st.markdown("---")
    
    # Información principal en columnas
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.subheader("📊 Información General")
        
        superficie = plot.get('surface_m2') or plot.get('m2') or 0
        precio = plot.get('price') or 0
        provincia = plot.get('province', 'N/A')
        localidad = plot.get('locality', plot.get('address', 'N/A'))
        
        st.metric("💰 Precio", f"€{precio:,.0f}")
        st.metric("📏 Superficie Total", f"{superficie} m²")
        
        # Edificabilidad
        edificabilidad = calculate_edificability(superficie, 0.33)
        st.metric("🏗️ Superficie Construible (33%)", f"{edificabilidad:.0f} m²")
        
        st.markdown(f"**📍 Ubicación:** {localidad}, {provincia}")
        st.markdown(f"**🏷️ Tipo:** {plot.get('type', 'Urbano')}")
        
        if plot.get('catastral_ref'):
            st.markdown(f"**📋 Referencia Catastral:** `{plot['catastral_ref']}`")
    
    with col_info2:
        st.subheader("📍 Ubicación en Mapa")
        try:
            import folium
            import streamlit.components.v1 as components
            
            lat = float(plot.get('lat', 40.4168))
            lon = float(plot.get('lon', -3.7038))
            
            m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB positron")
            folium.Marker(
                [lat, lon],
                popup=plot.get('title', 'Finca'),
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(m)
            
            components.html(m._repr_html_(), height=300)
        except Exception as e:
            st.error(f"Error mostrando mapa: {e}")
    
    st.markdown("---")
    
    # Descripción
    if plot.get('description'):
        st.subheader("📝 Descripción")
        st.write(plot['description'])
        st.markdown("---")
    
    # Datos catastrales
    st.subheader("📋 Datos Catastrales")
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.markdown(f"**Superficie:** {superficie} m²")
        st.markdown(f"**Edificabilidad máxima:** {edificabilidad:.0f} m² (33%)")
        if plot.get('catastral_ref'):
            st.markdown(f"**Ref. Catastral:** `{plot['catastral_ref']}`")
    
    with col_cat2:
        if plot.get('registry_note_path'):
            try:
                note_path = plot['registry_note_path']
                if os.path.exists(note_path):
                    with open(note_path, 'rb') as f:
                        pdf_data = f.read()
                        b64 = base64.b64encode(pdf_data).decode()
                        href = f"data:application/pdf;base64,{b64}"
                        st.markdown(f'[📄 Descargar Nota Simple Registral]({href})', unsafe_allow_html=True)
            except Exception:
                st.info("Nota registral disponible en el portal del cliente")
        else:
            st.info("Nota registral no disponible")
    
    st.markdown("---")
    
    # Acciones: Reservar o Comprar
    st.subheader("💳 Acciones")
    
    # Verificar si ya está registrado
    buyer_email = st.session_state.get('buyer_email')
    buyer_name = st.session_state.get('buyer_name')
    
    if not buyer_email or not buyer_name:
        # Formulario de registro primero
        st.info("📝 Por favor completa tus datos para proceder con la reserva o compra")
        
        with st.form("register_buyer"):
            col_reg1, col_reg2 = st.columns(2)
            with col_reg1:
                nombre = st.text_input("Nombre *", key="reg_nombre")
                apellidos = st.text_input("Apellidos *", key="reg_apellidos")
                email_reg = st.text_input("Email *", key="reg_email")
                telefono = st.text_input("Teléfono *", key="reg_telefono")
            with col_reg2:
                direccion = st.text_area("Dirección *", key="reg_direccion")
                provincia_reg = st.text_input("Provincia *", key="reg_provincia")
                pais = st.selectbox("País *", ["España", "Portugal", "Otro"], key="reg_pais", index=0)
            
            submitted_reg = st.form_submit_button("✅ Registrar y Continuar", type="primary")
            
            if submitted_reg:
                if not all([nombre, apellidos, email_reg, telefono, direccion, provincia_reg]):
                    st.error("Por favor completa todos los campos obligatorios (*)")
                else:
                    st.session_state['buyer_name'] = f"{nombre} {apellidos}"
                    st.session_state['buyer_email'] = email_reg
                    st.session_state['buyer_phone'] = telefono
                    st.session_state['buyer_address'] = direccion
                    st.session_state['buyer_province'] = provincia_reg
                    st.session_state['buyer_country'] = pais
                    st.success("✅ Datos guardados. Ahora puedes reservar o comprar.")
                    st.rerun()
    else:
        # Ya registrado, mostrar botones de acción
        st.success(f"✅ Registrado como: {buyer_name} ({buyer_email})")
        
        col_reserve, col_buy = st.columns(2)
        
        with col_reserve:
            reservation_amount = precio * 0.10
            st.markdown(f"### 💰 Reservar (10%)")
            st.markdown(f"**Importe:** €{reservation_amount:,.0f}")
            st.caption("Reserva la finca pagando el 10% del precio total")
            
            if st.button("🔒 Reservar Finca", key="btn_reserve", use_container_width=True, type="primary"):
                try:
                    rid = reserve_plot(
                        plot_id,
                        buyer_name,
                        buyer_email,
                        reservation_amount,
                        kind="reservation"
                    )
                    st.success(f"✅ Reserva realizada exitosamente!")
                    st.info(f"**ID de Reserva:** `{rid}`")
                    st.info(f"**Importe:** €{reservation_amount:,.0f}")
                    st.info(f"📧 Recibirás un email de confirmación en {buyer_email}")
                    st.info(f"🔗 Accede a tu portal de cliente para gestionar tu reserva")
                    
                    # Guardar email en session_state para auto-login
                    st.session_state['auto_owner_email'] = buyer_email
                    st.balloons()
                    st.info("🔄 Redirigiendo a tu portal de cliente...")
                    # Redirigir a portal cliente (será manejado en app.py)
                    st.session_state['role'] = 'cliente'
                    st.session_state['current_page'] = 'client_portal'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar la reserva: {str(e)}")
        
        with col_buy:
            st.markdown(f"### 🏠 Comprar (100%)")
            st.markdown(f"**Importe Total:** €{precio:,.0f}")
            st.caption("Compra la finca completa")
            
            if st.button("💳 Comprar Finca", key="btn_buy", use_container_width=True, type="primary"):
                try:
                    rid = reserve_plot(
                        plot_id,
                        buyer_name,
                        buyer_email,
                        precio,
                        kind="purchase"
                    )
                    st.success(f"✅ Compra realizada exitosamente!")
                    st.info(f"**ID de Transacción:** `{rid}`")
                    st.info(f"**Importe:** €{precio:,.0f}")
                    st.info(f"📧 Recibirás un email de confirmación en {buyer_email}")
                    st.info(f"🔗 Accede a tu portal de cliente para gestionar tu compra")
                    
                    # Guardar email en session_state para auto-login
                    st.session_state['auto_owner_email'] = buyer_email
                    st.balloons()
                    st.info("🔄 Redirigiendo a tu portal de cliente...")
                    # Redirigir a portal cliente (será manejado en app.py)
                    st.session_state['role'] = 'cliente'
                    st.session_state['current_page'] = 'client_portal'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar la compra: {str(e)}")

