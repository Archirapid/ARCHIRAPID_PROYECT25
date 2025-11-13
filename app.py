"""
ARCHIRAPID MVP - Main Application
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime
import base64
import json
import sys

# Configuration
BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

# Añadir path para módulo de export DXF
sys.path.insert(0, os.path.join(BASE, "archirapid_extract"))

st.set_page_config(page_title="ARCHIRAPID MVP", layout="wide")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # plots table
    c.execute('''
        CREATE TABLE IF NOT EXISTS plots (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            lat REAL,
            lon REAL,
            m2 INTEGER,
            height REAL,
            price REAL,
            type TEXT,
            province TEXT,
            locality TEXT,
            owner_name TEXT,
            owner_email TEXT,
            image_path TEXT,
            registry_note_path TEXT,
            created_at TEXT
        )
    ''')
    # projects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT,
            architect_name TEXT,
            architect_id TEXT,
            area_m2 INTEGER,
            max_height REAL,
            style TEXT,
            price REAL,
            file_path TEXT,
            description TEXT,
            created_at TEXT
        )
    ''')
    # reservations
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            plot_id TEXT,
            buyer_name TEXT,
            buyer_email TEXT,
            amount REAL,
            kind TEXT,
            created_at TEXT
        )
    ''')
    # architects and subscriptions
    c.execute('''
        CREATE TABLE IF NOT EXISTS architects (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            nif TEXT,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            architect_id TEXT,
            plan_name TEXT,
            plan_limit INTEGER,
            price REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_file(uploaded_file, prefix="file"):
    ext = os.path.splitext(uploaded_file.name)[1]
    fname = f"{prefix}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOADS, fname)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def insert_plot(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO plots (id, title, description, lat, lon, m2, height, price, type, province, locality, owner_name, owner_email, image_path, registry_note_path, created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['title'], data.get('description',''), data['lat'], data['lon'], data['m2'], data['height'], data['price'], data['type'], data['province'], data.get('locality',''), data.get('owner_name',''), data.get('owner_email',''), data.get('image_path'), data.get('registry_note_path'), data['created_at']
    ))
    conn.commit()
    conn.close()

def get_all_plots():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM plots ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_plot_by_id(pid):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM plots WHERE id = ?", conn, params=(pid,))
    conn.close()
    if df.shape[0] == 0:
        return None
    return df.iloc[0].to_dict()

def insert_project(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO projects (id, title, architect_name, architect_id, area_m2, max_height, style, price, file_path, description, created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
        data['id'], data['title'], data.get('architect_name',''), data.get('architect_id'), data.get('area_m2'), data.get('max_height'), data.get('style'), data.get('price'), data.get('file_path'), data.get('description',''), data.get('created_at')
    ))
    conn.commit()
    conn.close()

def get_all_projects():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()
    return df

def insert_reservation(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO reservations (id, plot_id, buyer_name, buyer_email, amount, kind, created_at) VALUES (?,?,?,?,?,?,?)',
              (data['id'], data['plot_id'], data['buyer_name'], data['buyer_email'], data['amount'], data['kind'], data['created_at']))
    conn.commit()
    conn.close()

def get_image_base64(image_path):
    try:
        with open(image_path, 'rb') as f:
            return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    except Exception:
        return None

# Initialize DB
init_db()

# Navigation bar
st.markdown("""
<nav style='background:#f8f9fa;padding:8px;border-radius:6px;margin-bottom:12px;'>
  <a href='/?page=Home' style='margin-right:12px;'>Inicio</a>
  <a href='/?page=plots' style='margin-right:12px;'>Registro Fincas</a>
  <a href='/?page=architects' style='margin-right:12px;'>Arquitectos</a>
</nav>
""", unsafe_allow_html=True)

# Get current page from query params (robust resolver)
raw_page = st.query_params.get('page', 'Home')
if isinstance(raw_page, list):
    raw_page = raw_page[0]
page = str(raw_page) if raw_page is not None else 'Home'
# Normalize common short values that sometimes appear (e.g. 'p' -> 'plots')
norm = page.strip().lower()
if norm in ['home', 'inicio', 'h']:
    page = 'Home'
elif norm in ['plots', 'plots', 'p', 'plot', 'plots']:
    page = 'plots'
elif norm in ['architects', 'architect', 'a']:
    page = 'architects'
else:
    # leave page as-is if it matches expected values; otherwise default to Home
    if page not in ['Home', 'plots', 'architects']:
        page = 'Home'

if page == 'Home':
    st.title('ARCHIRAPID — Home')
    st.write('Busca fincas en la izquierda y visualízalas en el mapa interactivo. Haz clic en un marcador para abrir el panel detalle a la derecha.')

    # Layout: filters (left) + map + details panel (right)
    left_col, main_col = st.columns([1, 3])

    # --- LEFT: filtros ---
    with left_col:
        st.header("Filters")
        if st.button("Registrar nueva finca"):
            st.query_params.update({"page": "plots"})
            st.rerun()
        min_m2 = st.number_input("Min m²", min_value=0, value=0)
        max_m2 = st.number_input("Max m²", min_value=0, value=100000)
        province = st.text_input("Province / Region", value="")
        type_sel = st.selectbox("Type", options=["any", "rural", "urban", "industrial"])
        min_price = st.number_input("Min price (€)", min_value=0, value=0)
        max_price = st.number_input("Max price (€)", min_value=0, value=10000000)
        q = st.text_input("Search text (locality, title...)", "")
        if st.button("Apply filters"):
            st.rerun()  # Fixed: removed deprecated experimental_rerun()


    # --- MAIN: map + right preview panel ---
    df_plots = get_all_plots()
    df = df_plots.copy()
    # Filtrar fincas con coordenadas válidas (lat/lon no nulos y tipo float)
    df = df[df["lat"].apply(lambda x: isinstance(x, (float, int)) and not pd.isnull(x))]
    df = df[df["lon"].apply(lambda x: isinstance(x, (float, int)) and not pd.isnull(x))]
    # Filtrar duplicados por id
    df = df.drop_duplicates(subset=["id"])
    # Aplicar filtros
    if df.shape[0] > 0:
        df = df[(df["m2"] >= min_m2) & (df["m2"] <= max_m2) & (df["price"] >= min_price) & (df["price"] <= max_price)]
        if province.strip() != "":
            df = df[df["province"].str.contains(province, case=False, na=False)]
        if type_sel != "any":
            df = df[df["type"] == type_sel]
        if q.strip() != "":
            df = df[df.apply(lambda row: q.lower() in str(row["title"]).lower() or q.lower() in str(row.get("province","")).lower(), axis=1)]

    # build map
    m = folium.Map(location=[40.0, -4.0], zoom_start=6, tiles="CartoDB positron")
    if df.shape[0] > 0:
        for _, r in df.iterrows():
            # small thumbnail in popup
            img_html = ""
            if r.get("image_path") and os.path.exists(r["image_path"]):
                img_b64 = get_image_base64(r["image_path"])
                if img_b64:
                    img_html = f'<img src="{img_b64}" width="160" style="border-radius:8px;display:block;margin:0 auto 6px;"/>'

            popup_html = f"""
            <div style="width:240px;font-family:'Segoe UI',Roboto,sans-serif;background:#fff;border-radius:12px;padding:8px;text-align:center;box-shadow:0 3px 8px rgba(0,0,0,0.15);">
                {img_html}
                <h4 style='margin:6px 0;font-size:15px;color:#004080;'>{r['title']}</h4>
                <div style='font-size:13px;color:#444;'><b>{int(r.get('m2',0)):,} m²</b> · €{int(r.get('price',0)):,}</div>
                <div style='font-size:12px;color:#666;margin-top:4px;'>📍 {r.get('province','')} {r.get('locality','')}</div>
                <div style='font-size:11px;color:#999;margin-top:8px;'>👉 Haz clic en el marcador para ver detalles completos</div>
            </div>
            """

            folium.Marker(
                location=[r["lat"], r["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=r["title"],
                icon=folium.Icon(color="cadetblue", icon="home", prefix="fa")
            ).add_to(m)

    # render map and panel side-by-side inside main column
    map_col, panel_col = main_col.columns([2, 1])
    with map_col:
        st.header("Mapa de fincas (España & Portugal)")
        map_data = st_folium(m, width="100%", height=650, key="folium_map")

    # detect incoming plot_id from URL (robust handling)
    qp = st.query_params
    if "plot_id" in qp:
        # Fixed: nueva API devuelve string directo, no lista
        plot_id_value = qp["plot_id"]
        if isinstance(plot_id_value, list):
            plot_id_value = plot_id_value[0]
        st.session_state["selected_plot"] = plot_id_value
        # clear params solo si existen otros params
        new_qp = {k: v for k, v in qp.items() if k != "plot_id"}
        if len(new_qp) > 0:
            st.query_params.update(new_qp)
        else:
            st.query_params.clear()
        st.rerun()

    # Detect marker click from map
    if map_data and map_data.get("last_object_clicked") is not None:
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lon = map_data["last_object_clicked"]["lng"]
        # Find the plot with these exact coordinates
        for _, r in df.iterrows():
            if abs(r["lat"] - clicked_lat) < 0.0001 and abs(r["lon"] - clicked_lon) < 0.0001:
                st.session_state["selected_plot"] = r["id"]
                break

    # --- RIGHT: detail panel ---
    selected_plot = None
    if "selected_plot" in st.session_state:
        pid = st.session_state["selected_plot"]
        selected_plot = get_plot_by_id(pid)

    with panel_col:
        if selected_plot is None:
            st.markdown("### Preview\nSelecciona una finca en el mapa para ver detalles rápidos aquí.")
        else:
            st.markdown(f"### {selected_plot.get('title','Detalle finca')}")
            if selected_plot.get("image_path") and os.path.exists(selected_plot["image_path"]):
                st.image(selected_plot["image_path"], use_container_width=True)
            else:
                st.info("Imagen no disponible")

            st.markdown(f"**{selected_plot.get('description','-')}**")
            st.write(f"**Superficie:** {int(selected_plot.get('m2',0)):,} m²")
            st.write(f"**Precio:** €{int(selected_plot.get('price',0)):,}")
            st.write(f"**Tipo:** {selected_plot.get('type','-')}")
            st.write(f"**Ubicación:** {selected_plot.get('province','-')} / {selected_plot.get('locality','-')}")

            st.markdown("---")
            if st.button("Reserve (10%)"):
                amount = float(selected_plot.get("price", 0)) * 0.10
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('INSERT INTO reservations (id, plot_id, buyer_name, buyer_email, amount, kind, created_at) VALUES (?,?,?,?,?,?,?)',
                          (uuid.uuid4().hex, selected_plot['id'], 'Demo buyer', 'demo@example.com', amount, 'reservation', datetime.utcnow().isoformat()))
                conn.commit()
                conn.close()
                st.success(f"Reservation simulated (€{amount:,.2f}).")

            if st.button("Buy (100%)"):
                amount = float(selected_plot.get("price", 0))
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('INSERT INTO reservations (id, plot_id, buyer_name, buyer_email, amount, kind, created_at) VALUES (?,?,?,?,?,?,?)',
                          (uuid.uuid4().hex, selected_plot['id'], 'Demo buyer', 'demo@example.com', amount, 'purchase', datetime.utcnow().isoformat()))
                conn.commit()
                conn.close()
                st.success(f"Purchase simulated (€{amount:,.2f}).")

            if selected_plot.get("registry_note_path") and os.path.exists(selected_plot.get("registry_note_path")):
                # Fixed: proper file handling with context manager
                with open(selected_plot["registry_note_path"], 'rb') as f:
                    registry_data = f.read()
                st.download_button("Download registry note",
                                   data=registry_data,
                                   file_name=os.path.basename(selected_plot["registry_note_path"]),
                                   mime="application/pdf")
                
                # Botón para procesar nota catastral con pipeline de extracción
                if st.button("🔍 Analizar Nota Catastral", key="analyze_registry"):
                    with st.spinner("Procesando nota catastral... Esto puede tardar 30-60 segundos..."):
                        import subprocess
                        import sys
                        
                        # Copiar PDF a archirapid_extract para procesamiento
                        pdf_source = selected_plot["registry_note_path"]
                        pdf_dest = os.path.join("archirapid_extract", "test_catastral.pdf")
                        
                        try:
                            # Copiar archivo
                            import shutil
                            shutil.copy(pdf_source, pdf_dest)
                            
                            # Usar Python del venv explícitamente
                            venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
                            if not os.path.exists(venv_python):
                                venv_python = sys.executable  # fallback
                            
                            # Ejecutar pipeline con encoding UTF-8 para Windows
                            env = os.environ.copy()
                            env["PYTHONIOENCODING"] = "utf-8"
                            
                            result = subprocess.run(
                                [venv_python, "run_pipeline_simple.py"],
                                cwd="archirapid_extract",
                                capture_output=True,
                                text=True,
                                encoding='utf-8',
                                errors='replace',
                                timeout=120,
                                env=env
                            )
                            
                            if result.returncode == 0:
                                # Leer resultados
                                edificability_path = os.path.join("archirapid_extract", "catastro_output", "edificability.json")
                                if os.path.exists(edificability_path):
                                    import json
                                    with open(edificability_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                    
                                    st.success("✅ Análisis completado")
                                    st.markdown("### 📊 Resultados del Análisis")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Referencia Catastral", data.get('catastral_ref', 'N/A'))
                                        st.metric("Superficie Parcela", f"{data.get('surface_m2', 0):,.0f} m²")
                                    with col2:
                                        st.metric("Máximo Edificable", f"{data.get('max_buildable_m2', 0):,.2f} m²")
                                        st.metric("% Edificabilidad", f"{data.get('buildability_pct', 33)}%")
                                    
                                    # Mostrar planos vectorizados si existen
                                    contours_overlay = os.path.join("archirapid_extract", "catastro_output", "contours_visualization.png")
                                    contours_clean = os.path.join("archirapid_extract", "catastro_output", "contours_clean.png")
                                    
                                    if os.path.exists(contours_overlay) or os.path.exists(contours_clean):
                                        st.markdown("### 🗺️ Plano Vectorizado de la Parcela")
                                        
                                        tab1, tab2 = st.tabs(["🎯 Plano para CAD/BIM", "🔍 Validación Visual"])
                                        
                                        with tab1:
                                            if os.path.exists(contours_clean):
                                                st.image(contours_clean, caption="Contorno limpio para trabajo arquitectónico profesional (CAD/Revit/BIM)", width="stretch")
                                                st.caption("✅ Este plano está listo para exportar a formatos CAD (DXF/DWG) y usar con herramientas de IA, VR/AR y gemelos digitales")
                                            else:
                                                st.info("Plano limpio no disponible")
                                        
                                        with tab2:
                                            if os.path.exists(contours_overlay):
                                                st.image(contours_overlay, caption="Contorno detectado sobre documento catastral original", width="stretch")
                                                st.caption("🔍 Visualización de validación: muestra el contorno detectado sobre el PDF original")
                                            else:
                                                st.info("Visualización overlay no disponible")
                                    
                                    # Botón de descarga DXF para AutoCAD/Revit
                                    st.markdown("---")
                                    st.markdown("### 📥 Exportar a CAD/BIM")
                                    
                                    try:
                                        from export_dxf import create_dxf_from_cadastral_output
                                        
                                        # Generar DXF desde la salida del pipeline
                                        dxf_bytes = create_dxf_from_cadastral_output(
                                            output_dir=os.path.join("archirapid_extract", "catastro_output"),
                                            scale_factor=0.1  # 10 píxeles = 1 metro
                                        )
                                        
                                        if dxf_bytes:
                                            ref = data.get('catastral_ref', 'parcela')
                                            filename = f"ARCHIRAPID_{ref}.dxf"
                                            
                                            col_dxf1, col_dxf2 = st.columns([2, 1])
                                            
                                            with col_dxf1:
                                                st.download_button(
                                                    label="⬇️ Descargar DXF (AutoCAD/Revit)",
                                                    data=dxf_bytes,
                                                    file_name=filename,
                                                    mime="application/dxf",
                                                    help="Archivo DXF compatible con AutoCAD, Revit, BricsCAD y otros software CAD/BIM"
                                                )
                                            
                                            with col_dxf2:
                                                st.info(f"📐 Tamaño: {len(dxf_bytes) / 1024:.1f} KB")
                                            
                                            st.caption("💡 **Uso profesional**: Este archivo DXF puede importarse directamente en AutoCAD, Revit, ArchiCAD, BricsCAD y otros software de arquitectura. Incluye el polígono de la parcela con escala métrica.")
                                        else:
                                            st.warning("⚠️ No se pudo generar el archivo DXF. Verifica que el análisis se completó correctamente.")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Error generando DXF: {e}")
                                        st.caption("Contacta con soporte si el problema persiste.")
                                
                                else:
                                    st.warning("⚠️ Pipeline ejecutado pero no se generó edificability.json")
                                    st.text("STDOUT:")
                                    st.code(result.stdout)
                            else:
                                st.error(f"❌ Error en pipeline (código: {result.returncode})")
                                if result.stderr:
                                    st.text("STDERR:")
                                    st.code(result.stderr)
                                if result.stdout:
                                    st.text("STDOUT:")
                                    st.code(result.stdout)
                        
                        except subprocess.TimeoutExpired:
                            st.error("❌ Timeout: El procesamiento tardó más de 2 minutos")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")


            st.markdown("---")
            if st.button("Close preview"):
                st.session_state.pop("selected_plot", None)
                st.rerun()  # Fixed: removed deprecated experimental_rerun()

elif page == 'plots':
    st.title('Registro y Gestión de Fincas')
    tab = st.radio('Panel:', ['Registrar Nueva Finca', 'Ver Fincas'])
    if tab == 'Registrar Nueva Finca':
        with st.form('registro_finca'):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input('Título/Nombre de la Finca*')
                province = st.text_input('Provincia*')
                locality = st.text_input('Localidad')
                type_prop = st.selectbox('Tipo*', ['rural','urban','industrial'])
                m2 = st.number_input('Superficie (m²)*', min_value=1, value=100)
            with col2:
                height = st.number_input('Altura máxima (m)', min_value=0.0, value=6.0)
                price = st.number_input('Precio (€)*', min_value=0, value=100000)
                st.markdown('**Coordenadas geográficas**')
                st.caption("Formato admitido: decimal (ej: 36.5123) o grados/minutos/segundos (ej: 36º25'10''). Se convertirán automáticamente.")
                lat_input = st.text_input('Latitud*', value='')
                lon_input = st.text_input('Longitud*', value='')
                owner_name = st.text_input('Nombre del Propietario')
                owner_email = st.text_input('Email del Propietario')
            description = st.text_area('Descripción')
            images = st.file_uploader('Imágenes', accept_multiple_files=True, type=['jpg','jpeg','png'])
            registry_note = st.file_uploader('Nota Simple (PDF)', type=['pdf'])
            submitted = st.form_submit_button('Registrar Finca')

            if submitted:
                # Validar coordenadas
                def gms_to_decimal(coord):
                    import re
                    # Ejemplo: 36º25'10'' o 36 25 10 o 36°25'10" o 36d25m10s
                    # Intenta múltiples formatos
                    patterns = [
                        r"([\d.]+)[º°d][\s]*(\d+)['\s][\s]*(\d+)[\"s]?",  # 36º 25' 10"
                        r"([\d.]+)[º°d][\s]*(\d+)[\s]*(\d+)",  # 36 25 10
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, str(coord).strip())
                        if match:
                            deg, min_, sec = map(float, match.groups())
                            return deg + min_/60 + sec/3600
                    try:
                        return float(str(coord).replace(',', '.').strip())
                    except Exception:
                        return None

                lat = gms_to_decimal(lat_input)
                lon = gms_to_decimal(lon_input)
                if not all([title, province, m2, price, lat, lon]):
                    st.error('Campos obligatorios incompletos o coordenadas inválidas')
                else:
                    image_path = None
                    if images:
                        image_path = save_file(images[0], prefix='plot')
                    registry_path = None
                    if registry_note:
                        registry_path = save_file(registry_note, prefix='registry')
                    pdata = {
                        'id': uuid.uuid4().hex,
                        'title': title,
                        'description': description,
                        'lat': lat,
                        'lon': lon,
                        'm2': int(m2),
                        'height': float(height),
                        'price': float(price),
                        'type': type_prop,
                        'province': province,
                        'locality': locality,
                        'owner_name': owner_name,
                        'owner_email': owner_email,
                        'image_path': image_path,
                        'registry_note_path': registry_path,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_plot(pdata)
                    st.success('Finca registrada con éxito')
    else:
        st.title('Fincas Registradas')
        df = get_all_plots()
        # Filtrar duplicados por id y registros válidos
        df = df.drop_duplicates(subset=["id"])
        df = df[df["title"].notnull() & (df["title"] != "")]
        if df.shape[0] == 0:
            st.info('No hay fincas registradas')
        else:
            for idx, r in df.iterrows():
                with st.expander(f"{r['title']} — {r.get('province','')} — {r.get('m2',0)} m²"):
                    if r.get('image_path') and os.path.exists(r['image_path']):
                        st.image(r['image_path'], width=300)
                    st.write(r.get('description',''))
                    if r.get('registry_note_path') and os.path.exists(r['registry_note_path']):
                        # Fixed: proper file handling with context manager
                        with open(r['registry_note_path'],'rb') as f:
                            registry_data = f.read()
                        st.download_button('Descargar Nota Simple', 
                                        data=registry_data,
                                        file_name=os.path.basename(r['registry_note_path']),
                                        mime='application/pdf')

elif page == 'architects':
    from src.architect_manager import ArchitectManager
    arch_manager = ArchitectManager(DB_PATH, UPLOADS)

    st.title('Portal de Arquitectos')
    tab = st.radio('Seleccione una opción:', ['Registro', 'Acceso', 'Panel de Control'])

    if tab == 'Registro':
        with st.form('registro_form'):
            nombre = st.text_input('Nombre completo*')
            email = st.text_input('Email*')
            telefono = st.text_input('Teléfono')
            empresa = st.text_input('Empresa/Estudio')
            nif = st.text_input('NIF/CIF')
            submitted = st.form_submit_button('Registrar')
            
            if submitted:
                if not nombre or not email:
                    st.error('Nombre y email son obligatorios')
                else:
                    success, result = arch_manager.register_architect({
                        'name': nombre,
                        'email': email,
                        'phone': telefono,
                        'company': empresa,
                        'nif': nif
                    })
                    if success:
                        st.success('¡Registro completado con éxito!')
                        st.session_state['arch_id'] = result
                    else:
                        st.error(result)

    elif tab == 'Acceso':
        email_login = st.text_input('Email registrado')
        if st.button('Acceder'):
            if email_login:
                architect = arch_manager.get_architect(email=email_login)
                if architect:
                    st.success(f"Bienvenido/a, {architect['name']}")
                    st.session_state['arch_id'] = architect['id']
                else:
                    st.error('Email no encontrado')

    else:
        if 'arch_id' not in st.session_state:
            st.warning('Debe iniciar sesión primero')
        else:
            arch = arch_manager.get_architect(architect_id=st.session_state['arch_id'])
            if not arch:
                st.error('Error al cargar los datos')
            else:
                st.header(f"Bienvenido/a {arch['name']}")
                if arch.get('company'):
                    st.subheader(f"🏢 {arch['company']}")

                # subscription and project actions
                subscription = arch_manager.get_subscription(arch['id'])
                projects_count = arch_manager.count_projects(arch['id'])

                st.markdown('---')
                st.markdown('### Planes Disponibles')
                PLANS = {"BASIC": {"limit": 3, "price": 200}, 
                        "STANDARD": {"limit": 6, "price": 350}, 
                        "PRO": {"limit": 10, "price": 600}}

                cols = st.columns(len(PLANS))
                for i, (plan_name, details) in enumerate(PLANS.items()):
                    with cols[i]:
                        st.markdown(f"### {plan_name}")
                        st.markdown(f"**{details['limit']} proyectos** — €{details['price']}")
                        if st.button(f"Contratar {plan_name}", key=f"plan_{plan_name}"):
                            success, result = arch_manager.create_subscription(
                                arch['id'], plan_name, details['limit'], details['price'])
                            if success:
                                st.success('Plan contratado')
                                st.rerun()
                            else:
                                st.error(result)

                st.markdown('---')
                st.header('Gestión de Proyectos')
                if not subscription:
                    st.error('Necesita contratar un plan antes de subir proyectos')
                elif projects_count >= subscription['plan_limit']:
                    st.error(f"Ha alcanzado el límite de su plan ({projects_count}/{subscription['plan_limit']})")
                else:
                    with st.form('subida_proyecto'):
                        title = st.text_input('Título del proyecto*')
                        area_m2 = st.number_input('Superficie (m²)', min_value=1, value=100)
                        max_height = st.number_input('Altura máxima (m)', min_value=1.0, value=6.0)
                        style = st.selectbox('Estilo', ['Moderno','Tradicional','Minimalista','Rústico','Industrial','Otro'])
                        description = st.text_area('Descripción')
                        files = st.file_uploader('Archivos (varios)', accept_multiple_files=True, 
                                               type=['pdf','png','jpg','jpeg','zip','ifc','rvt','dwg'])
                        submit_project = st.form_submit_button('Subir Proyecto')

                        if submit_project:
                            if not title:
                                st.error('El título del proyecto es obligatorio')
                            else:
                                project_id = uuid.uuid4().hex
                                saved_paths = []
                                if files:
                                    for f in files:
                                        saved_paths.append(save_file(f, prefix='proj'))
                                pdata = {
                                    'id': project_id,
                                    'title': title,
                                    'architect_name': arch['name'],
                                    'architect_id': arch['id'],
                                    'area_m2': int(area_m2),
                                    'max_height': float(max_height),
                                    'style': style,
                                    'price': 0,
                                    'file_path': saved_paths[0] if saved_paths else None,
                                    'description': description,
                                    'created_at': datetime.utcnow().isoformat()
                                }
                                insert_project(pdata)
                                # store metadata list
                                if saved_paths:
                                    meta_path = os.path.join(UPLOADS, f"projfiles_{project_id}.json")
                                    with open(meta_path, 'w', encoding='utf-8') as jf:
                                        json.dump(saved_paths, jf)
                                st.success('Proyecto subido con éxito')
else:
    st.error('Página no encontrada')
    st.write(f'page={page}')