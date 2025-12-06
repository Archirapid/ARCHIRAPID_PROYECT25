# modules/marketplace/owners.py
import streamlit as st
from modules.marketplace.utils import save_upload, create_plot_record, get_user_by_email, db_conn, get_client_proposals
from pathlib import Path
import uuid, json
from datetime import datetime
import geopy.geocoders

def main():
    st.header("Panel de Propietarios — ARCHIRAPID")

    if "geocoded_lat" not in st.session_state:
        st.session_state.geocoded_lat = None
        st.session_state.geocoded_lon = None

    # sencillo login/registro por email
    email = st.text_input("Tu email (propietario)")
    name = st.text_input("Nombre completo")
    if st.button("Identificar / Registrar"):
        if not email or not name:
            st.error("Introduce nombre y email.")
        else:
            # create simple user if not exists
            cur = get_user_by_email(email)
            if cur:
                st.success("Usuario encontrado.")
                user_id = cur[0]
            else:
                user_id = uuid.uuid4().hex
                from modules.marketplace.utils import insert_user
                insert_user({"id":user_id,"name":name,"email":email,"role":"owner","company":""})
                st.success("Usuario creado.")
            st.session_state["owner_id"] = user_id
            st.session_state["owner_email"] = email

    if "owner_id" not in st.session_state:
        st.info("Identifícate para acceder a tu panel.")
        st.stop()

    # Tabs para panel de propietario
    tab_subir, tab_propuestas = st.tabs(["🏠 Subir Finca", "📨 Propuestas Recibidas"])

    with tab_subir:
        st.subheader("Subir nota registral / catastral (PDF)")
        uploaded_pdf = st.file_uploader("Nota registral (PDF)", type=["pdf"])
        
        st.subheader("Datos del Propietario")
        owner_name = st.text_input("Nombre completo del propietario", value=name if 'name' in locals() else "")
        owner_phone = st.text_input("Teléfono de contacto")
        owner_address = st.text_input("Dirección completa (para geocodificación)")
        
        st.subheader("Datos de la Finca")
        title = st.text_input("Título para la finca", value="Parcela - nuevo registro")
        finca_type = st.selectbox("Tipología", ["Urbana", "Rústica", "Mixta"])
        surface_m2 = st.number_input("Superficie (m²)", min_value=0.0, value=1000.0)
        sanitation = st.selectbox("Saneamiento", ["Conectado a red", "Fosa séptica", "Sin saneamiento", "Otro"])
        price = st.number_input("Precio (EUR)", min_value=0.0, value=50000.0)
        
        # Geocodificación automática
        if owner_address:
            if st.button("Generar coordenadas desde dirección"):
                try:
                    geolocator = geopy.geocoders.Nominatim(user_agent="archirapid")
                    location = geolocator.geocode(owner_address)
                    if location:
                        st.session_state.geocoded_lat = location.latitude
                        st.session_state.geocoded_lon = location.longitude
                        st.success(f"Coordenadas generadas: {location.latitude}, {location.longitude}")
                        st.rerun()
                    else:
                        st.error("Dirección no encontrada.")
                except Exception as e:
                    st.error(f"Error en geocodificación: {e}")
        
        lat_manual = st.number_input("Latitud (opcional, si no usas geocodificación)", value=st.session_state.geocoded_lat or 0.0)
        lon_manual = st.number_input("Longitud (opcional, si no usas geocodificación)", value=st.session_state.geocoded_lon or 0.0)
        
        st.subheader("Fotos de la Finca")
        uploaded_photos = st.file_uploader("Subir fotos (máx 5)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        if len(uploaded_photos) > 5:
            st.error("Máximo 5 fotos.")
            uploaded_photos = uploaded_photos[:5]

        if st.button("Guardar finca"):
            if not uploaded_pdf:
                st.error("Sube la nota registral (PDF).")
            elif not owner_name or not owner_phone or not owner_address:
                st.error("Completa nombre, teléfono y dirección del propietario.")
            elif not title or surface_m2 <= 0:
                st.error("Completa título y superficie válida.")
            else:
                try:
                    # save PDF
                    pdf_path = save_upload(uploaded_pdf, prefix="nota")
                    
                    # save photos
                    photo_paths = []
                    for photo in uploaded_photos:
                        photo_path = save_upload(photo, prefix="finca_photo")
                        photo_paths.append(photo_path)
                    
                    # use manual or geocoded lat/lon
                    final_lat = lat_manual if lat_manual != 0.0 else None
                    final_lon = lon_manual if lon_manual != 0.0 else None
                    
                    plot = {
                        "id": uuid.uuid4().hex,
                        "owner_id": st.session_state["owner_id"],
                        "title": title,
                        "cadastral_ref": None,
                        "surface_m2": surface_m2,
                        "buildable_m2": None,  # to be calculated later
                        "is_urban": finca_type == "Urbana",
                        "vector_geojson": None,  # to be extracted
                        "registry_note_path": pdf_path,
                        "photo_paths": json.dumps(photo_paths),
                        "price": price,
                        "lat": final_lat,
                        "lon": final_lon,
                        "status": "published",
                        "owner_name": owner_name,
                        "owner_phone": owner_phone,
                        "owner_address": owner_address,
                        "sanitation": sanitation,
                        "finca_type": finca_type
                    }
                    create_plot_record(plot)
                    st.success("Finca creada y publicada exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

    with tab_propuestas:
        st.subheader("📨 Propuestas Recibidas de Arquitectos")
        client_email = st.session_state.get("owner_email")
        if client_email:
            proposals = get_client_proposals(client_email)
            if proposals:
                for prop in proposals:
                    with st.expander(f"📋 Propuesta de {prop['architect_name']} - {prop['plot_title']} (€{prop['estimated_budget']:.0f})"):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write(f"**Arquitecto:** {prop['architect_name']}")
                            if prop['architect_company']:
                                st.write(f"**Empresa:** {prop['architect_company']}")
                            st.write(f"**Proyecto:** {prop['project_title'] or 'Sin proyecto asociado'}")
                            st.write(f"**Presupuesto:** €{prop['estimated_budget']:.0f}")
                            st.write(f"**Plazo:** {prop['deadline_days']} días")
                            st.write(f"**Estado:** {prop['status'].capitalize()}")
                        with col2:
                            st.write(f"**Descripción:** {prop['proposal_text']}")
                            if prop['project_description']:
                                st.write(f"**Proyecto Detalles:** {prop['project_description'][:200]}...")
                            st.write(f"**Finca:** {prop['plot_title']} ({prop['plot_surface']:.0f} m²)")
                            if prop['sketch_image_path']:
                                st.image(f"uploads/{prop['sketch_image_path']}", width=300, caption="Boceto")
                            # Botones Aceptar/Rechazar (para paso 5, pero agregar placeholders)
                            if prop['status'] == 'pending':
                                col_a, col_r = st.columns(2)
                                with col_a:
                                    if st.button(f"✅ Aceptar (€{prop['total_cliente']:.0f})", key=f"accept_{prop['id']}"):
                                        st.info("Funcionalidad de aceptar - Próximamente")
                                with col_r:
                                    if st.button("❌ Rechazar", key=f"reject_{prop['id']}"):
                                        st.info("Funcionalidad de rechazar - Próximamente")
            else:
                st.info("No has recibido propuestas aún. ¡Publica una finca para empezar!")
        else:
            st.error("Email no disponible.")

# Qué hace: permite registro simple de propietario (email) y subir nota PDF y crear registro de finca (en un MVP se publica inmediatamente). Más adelante lo conectamos para ejecución automática del pipeline de extracción.