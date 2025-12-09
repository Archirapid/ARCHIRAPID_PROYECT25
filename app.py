import streamlit as st
from modules.marketplace.footer import show_footer

st.set_page_config(page_title="ARCHIRAPID", layout="wide")
st.sidebar.title("ARCHIRAPID")

# Detectar navegación automática desde session state (de owners.py)
if "navigate_to_client_panel" in st.session_state:
    st.session_state["auto_select_page"] = "👤 Panel de Cliente"
    st.session_state["selected_page"] = "👤 Panel de Cliente"  # Forzar selección
    if "navigate_owner_email" in st.session_state:
        st.session_state["auto_owner_email"] = st.session_state["navigate_owner_email"]
    # Limpiar estado de navegación
    del st.session_state["navigate_to_client_panel"]
    del st.session_state["navigate_owner_email"]
    st.rerun()  # Forzar recarga completa

# Determinar página seleccionada
default_page = st.session_state.get("auto_select_page", "Home")
selected_page = st.session_state.get("selected_page", default_page)
page = st.sidebar.radio("Navegación", [
    "Home",
    "Propietarios (Subir Fincas)",
    "Inmobiliaria (Mapa)",
    "👤 Panel de Cliente",
    "Arquitectos (Marketplace)",
    "Intranet"
], index=["Home", "Propietarios (Subir Fincas)", "Inmobiliaria (Mapa)", "👤 Panel de Cliente", "Arquitectos (Marketplace)", "Intranet"].index(selected_page) if selected_page in ["Home", "Propietarios (Subir Fincas)", "Inmobiliaria (Mapa)", "👤 Panel de Cliente", "Arquitectos (Marketplace)", "Intranet"] else 0)

# Limpiar estado de navegación automática
if "auto_select_page" in st.session_state:
    del st.session_state["auto_select_page"]
if "selected_page" in st.session_state:
    del st.session_state["selected_page"]

if page == "Home":
    with st.container():
        st.title("🏗️ ARCHIRAPID")
        st.image("assets/branding/logo.png", width=300)
        st.markdown("""
        ### Arquitectura Unificada - MVP Completo

        **Tres flujos principales sincronizados:**

        #### 👤 **Propietario → Gemelo Digital con IA**
        - Sube finca → Catastro automático → Genera plan con IA → Edición → Validación → 3D → Memoria → Pago → Exportación

        #### 🎨 **Diseñador de Vivienda**
        - Selecciona finca → Ajusta parámetros → Usa mismos módulos de edición/validación/3D → Documentación → Pago

        #### 🗺️ **Cliente Inmobiliario (Mapa)**
        - Explora fincas → Ve proyectos compatibles → Reserva/compra → Descarga documentación

        #### 👷 **Arquitecto → Marketplace**
        - Sube proyectos completos (3D, RV, memoria, CAD) → Aparecen en catálogo → Clientes compran

        #### 🔄 **Sincronización Total**
        - **Fincas + Proyectos + Transacciones** en data_access.py
        - **Catastro API** (real/simulado) en catastro_api.py
        - **Módulos compartidos:** plan_vivienda, editor, validación, 3D, documentación, pago

        ---
        *MVP unificado - Tres entradas, un núcleo, escalable*
        """)
    show_footer()
elif page == "Propietarios (Subir Fincas)":
    with st.container():
        # Propietarios suben fincas al marketplace inmobiliario
        from modules.marketplace import owners
        owners.main()
    show_footer()
elif page == "Inmobiliaria (Mapa)":
    with st.container():
        # Flujo terciario: Cliente explora fincas y proyectos
        from modules.marketplace import marketplace
        marketplace.main()
    show_footer()
elif page == "👤 Panel de Cliente":
    with st.container():
        # Panel de cliente con acceso a transacciones y servicios
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()
    show_footer()
elif page == "Arquitectos (Marketplace)":
    with st.container():
        # Arquitectos suben proyectos al marketplace
        from modules.marketplace import marketplace_upload
        st.title("👷 Marketplace Arquitectos")

        # Submenú para arquitectos
        sub_page = st.radio("Acciones", ["Subir Proyecto", "Mis Proyectos", "Explorar Mercado"],
                           horizontal=True, key="arquitectos_submenu")

        if sub_page == "Subir Proyecto":
            # Simular arquitecto ID (en producción vendría de login)
            arquitecto_id = st.session_state.get('arquitecto_id', 1)

            proyecto = marketplace_upload.upload_proyecto_form(arquitecto_id)
            if proyecto:
                st.success("✅ Proyecto subido exitosamente!")

        elif sub_page == "Mis Proyectos":
            arquitecto_id = st.session_state.get('arquitecto_id', 1)
            proyectos = marketplace_upload.proyectos_por_arquitecto(arquitecto_id)

            if proyectos:
                for proyecto in proyectos:
                    marketplace_upload.mostrar_proyecto_arquitecto(proyecto)
                    st.divider()
            else:
                st.info("No tienes proyectos subidos aún")

        elif sub_page == "Explorar Mercado":
            proyectos = marketplace_upload.explorar_proyectos_arquitectos()

            st.subheader(f"📚 Catálogo de Proyectos ({len(proyectos)} disponibles)")

            for proyecto in proyectos:
                marketplace_upload.mostrar_proyecto_arquitecto(proyecto)
                st.divider()
    show_footer()
elif page == "Intranet":
    with st.container():
        from modules.marketplace import intranet
        intranet.main()
    show_footer()
