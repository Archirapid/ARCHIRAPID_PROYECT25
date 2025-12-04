# app.py (entry)
import streamlit as st
from modules.marketplace import architects, owners, marketplace

st.set_page_config(page_title="ARCHIRAPID", layout="wide")
st.sidebar.title("ARCHIRAPID")
page = st.sidebar.radio("Navegación", ["Home","Marketplace","Owners","Architects","Design Assistant"])

if page=="Home":
    st.title("ARCHIRAPID — Home")
    st.write("Demo MVP: marketplace de fincas + proyectos.")
elif page=="Marketplace":
    marketplace.main() if hasattr(marketplace, "main") else marketplace
elif page=="Owners":
    owners.main() if hasattr(owners, "main") else owners
elif page=="Architects":
    architects.main() if hasattr(architects, "main") else architects
elif page=="Design Assistant":
    from archirapid_extract.streamlit_design import main as design_main
    design_main()
