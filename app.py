import streamlit as st

import sqlite3
import pandas as pd
import os
from pathlib import Path
from src import db as _db

# Page configuration: wide layout and sidebar expanded by default
st.set_page_config(page_title="ARCHIRAPID", layout="wide", initial_sidebar_state="expanded")

# Home will render header and project lists; audit code removed now that DB path is unified

st.sidebar.title("ARCHIRAPID")

# Central page registry — all routes point to `views/` or `modules/marketplace/` (NO pages/ entries)
PAGES = {
    "Home": ("modules.marketplace.marketplace", "main"),
    "Propietario (Gemelo Digital)": ("modules.marketplace.gemelo_digital", "main"),
    "Propietarios (Subir Fincas)": ("modules.marketplace.owners", "main"),
    "Diseñador de Vivienda": ("modules.marketplace.disenador_vivienda", "main"),
    "👤 Panel de Cliente": ("modules.marketplace.client_panel_fixed", "main"),
    "Arquitectos (Marketplace)": ("modules.marketplace.marketplace_upload", None),
    "Intranet": ("modules.marketplace.intranet", "main"),
}

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
page_keys = list(PAGES.keys())
default_page = st.session_state.get("auto_select_page", "Home")
selected_page = st.session_state.get("selected_page", default_page)
try:
    index = page_keys.index(selected_page) if selected_page in page_keys else 0
except Exception:
    index = 0
page = st.sidebar.radio("Navegación", page_keys, index=index)

# Limpiar estado de navegación automática
if "auto_select_page" in st.session_state:
    del st.session_state["auto_select_page"]
if "selected_page" in st.session_state:
    del st.session_state["selected_page"]

if page == "Home":
    # HEADER
    with st.container():
        # header rendered above (single invocation)
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

    # Mostrar mapa: usar marketplace.main() para Home (mapa + detalle)
    filter_province = None if province == "Todas" else province
    try:
        from modules.marketplace import marketplace
        # Comentada la llamada antigua a map_manager para usar la UI unificada
        # if map_manager:
        #     map_manager.mostrar_plots_on_map(
        #         province=filter_province,
        #         query=query,
        #         width=1100,
        #         height=650,
        #     )
        marketplace.main()
    except Exception:
        # Fallback a map_manager si marketplace no está disponible
        if map_manager:
            map_manager.mostrar_plots_on_map(
                province=filter_province,
                query=query,
                width=1100,
                height=650,
            )
        else:
            st.info("Mapa no disponible (módulos faltantes)")

    # (Removed quick DB counts for a cleaner Home presentation)

    st.markdown("---")

    # PROYECTOS DESTACADOS
    st.header("Proyectos destacados")
    # Helper: obtener valor de proyecto prefiriendo columna y luego JSON
    def _get_project_value(row: dict, data_json: dict, key: str):
        """
        Preferir valor en columna (row) y si no existe, buscar en data_json.
        Maneja el caso especial de 'baños'/'banos'.
        """
        # Manejo especial para baños/banos
        if key in ('baños', 'banos'):
            # Preferir columna con tilde, luego sin tilde
            for col in ('baños', 'banos'):
                if row.get(col) not in (None, ''):
                    return row.get(col)
            # Luego JSON
            if isinstance(data_json, dict):
                for jkey in ('baños', 'banos'):
                    if data_json.get(jkey) not in (None, ''):
                        return data_json.get(jkey)
            return None

        # General: preferir columna, luego JSON
        v = row.get(key)
        if v not in (None, ''):
            return v
        if isinstance(data_json, dict) and data_json.get(key) not in (None, ''):
            return data_json.get(key)
        return None
    projects = []
    try:
        if db:
            projects = db.get_featured_projects(limit=3)
    except Exception:
        projects = []

    # Proyectos Destacados — ficha técnica expandible y multimedia (mapeo robusto)
    import json
    cols = st.columns(3)
    for idx, p in enumerate(projects[:3]):
        with cols[idx]:
            # Parse safe JSON (normalize nested `characteristics` and `extras` to a flat dict)
            try:
                raw = json.loads(p.get('characteristics_json') or '{}')
            except Exception:
                raw = {}

            # If the stored JSON uses a nested 'characteristics' object, prefer it
            if isinstance(raw, dict) and isinstance(raw.get('characteristics'), dict):
                ch = raw.get('characteristics')
            else:
                ch = raw if isinstance(raw, dict) else {}

            # Merge 'extras' into top-level characteristics for compatibility
            ch_flat = dict(ch) if isinstance(ch, dict) else {}
            extras = ch_flat.pop('extras', None) or {}
            if isinstance(extras, dict):
                for k, v in extras.items():
                    if k not in ch_flat:
                        ch_flat[k] = v

            # Normalize key variations (compatibility with older uploads)
            if 'banos' in ch_flat and 'baños' not in ch_flat:
                ch_flat['baños'] = ch_flat['banos']
            if 'baños' in ch_flat and 'banos' not in ch_flat:
                ch_flat['banos'] = ch_flat['baños']

            # Prefer explicit top-level image/model paths from raw if present
            if isinstance(raw, dict):
                if raw.get('imagenes') and not ch_flat.get('imagenes'):
                    ch_flat['imagenes'] = raw.get('imagenes')
                if raw.get('modelo_3d_path') and not ch_flat.get('modelo_3d_path'):
                    ch_flat['modelo_3d_path'] = raw.get('modelo_3d_path')

            data = ch_flat
            files = raw.get('files') or {}

            # Imagen superior: usar únicamente las columnas/rutas exactas presentes en la tabla de auditoría
            img = (
                p.get('foto_principal')
                or p.get('imagenes')
                or p.get('imagenes_path')
                or data.get('imagenes')
                or "https://via.placeholder.com/640x360?text=No+Image"
            )
            try:
                st.image(img, use_column_width=True)
            except Exception:
                st.image("https://via.placeholder.com/640x360?text=No+Image")

            # Título y precio destacados
            title = p.get('title') or p.get('titulo') or 'Sin título'
            price = p.get('price') if p.get('price') not in (None, '') else p.get('precio') or None
            area = p.get('area_m2') if p.get('area_m2') not in (None, '') else p.get('area') or p.get('total_m2') or '—'

            st.markdown(f"**{title}**")
            if price is not None:
                try:
                    price_num = float(price)
                    st.markdown(f"**Precio:** 🔸 €{format(price_num, ',.0f')}")
                except Exception:
                    st.markdown(f"**Precio:** 🔸 {price}")
            else:
                st.markdown("**Precio:** —")

            st.markdown(f"**Superficie:** {area} m²")

            # Expander principal (único)
            with st.expander("🔍 Ver Ficha Técnica y Multimedia"):
                # Mapeo estricto: usar exactamente las claves que aparecen en la tabla de auditoría.
                habitaciones = _get_project_value(p, data, 'habitaciones') or '—'
                banos = _get_project_value(p, data, 'baños') or '—'
                plantas = _get_project_value(p, data, 'plantas') or '—'
                piscina_raw = _get_project_value(p, data, 'piscina') or False
                # Normalize piscina: accept 1/True/'1'/'true'/'si'
                piscina = False
                try:
                    if isinstance(piscina_raw, str):
                        piscina = piscina_raw.strip().lower() in ('1', 'true', 'si', 'yes', 'y')
                    else:
                        piscina = bool(int(piscina_raw)) if isinstance(piscina_raw, (int, float)) else bool(piscina_raw)
                except Exception:
                    piscina = bool(piscina_raw)

                garaje = _get_project_value(p, data, 'garaje') or False
                m2_area = _get_project_value(p, data, 'm2_area') or _get_project_value(p, data, 'm2_construidos') or area or '—'

                # Mostrar métricas en columnas (usar las variables exactas solicitadas)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.caption(f"🛏️ Habitaciones: {habitaciones if habitaciones not in (None,'') else '—'}")
                    st.caption(f"🏢 Plantas: {plantas if plantas not in (None,'') else '—'}")
                with c2:
                    st.caption(f"🛁 Baños: {banos if banos not in (None,'') else '—'}")
                    constructed = m2_area if m2_area not in (None,'') else '—'
                    st.caption(f"📐 Construidos: {constructed} m²")
                with c3:
                    st.caption("🏊 Piscina: ✅" if piscina else "🏊 Piscina: —")
                    st.caption("🚗 Garaje: ✅" if garaje else "🚗 Garaje: —")

                st.markdown("---")
                # Multimedia: mostrar mini-galería si hay imágenes (no exponer rutas sensibles)
                image_preview = None
                # Preferir ruta exacta en la tabla de auditoría
                if 'imagenes' in data and data.get('imagenes'):
                    image_preview = data.get('imagenes')
                elif p.get('imagenes_path'):
                    image_preview = p.get('imagenes_path')

                if image_preview:
                    try:
                        st.image(image_preview, width=300)
                    except Exception:
                        pass

                # Botones de interacción (simulados). Mostrar botón 3D si existe modelo_3d en data top-level o files.
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Simular Realidad Virtual (RV)", key=f"rv_{p.get('id')}"):
                        st.info("Iniciando simulación RV (simulada)...")
                with col_b:
                    # Descargar Memoria Técnica / PDF si existe
                    pdf_candidate = None
                    for k in ('memoria_pdf', 'planos_pdf', 'memoria', 'memoria_tecnica', 'pdf'):
                        if k in data and data.get(k):
                            pdf_candidate = data.get(k)
                            break
                        if p.get(k):
                            pdf_candidate = p.get(k)
                            break

                    pdf_checked = None
                    if pdf_candidate and isinstance(pdf_candidate, str) and pdf_candidate.strip():
                        root = Path(r"C:/ARCHIRAPID_PROYECT25")
                        pth = Path(pdf_candidate)
                        if not pth.is_absolute():
                            pdf_checked = str((root / pdf_candidate).resolve())
                        else:
                            pdf_checked = str(pth)

                    if pdf_checked and Path(pdf_checked).exists():
                        try:
                            with open(pdf_checked, 'rb') as fpdf:
                                st.download_button("📄 Descargar Memoria Técnica", data=fpdf, file_name=Path(pdf_checked).name, mime='application/pdf', key=f"dlpdf_{p.get('id')}")
                        except Exception:
                            st.caption("Memoria Técnica: —")
                    else:
                        st.caption("Memoria Técnica: —")
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

# "Inmobiliaria (Mapa)" route removed — Home now uses `marketplace.main()` directly.

elif page == "👤 Panel de Cliente":
    with st.container():
        # Panel de cliente con acceso a transacciones y servicios
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()

elif page == "Arquitectos (Marketplace)":
    with st.container():
        # Use the new main() entrypoint which handles auth, plans and upload flow
        from modules.marketplace import marketplace_upload
        marketplace_upload.main()

elif page == "Intranet":
    with st.container():
        from modules.marketplace import intranet
        intranet.main()
