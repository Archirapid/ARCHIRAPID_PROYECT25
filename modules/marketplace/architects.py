# modules/marketplace/architects.py
import streamlit as st
from modules.marketplace.utils import save_upload, db_conn, insert_user, list_published_plots
import uuid, json
from datetime import datetime

def main():
    st.title("🏗️ Arquitectos — Gestión Profesional de Proyectos")

    # Tab system for better organization
    tab1, tab2, tab3 = st.tabs(["👤 Registro", "💳 Planes", "📤 Subir Proyecto"])

    with tab1:
        st.header("Registro de Arquitecto")
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email profesional", key="arch_email")
            name = st.text_input("Nombre del arquitecto / estudio", value=st.session_state.get("arch_name_db", ""), key="arch_name")
        with col2:
            company = st.text_input("Empresa (opcional)", key="arch_company")
            specialty = st.selectbox("Especialidad", ["Arquitectura Residencial", "Comercial", "Industrial", "Urbanismo"], key="arch_specialty")

        if st.button("Identificar / Registrar", type="primary", key="register_arch"):
            if not email or not name:
                st.error("Nombre y email son obligatorios.")
            else:
                from modules.marketplace.utils import get_user_by_email
                cur = get_user_by_email(email)
                if cur:
                    st.success("✅ Arquitecto ya registrado. Bienvenido de vuelta!")
                    st.session_state["arch_user_id"] = cur[0]
                    st.session_state["arch_name_db"] = cur[1]
                else:
                    uid = uuid.uuid4().hex
                    insert_user({"id":uid,"name":name,"email":email,"role":"architect","company":company})
                    st.session_state["arch_user_id"] = uid
                    st.session_state["arch_name_db"] = name
                    st.success("🎉 Arquitecto registrado exitosamente!")

        if "arch_user_id" in st.session_state:
            st.info(f"✅ Conectado como: {st.session_state.get('arch_name_db', 'Arquitecto')}")

    with tab2:
        st.header("Planes de Suscripción")
        if "arch_user_id" not in st.session_state:
            st.warning("Regístrate primero para ver los planes.")
            st.stop()

        plans = {
            "BASIC": {"proyectos": 3, "precio": 200, "desc": "Para arquitectos independientes"},
            "STANDARD": {"proyectos": 6, "precio": 350, "desc": "Para estudios pequeños"},
            "PRO": {"proyectos": 10, "precio": 600, "desc": "Para estudios profesionales"}
        }
        cols = st.columns(3)
        for i, (p, data) in enumerate(plans.items()):
            with cols[i]:
                st.subheader(f"**{p}**")
                st.write(f"📋 {data['proyectos']} proyectos")
                st.write(f"💰 €{data['precio']}/mes")
                st.write(f"📝 {data['desc']}")
                if st.button(f"Comprar {p}", key=f"buy_{p}"):
                    aid = uuid.uuid4().hex
                    conn = db_conn(); c=conn.cursor()
                    c.execute("INSERT INTO subscriptions (id,architect_id,plan,price,created_at) VALUES (?,?,?,?,?)",
                              (aid, st.session_state["arch_user_id"], p, data['precio'], datetime.utcnow().isoformat()))
                    conn.commit(); conn.close()
                    st.success(f"✅ Plan {p} activado! Disfruta de tus {data['proyectos']} proyectos.")

    with tab3:
        st.header("Subir Proyecto Arquitectónico")
        if "arch_user_id" not in st.session_state:
            st.warning("Regístrate y elige un plan para subir proyectos.")
            st.stop()

        # Project details
        st.subheader("📋 Detalles del Proyecto")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Título del proyecto", key="proj_title")
            description = st.text_area("Descripción", key="proj_desc", height=100)
            price = st.number_input("Precio de licencia (€)", min_value=0.0, value=1200.0, key="proj_price")
        with col2:
            # Link to plot
            plots = list_published_plots()
            plot_options = ["Ninguna"] + [f"{p['title']} ({p['surface_m2']} m²)" for p in plots]
            selected_plot_str = st.selectbox("Vincular a parcela existente (opcional)", plot_options, key="proj_plot")
            selected_plot = None
            if selected_plot_str != "Ninguna":
                selected_plot = next((p for p in plots if f"{p['title']} ({p['surface_m2']} m²)" == selected_plot_str), None)

        # Characteristics
        st.subheader("🏠 Características Técnicas")
        col1, col2, col3 = st.columns(3)
        with col1:
            area = st.number_input("Superficie construida (m²)", min_value=1.0, value=100.0, key="proj_area")
            habitaciones = st.number_input("Habitaciones", min_value=0, value=3, key="proj_hab")
            banos = st.number_input("Baños", min_value=0, value=2, key="proj_banos")
        with col2:
            cocinas = st.number_input("Cocinas", min_value=0, value=1, key="proj_cocinas")
            garage = st.checkbox("Garaje incluido", key="proj_garage")
            altura = st.number_input("Altura (plantas)", min_value=1, value=1, key="proj_altura")
        with col3:
            tipo_construccion = st.selectbox("Tipo", ["Unifamiliar", "Adosada", "Piso", "Chalet", "Comercial"], key="proj_tipo")
            estilo = st.selectbox("Estilo", ["Moderno", "Clásico", "Mediterráneo", "Industrial", "Minimalista"], key="proj_estilo")

        # Adjust based on plot
        if selected_plot:
            st.info(f"⚠️ Ajustando a parcela: {selected_plot['surface_m2']} m². Edificabilidad máxima: {selected_plot['surface_m2'] * 0.8} m²")
            max_area = selected_plot['surface_m2'] * 0.8
            if area > max_area:
                st.warning(f"Área supera edificabilidad. Máximo recomendado: {max_area} m²")

        # File uploads
        st.subheader("📎 Archivos del Proyecto")
        st.info("Sube archivos organizados por categoría para mejor presentación.")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Documentación**")
            memoria = st.file_uploader("Memoria del proyecto (PDF)", type="pdf", key="upload_memoria")
            proyecto_completo = st.file_uploader("Proyecto completo (ZIP/PDF)", type=["zip", "pdf"], key="upload_proyecto")

            st.write("**Planos Técnicos**")
            dwg_files = st.file_uploader("Archivos DWG (AutoCAD)", type="dwg", accept_multiple_files=True, key="upload_dwg")

        with col2:
            st.write("**Visualización 3D**")
            glb_files = st.file_uploader("Modelos 3D (GLB/GLTF)", type=["glb", "gltf"], accept_multiple_files=True, key="upload_glb")

            st.write("**Realidad Virtual**")
            rv_files = st.file_uploader("Archivos RV (ZIP con escena)", type="zip", key="upload_rv")

            st.write("**Imágenes**")
            fotos = st.file_uploader("Fotos del proyecto", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="upload_fotos")

        # Upload button
        if st.button("🚀 Subir Proyecto Completo", type="primary", key="upload_proj"):
            if not title:
                st.error("El título es obligatorio.")
            elif not any([memoria, proyecto_completo, dwg_files, glb_files, rv_files, fotos]):
                st.error("Sube al menos un archivo del proyecto.")
            else:
                # Save files
                saved_files = {}
                if memoria:
                    saved_files["memoria"] = save_upload(memoria, "memoria")
                if proyecto_completo:
                    saved_files["proyecto"] = save_upload(proyecto_completo, "proyecto")
                if dwg_files:
                    saved_files["dwg"] = [save_upload(f, "dwg") for f in dwg_files]
                if glb_files:
                    saved_files["glb"] = [save_upload(f, "glb") for f in glb_files]
                if rv_files:
                    saved_files["rv"] = save_upload(rv_files, "rv")
                if fotos:
                    saved_files["fotos"] = [save_upload(f, "foto") for f in fotos]

                # Characteristics
                characteristics = {
                    "area_m2": area,
                    "habitaciones": habitaciones,
                    "banos": banos,
                    "cocinas": cocinas,
                    "garage": garage,
                    "altura_plantas": altura,
                    "tipo_construccion": tipo_construccion,
                    "estilo": estilo
                }

                # Insert project
                pid = uuid.uuid4().hex
                conn = db_conn(); c=conn.cursor()
                c.execute("""
                    INSERT INTO projects (id,architect_id,title,description,area_m2,price,files_json,characteristics_json,plot_id,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    pid, st.session_state["arch_user_id"], title, description, area, price,
                    json.dumps(saved_files), json.dumps(characteristics),
                    selected_plot["id"] if selected_plot else None,
                    datetime.utcnow().isoformat()
                ))
                conn.commit(); conn.close()

                st.success("🎉 Proyecto subido exitosamente!")
                st.info("El proyecto aparecerá en el marketplace para que los compradores lo descubran.")

                # Preview
                st.subheader("Vista Previa del Proyecto")
                st.json(characteristics)
                if fotos:
                    st.image(fotos[0], caption="Foto principal", width=300)