import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime
import base64
import json

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, "data.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

st.set_page_config(page_title="ARCHIRAPID MVP (fixed)", layout="wide")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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


# Minimal pages: Home / plots / architects
init_db()

st.markdown("""
<nav style='background:#f8f9fa;padding:8px;border-radius:6px;margin-bottom:12px;'>
  <a href='/?page=Home' style='margin-right:12px;'>Inicio</a>
  <a href='/?page=plots' style='margin-right:12px;'>Registro Fincas</a>
  <a href='/?page=architects' style='margin-right:12px;'>Arquitectos</a>
</nav>
""", unsafe_allow_html=True)

qp = st.query_params
page = qp.get('page', ['Home'])[0]

if page == 'Home':
    st.title('ARCHIRAPID — Home')
    df = get_all_plots()
    st.write(f"Fincas registradas: {df.shape[0]}")

elif page == 'plots':
    st.title('Registro de Fincas (fixed)')
    with st.form('registro'):
        title = st.text_input('Título')
        province = st.text_input('Provincia')
        m2 = st.number_input('m2', min_value=1, value=100)
        lat = st.number_input('Latitud', value=40.0)
        lon = st.number_input('Longitud', value=-3.0)
        price = st.number_input('Precio', min_value=0, value=100000)
        submitted = st.form_submit_button('Registrar')
    if submitted:
        pdata = {'id': uuid.uuid4().hex, 'title': title, 'description': '', 'lat': lat, 'lon': lon, 'm2': m2, 'height': 6.0, 'price': price, 'type': 'rural', 'province': province, 'locality': '', 'owner_name': '', 'owner_email': '', 'image_path': None, 'registry_note_path': None, 'created_at': datetime.utcnow().isoformat()}
        insert_plot(pdata)
        st.success('Registrada')

elif page == 'architects':
    from src.architect_manager import ArchitectManager
    arch = ArchitectManager(DB_PATH, UPLOADS)
    st.title('Portal Arquitectos (fixed)')
    tab = st.radio('Acción', ['Registro','Acceso'])
    if tab == 'Registro':
        with st.form('reg'):
            name = st.text_input('Nombre')
            email = st.text_input('Email')
            submitted = st.form_submit_button('Registrar')
        if submitted:
            ok, res = arch.register_architect({'name': name, 'email': email, 'phone': '', 'company': '', 'nif': ''})
            if ok:
                st.success('Registrado')
            else:
                st.error(res)
    else:
        st.info('Por favor use el portal completo en app.py cuando esté reparado')
