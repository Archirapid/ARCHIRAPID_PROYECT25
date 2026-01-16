import streamlit as st
from modules.marketplace.project_detail import show_project_detail_page

st.set_page_config(layout="wide")

params = st.query_params
project_id = params.get("project_id")

# Soporta que project_id sea lista o string
if isinstance(project_id, list):
    project_id = project_id[0] if project_id else None

if not project_id:
    st.error("❌ No se ha proporcionado ningún parámetro 'project_id' en la URL. Ejemplo: /?project_id=123")
else:
    show_project_detail_page(project_id)
