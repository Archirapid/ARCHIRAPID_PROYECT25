import streamlit as st

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
    "Propietario (Gemelo Digital)",
    "Propietarios (Subir Fincas)",
    "Diseñador de Vivienda",
    "Inmobiliaria (Mapa)",
    "👤 Panel de Cliente",
    "Arquitectos (Marketplace)",
    "Intranet"
], index=["Home", "Propietario (Gemelo Digital)", "Propietarios (Subir Fincas)", "Diseñador de Vivienda", "Inmobiliaria (Mapa)", "👤 Panel de Cliente", "Arquitectos (Marketplace)", "Intranet"].index(selected_page) if selected_page in ["Home", "Propietario (Gemelo Digital)", "Propietarios (Subir Fincas)", "Diseñador de Vivienda", "Inmobiliaria (Mapa)", "👤 Panel de Cliente", "Arquitectos (Marketplace)", "Intranet"] else 0)

# Limpiar estado de navegación automática
if "auto_select_page" in st.session_state:
    del st.session_state["auto_select_page"]
if "selected_page" in st.session_state:
    del st.session_state["selected_page"]

if page == "Home":
    # HEADER
    with st.container():
        try:
            from components.header import render_header
            cols = render_header()
            # Put ACCESS button at the right-most column
            access_col = cols[2]
        except Exception:
            # Fallback header
            cols = st.columns([1, 4, 1])
            with cols[0]:
                try:
                    st.image("assets/branding/logo.png", width=140)
                except Exception:
                    st.markdown("# 🏗️ ARCHIRAPID")
            with cols[1]:
                st.markdown("### IA Avanzada + Precios en Vivo + Exportación Profesional")
            access_col = cols[2]

        with access_col:
            if st.button("ACCESO"):
                # Show a small login modal/form
                if hasattr(st, 'modal'):
                    with st.modal("Acceso"):
                        login_val = st.text_input("Email o Clave", key="login_input")
                        if st.button("Entrar", key="login_submit"):
                            val = st.session_state.get("login_input", "")
                            # Admin static password
                            if val == "admin123":
                                st.success("Acceso admin aceptado")
                                st.session_state['selected_page'] = "Intranet"
                                st.experimental_rerun()
                            elif "@" in val:
                                # Buscar en clients
                                try:
                                    from src import db
                                    db.ensure_tables()
                                    conn = db.get_conn()
                                    cur = conn.cursor()
                                    cur.execute("SELECT * FROM clients WHERE email = ?", (val,))
                                    row = cur.fetchone()
                                    conn.close()
                                    if row:
                                        st.success("Acceso cliente reconocido — redirigiendo al Panel Cliente")
                                        st.session_state['selected_page'] = "👤 Panel de Cliente"
                                        st.session_state['auto_owner_email'] = val
                                        st.experimental_rerun()
                                    else:
                                        st.error("Email no encontrado como propietario en la base de datos")
                                except Exception as e:
                                    st.error(f"Error comprobando usuario: {e}")
                            else:
                                st.error("Credenciales inválidas")
                else:
                    with st.expander("Acceso"):
                        login_val = st.text_input("Email o Clave", key="login_input_no_modal")
                        if st.button("Entrar", key="login_submit_no_modal"):
                            val = st.session_state.get("login_input_no_modal", "")
                            if val == "admin123":
                                st.success("Acceso admin aceptado")
                                st.session_state['selected_page'] = "Intranet"
                                st.experimental_rerun()
                            elif "@" in val:
                                try:
                                    from src import db
                                    db.ensure_tables()
                                    conn = db.get_conn()
                                    cur = conn.cursor()
                                    cur.execute("SELECT * FROM clients WHERE email = ?", (val,))
                                    row = cur.fetchone()
                                    conn.close()
                                    if row:
                                        st.success("Acceso cliente reconocido — redirigiendo al Panel Cliente")
                                        st.session_state['selected_page'] = "👤 Panel de Cliente"
                                        st.session_state['auto_owner_email'] = val
                                        st.experimental_rerun()
                                    else:
                                        st.error("Email no encontrado como propietario en la base de datos")
                                except Exception as e:
                                    st.error(f"Error comprobando usuario: {e}")
                            else:
                                st.error("Credenciales inválidas")

    st.markdown("---")

    # BUSCADOR + MAPA
    st.header("Buscar Fincas")
    try:
        from src import db
        from src import map_manager
    except Exception:
        st.error("Error cargando módulos de base de datos o mapa")
        db = None
        map_manager = None

    province_options = []
    if db:
        try:
            province_options = db.get_all_provinces()
        except Exception:
            province_options = []

    province = st.selectbox("Provincia", options=["Todas"] + province_options, index=0)
    query = st.text_input("Localidad o dirección", value="")

    # Mostrar mapa reutilizando helper que consulta la BBDD
    filter_province = None if province == "Todas" else province
    if map_manager:
        map_manager.mostrar_plots_on_map(province=filter_province, query=query)
    else:
        st.info("Mapa no disponible (módulo map_manager faltante)")

    st.markdown("---")

    # PROYECTOS DESTACADOS
    st.header("Proyectos destacados")
    projects = []
    try:
        if db:
            projects = db.get_featured_projects(limit=3)
    except Exception:
        projects = []

    cols = st.columns(3)
    for i in range(3):
        with cols[i]:
            if i < len(projects):
                p = projects[i]
                img = p.get('foto_principal') or "https://via.placeholder.com/320x240?text=No+Image"
                try:
                    st.image(img, use_column_width=True)
                except Exception:
                    st.image("https://via.placeholder.com/320x240?text=No+Image")
                st.markdown(f"**{p.get('title','Sin título')}**")
                st.markdown(f"m²: {p.get('area_m2','—')}")
                st.markdown(f"Presupuesto: €{p.get('price','—')}")
            else:
                st.info("Sin proyecto")
elif page == "Propietario (Gemelo Digital)":
    with st.container():
        # Flujo principal: Propietario sube finca → IA genera plan
        from modules.marketplace import gemelo_digital
        gemelo_digital.main()

elif page == "Propietarios (Subir Fincas)":
    with st.container():
        # Propietarios suben fincas al marketplace inmobiliario
        from modules.marketplace import owners
        owners.main()

elif page == "Diseñador de Vivienda":
    with st.container():
        # Flujo secundario: Cliente diseña vivienda personalizada
        from modules.marketplace import disenador_vivienda
        disenador_vivienda.main()

elif page == "Inmobiliaria (Mapa)":
    with st.container():
        # Flujo terciario: Cliente explora fincas y proyectos
        from modules.marketplace import marketplace
        marketplace.main()

elif page == "👤 Panel de Cliente":
    with st.container():
        # Panel de cliente con acceso a transacciones y servicios
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()

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

elif page == "Intranet":
    with st.container():
        from modules.marketplace import intranet
        intranet.main()
