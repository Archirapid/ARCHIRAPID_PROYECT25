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

# Configuration
BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

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

# Get current page from query params
page = st.query_params.get('page', ['Home'])[0]

if page == 'Home':
    st.title('ARCHIRAPID — Home')
    st.write('Listado de fincas registradas y mapa')
    df = get_all_plots()
    if df.shape[0] == 0:
        st.info('No hay fincas registradas aún')
    else:
        for idx, r in df.iterrows():
            st.markdown(f"**{r['title']}** — {r.get('province','')} — {r.get('m2',0)} m² — €{int(r.get('price',0))}")

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
                lat = st.number_input('Latitud*', value=40.0)
                lon = st.number_input('Longitud*', value=-3.0)
                owner_name = st.text_input('Nombre del Propietario')
                owner_email = st.text_input('Email del Propietario')
            description = st.text_area('Descripción')
            images = st.file_uploader('Imágenes', accept_multiple_files=True, type=['jpg','jpeg','png'])
            registry_note = st.file_uploader('Nota Simple (PDF)', type=['pdf'])
            submitted = st.form_submit_button('Registrar Finca')

            if submitted:
                if not all([title, province, m2, price, lat, lon]):
                    st.error('Campos obligatorios incompletos')
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
                        'lat': float(lat),
                        'lon': float(lon),
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
        if df.shape[0] == 0:
            st.info('No hay fincas registradas')
        else:
            for idx, r in df.iterrows():
                with st.expander(f"{r['title']} — {r.get('province','')} — {r.get('m2',0)} m²"):
                    if r.get('image_path') and os.path.exists(r['image_path']):
                        st.image(r['image_path'], width=300)
                    st.write(r.get('description',''))
                    if r.get('registry_note_path') and os.path.exists(r['registry_note_path']):
                        st.download_button('Descargar Nota Simple', 
                                        data=open(r['registry_note_path'],'rb').read(),
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