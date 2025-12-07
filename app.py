# app.py (entry)
import streamlit as st
from modules.marketplace import architects, owners, marketplace, intranet, gemelo_digital

st.set_page_config(page_title="ARCHIRAPID", layout="wide")
st.sidebar.title("ARCHIRAPID")
page = st.sidebar.radio("Navegación", ["Home","Marketplace","Owners","Architects","Design Assistant","Gemelo Digital","Intranet"])

if page=="Home":
    st.title("🏗️ ARCHIRAPID")
    st.image("assets/branding/logo.png", width=300)
    st.markdown("""
    ### Bienvenido al Marketplace de Arquitectura y Construcción
    
    **ARCHIRAPID** es la plataforma que conecta propietarios de terrenos urbanos con arquitectos y constructores para proyectos de edificación rápida y eficiente.
    
    #### 🚀 Características Principales:
    - **Marketplace de Fincas:** Encuentra terrenos urbanos listos para construir
    - **Arquitectos Certificados:** Diseña proyectos optimizados para tu parcela
    - **Asistente de Diseño:** Genera planos automáticamente con IA
    - **Pagos Seguros:** Reserva y compra con garantías
    
    #### 📍 Navega por las secciones:
    - **Marketplace:** Explora fincas disponibles en el mapa
    - **Owners:** Registra tu terreno para vender
    - **Architects:** Ofrece tus servicios de diseño
    - **Design Assistant:** Crea planos con IA
    - **Gemelo Digital:** Simula y optimiza proyectos con IA
    
    ---
    *Demo MVP funcional - Listo para inversión*
    """)
elif page=="Marketplace":
    marketplace.main() if hasattr(marketplace, "main") else marketplace
elif page=="Owners":
    owners.main() if hasattr(owners, "main") else owners
elif page=="Architects":
    architects.main() if hasattr(architects, "main") else architects
elif page=="Design Assistant":
    from archirapid_extract.streamlit_design import main as design_main
    design_main()
elif page=="Gemelo Digital":
    gemelo_digital.main()
elif page=="Intranet":
    intranet.main()
