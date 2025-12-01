# modules/marketplace/architects.py
import streamlit as st
from modules.marketplace.utils import save_upload, db_conn, insert_user
import uuid, json
from datetime import datetime

def main():
    st.header("Arquitectos — registro y gestión de proyectos")

    email = st.text_input("Email (arquitecto)")
    name = st.text_input("Nombre del arquitecto / estudio")
    if st.button("Identificar / Registrar arquitecto"):
        if not email or not name:
            st.error("Completa nombre y email.")
        else:
            # create user
            from modules.marketplace.utils import get_user_by_email
            cur = get_user_by_email(email)
            if cur:
                st.success("Usuario ya registrado.")
                st.session_state["arch_user_id"] = cur[0]
            else:
                uid = uuid.uuid4().hex
                insert_user({"id":uid,"name":name,"email":email,"role":"architect","company":""})
                st.session_state["arch_user_id"] = uid
                st.success("Arquitecto registrado.")

    if "arch_user_id" not in st.session_state:
        st.info("Identifícate para continuar.")
        st.stop()

    st.subheader("Comprar plan (simulado)")
    plans = {"BASIC":(3,200),"STANDARD":(6,350),"PRO":(10,600)}
    cols = st.columns(3)
    for i,(p,(limit,price)) in enumerate(plans.items()):
        with cols[i]:
            st.write(f"**{p}**")
            st.write(f"{limit} proyectos — €{price}")
            if st.button(f"Comprar {p}"):
                # insert subscription record
                aid = uuid.uuid4().hex
                conn = db_conn(); c=conn.cursor()
                c.execute("INSERT INTO subscriptions (id,architect_id,plan,price,created_at) VALUES (?,?,?,?,?)",
                          (aid, st.session_state["arch_user_id"], p, price, datetime.utcnow().isoformat()))
                conn.commit(); conn.close()
                st.success(f"Plan {p} comprado (simulado).")

    st.markdown("---")
    st.subheader("Subir proyecto (completo)")
    title = st.text_input("Título del proyecto")
    area = st.number_input("Superficie construida (m²)", min_value=1.0, value=100.0)
    price = st.number_input("Precio del proyecto (por la licencia/descarga)", min_value=0.0, value=1200.0)
    files = st.file_uploader("Ficheros del proyecto (pdf, zip, glb)", accept_multiple_files=True)
    if st.button("Subir proyecto"):
        if not title:
            st.error("Título obligatorio.")
        else:
            saved = []
            for f in files:
                saved.append(save_upload(f, prefix="proj"))
            # insert project
            pid = uuid.uuid4().hex
            conn = db_conn(); c=conn.cursor()
            c.execute("INSERT INTO projects (id,architect_id,title,description,area_m2,price,files_json,created_at) VALUES (?,?,?,?,?,?,?,?)",
                      (pid, st.session_state["arch_user_id"], title, "", area, price, json.dumps(saved), datetime.utcnow().isoformat()))
            conn.commit(); conn.close()
            st.success("Proyecto subido. Ahora aparecerá en el marketplace cuando lo apruebes (demo: auto aprobado).")