# modules/marketplace/owners.py
import streamlit as st
from modules.marketplace.utils import save_upload, create_plot_record, get_user_by_email, db_conn
from pathlib import Path
import uuid, json
from datetime import datetime

def main():
    st.header("Registro de Fincas — Propietarios")

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

    if "owner_id" not in st.session_state:
        st.info("Identifícate para subir una finca.")
        st.stop()

    st.subheader("Subir nota registral / catastral (PDF)")
    uploaded = st.file_uploader("Nota registral (PDF)", type=["pdf"])
    title = st.text_input("Título para la finca", value="Parcela - nuevo registro")
    price = st.number_input("Precio (EUR)", min_value=0.0, value=50000.0)
    lat = st.text_input("Latitud (opcional)")
    lon = st.text_input("Longitud (opcional)")

    if st.button("Guardar finca"):
        if not uploaded:
            st.error("Sube la nota registral.")
        else:
            # save file
            path = save_upload(uploaded, prefix="nota")
            # call extraction pipeline (we already have scripts). For MVP we assume user ran extraction; here we store path and initial record.
            # We'll attempt to extract via archirapid_extract pipeline if available
            vector_json = None
            surface = None
            buildable = None
            is_urban = True
            try:
                # optional: call Python extractor functions directly
                from archirapid_extract import extract_pdf, ocr_and_preprocess, vectorize_plan, compute_edificability
                # If those modules exist, you can import and run programmatically (skipped to avoid blocking)
            except Exception:
                pass

            plot = {
                "id": uuid.uuid4().hex,
                "owner_id": st.session_state["owner_id"],
                "title": title,
                "cadastral_ref": None,
                "surface_m2": surface,
                "buildable_m2": buildable,
                "is_urban": is_urban,
                "vector_geojson": vector_json,
                "registry_note_path": path,
                "price": price,
                "lat": float(lat) if lat else None,
                "lon": float(lon) if lon else None,
                "status": "published"
            }
            create_plot_record(plot)
            st.success("Finca creada y publicada (modo demo).")

# Qué hace: permite registro simple de propietario (email) y subir nota PDF y crear registro de finca (en un MVP se publica inmediatamente). Más adelante lo conectamos para ejecución automática del pipeline de extracción.