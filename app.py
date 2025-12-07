# app.py (entry)
import streamlit as st

st.set_page_config(page_title="ARCHIRAPID", layout="wide")
st.sidebar.title("ARCHIRAPID")
page = st.sidebar.radio("Navegación", [
    "Home",
    "Propietario (Gemelo Digital)",
    "Diseñador de Vivienda",
    "Inmobiliaria (Mapa)",
    "Arquitectos (Marketplace)",
    "Intranet"
])

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
elif page == "Propietario (Gemelo Digital)":
    with st.container():
        # Flujo principal: Propietario sube finca → IA genera plan
        from modules.marketplace import gemelo_digital
        gemelo_digital.main()

elif page == "Diseñador de Vivienda":
    with st.container():
        # Flujo secundario: Cliente diseña vivienda personalizada
        from modules.marketplace import disenador_vivienda
        disenador_vivienda.main()

elif page == "Inmobiliaria (Mapa)":
    with st.container():
        # Flujo terciario: Cliente explora fincas y proyectos
        from modules.marketplace import inmobiliaria_mapa
        inmobiliaria_mapa.mostrar_mapa_inmobiliario()

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
