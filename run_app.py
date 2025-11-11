import streamlit as st
import os
import uuid
from datetime import datetime

from src.architect_manager import ArchitectManager
from src.property_manager import PropertyManager

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

st.set_page_config(page_title="ARCHIRAPID MVP (light)", layout="wide")

st.markdown("""
<nav style='background:#f8f9fa;padding:8px;border-radius:6px;'>
  <a href='/?page=home' style='margin-right:12px;'>Inicio</a>
  <a href='/?page=plots' style='margin-right:12px;'>Registro Fincas</a>
  <a href='/?page=architects' style='margin-right:12px;'>Arquitectos</a>
</nav>
""", unsafe_allow_html=True)

qp = st.experimental_get_query_params()
page = qp.get("page", ["home"])[0]

arch_manager = ArchitectManager(DB_PATH, UPLOADS)
prop_manager = PropertyManager(DB_PATH, UPLOADS)

if page == "home":
    st.title("ARCHIRAPID — Inicio")
    st.write("Bienvenido al entorno de pruebas. Use la navegación para probar las secciones principales.")

elif page == "plots":
    st.title("Registro de Fincas (simple)")
    with st.form("registro_finca"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Título/Nombre de la Finca*")
            province = st.text_input("Provincia*")
            m2 = st.number_input("Superficie (m²)*", min_value=1, value=100)
            lat = st.number_input("Latitud*", value=40.0)
            lon = st.number_input("Longitud*", value=-3.0)
        with col2:
            price = st.number_input("Precio (€)*", min_value=0, value=100000)
            owner_name = st.text_input("Nombre del Propietario")
            owner_email = st.text_input("Email del Propietario")
            description = st.text_area("Descripción")

        images = st.file_uploader("Imágenes (opc.)", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        registry_note = st.file_uploader("Nota simple (PDF, opc.)", type=["pdf"])
        submitted = st.form_submit_button("Registrar Finca")

    if submitted:
        if not all([title, province, m2, lat, lon, price]):
            st.error("Los campos marcados con * son obligatorios")
        else:
            registry_path = None
            if registry_note:
                fname = f"registry_{uuid.uuid4().hex}.pdf"
                registry_path = os.path.join(UPLOADS, fname)
                with open(registry_path, "wb") as f:
                    f.write(registry_note.getbuffer())

            data = {
                'title': title,
                'province': province,
                'locality': '',
                'type': 'rural',
                'm2': int(m2),
                'height': 6.0,
                'price': float(price),
                'lat': float(lat),
                'lon': float(lon),
                'owner_name': owner_name,
                'owner_email': owner_email,
                'description': description,
                'registry_note_path': registry_path
            }
            success, result = prop_manager.register_property(data, image_files=images)
            if success:
                st.success("Finca registrada con éxito")
            else:
                st.error(f"Error registrando finca: {result}")

elif page == "architects":
    st.title("Portal de Arquitectos")
    tab = st.radio("Seleccione una opción:", ["Registro", "Acceso", "Panel de Control"]) 

    if tab == "Registro":
        with st.form("registro_arch"):
            name = st.text_input("Nombre completo*")
            email = st.text_input("Email*")
            phone = st.text_input("Teléfono")
            company = st.text_input("Empresa/Estudio")
            nif = st.text_input("NIF/CIF")
            submit = st.form_submit_button("Registrar")
        if submit:
            if not name or not email:
                st.error("Nombre y email obligatorios")
            else:
                ok, res = arch_manager.register_architect({'name': name, 'email': email, 'phone': phone, 'company': company, 'nif': nif})
                if ok:
                    st.success("Arquitecto registrado")
                else:
                    st.error(res)

    elif tab == "Acceso":
        email_login = st.text_input("Email registrado")
        if st.button("Acceder"):
            if email_login:
                architect = arch_manager.get_architect(email=email_login)
                if architect:
                    st.success(f"Bienvenido/a {architect['name']}")
                    st.session_state['arch_id'] = architect['id']
                else:
                    st.error("Email no encontrado")

    else:
        if 'arch_id' not in st.session_state:
            st.info("Inicie sesión para ver el panel de control")
        else:
            arch = arch_manager.get_architect(architect_id=st.session_state['arch_id'])
            if not arch:
                st.error("No se encontraron datos del arquitecto")
            else:
                st.header(f"Bienvenido {arch['name']}")
                st.write(f"Empresa: {arch.get('company','-')}")
