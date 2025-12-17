# modules/marketplace/architects.py
import streamlit as st
from modules.marketplace.utils import save_upload, db_conn, insert_user, list_published_plots
import uuid, json
from datetime import datetime

def main():
    st.title("🏗️ Arquitectos — Gestión Profesional de Proyectos")

    # Tab system for better organization (Subir Proyecto migrado to arquitectos_registro)
    tab1, tab2 = st.tabs(["👤 Registro", "💳 Planes"])

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

    # Tab3 (Subir Proyecto) migrado a pages/arquitectos_registro.py