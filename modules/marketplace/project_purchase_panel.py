"""
Panel de Compra de Proyectos Arquitectónicos
"""

import streamlit as st
from modules.marketplace. utils import db_conn
import json
import os


def show_project_purchase_panel(project_id:  str, client_email: str):
    """Panel de compra de proyecto"""
    
    st.title("🏗️ Compra de Proyecto Arquitectónico")
    
    # Obtener datos del proyecto
    conn = db_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, m2_construidos, area_m2, price, estimated_cost,
               price_memoria, price_cad, property_type, foto_principal, galeria_fotos,
               memoria_pdf, planos_pdf, planos_dwg, modelo_3d_glb, vr_tour, energy_rating,
               architect_name, characteristics_json, habitaciones, banos, garaje, plantas,
               m2_parcela_minima, m2_parcela_maxima, certificacion_energetica, tipo_proyecto
        FROM projects
        WHERE id = ?
    """, (project_id,))
    
    proyecto = cursor.fetchone()
    conn.close()
    
    if not proyecto:
        st.error(f"❌ Proyecto no encontrado: {project_id}")
        return
    
    # Desempaquetar
    (pid, title, desc, m2_construidos, area_m2, price, estimated_cost,
     price_memoria, price_cad, property_type, foto_principal, galeria_fotos,
     memoria_pdf, planos_pdf, planos_dwg, modelo_3d_glb, vr_tour, energy_rating,
     architect_name, characteristics_json, habitaciones, banos, garaje, plantas,
     m2_parcela_minima, m2_parcela_maxima, certificacion_energetica, tipo_proyecto) = proyecto
    
    # Calcular superficie
    surface = m2_construidos or area_m2 or 0
    beds = habitaciones or 0
    baths = banos or 0
    piscina = False  # TODO: parse from characteristics_json if needed
    
    # Cliente
    st.success(f"👤 Cliente: **{client_email. upper()}**")
    st.markdown("---")
    
    # Datos del proyecto
    st.header(f"📐 {title}")
    
    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        if foto_principal and os.path.exists(foto_principal):
            st.image(foto_principal, use_column_width=True, caption="Vista principal")
        else:
            st.info("📷 Sin imagen")
    
    with col_info:
        st.subheader("📊 Características")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏠 Superficie", f"{surface or 0} m²")
            st.metric("🛏️ Habitaciones", beds or 0)
            st.metric("🚿 Baños", baths or 0)
        with col2:
            st.metric("🏊 Piscina", "Sí" if piscina else "No")
            st.metric("🚗 Garaje", "Sí" if garaje else "No")
            st.metric("🏢 Plantas", plantas or 0)
    
    if desc:
        with st.expander("📝 Descripción"):
            st.write(desc)
    
    st.markdown("---")
    
    # Opciones de compra
    st. header("💰 Opciones de Compra")
    
    precio_pdf = price_memoria or 1800
    precio_cad = price_cad or 2500
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px;">
            <h3 style="color: #4CAF50;">📄 Proyecto PDF</h3>
            <ul>
                <li>Memoria completa</li>
                <li>Planos en PDF</li>
                <li>Ficha técnica</li>
            </ul>
            <h2 style="color: #4CAF50; text-align: center;">1.800 €</h2>
        </div>
        """, unsafe_allow_html=True)
        comprar_pdf = st.checkbox("✅ Seleccionar PDF", key="pdf")
    
    with col2:
        st.markdown("""
        <div style="border: 2px solid #2196F3; padding: 20px; border-radius: 10px;">
            <h3 style="color: #2196F3;">📐 Proyecto CAD</h3>
            <ul>
                <li>Todo lo del PDF +</li>
                <li>Archivos DWG editables</li>
                <li>Modelo 3D</li>
            </ul>
            <h2 style="color: #2196F3; text-align: center;">2.500 €</h2>
        </div>
        """, unsafe_allow_html=True)
        comprar_cad = st.checkbox("✅ Seleccionar CAD", key="cad")
    
    st.markdown("---")
    
    # Servicios adicionales
    st.header("🛠️ Servicios Adicionales (MVP Simulado)")
    
    col1, col2 = st.columns(2)
    with col1:
        s1 = st.checkbox("📋 Visado - 500 €", key="s1")
        s2 = st.checkbox("👷 Constructor - 3. 000 €", key="s2")
        s3 = st.checkbox("🧱 Materiales - 2.500 €", key="s3")
    with col2:
        s4 = st.checkbox("🚰 Fontanería - 3.500 €", key="s4")
        s5 = st. checkbox("💡 Electricidad - 4.200 €", key="s5")
        s6 = st. checkbox("🎨 Decoración - 2.800 €", key="s6")
    
    # Calcular total
    total = 0
    if comprar_pdf and not comprar_cad:
        total += precio_pdf
    elif comprar_cad: 
        total += precio_cad
    
    if s1: total += 500
    if s2: total += 3000
    if s3: total += 2500
    if s4: total += 3500
    if s5: total += 4200
    if s6: total += 2800
    
    st.subheader(f"💵 TOTAL: **{total: ,.2f} €**")
    
    # Botón comprar
    if total > 0:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🛒 COMPRAR AHORA", type="primary", use_column_width=True):
                st.success("✅ Compra realizada (SIMULADO - MVP)")
                st.balloons()
                st.info("Recibirás un email con los detalles")
    else:
        st.warning("⚠️ Selecciona al menos una opción (PDF o CAD)")
    
    st.markdown("---")
    if st.button("⬅️ Volver"):
        st.query_params. clear()
        st.rerun()


def main():
    """Punto de entrada"""
    
    project_id = st.query_params.get("selected_project")
    client_email = st. session_state.get("client_email") or st.session_state.get("buyer_email")
    
    if not project_id:
        st.error("❌ No se especificó proyecto")
        st.stop()
    
    if not client_email:
        st.error("❌ No has iniciado sesión")
        st.info("Regístrate primero en la página del proyecto")
        st.stop()
    
    show_project_purchase_panel(project_id, client_email)


if __name__ == "__main__":
    main()