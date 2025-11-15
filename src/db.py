"""Base de datos centralizada para ArchiRapid (SQLite)."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

BASE_PATH = Path(__file__).parent.parent
DB_PATH = BASE_PATH / 'data.db'

def get_conn():
    return sqlite3.connect(DB_PATH)

def ensure_tables():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS plots (
        id TEXT PRIMARY KEY,
        title TEXT, description TEXT, lat REAL, lon REAL,
        m2 INTEGER, height REAL, price REAL, type TEXT, province TEXT,
        locality TEXT, owner_name TEXT, owner_email TEXT,
        image_path TEXT, registry_note_path TEXT, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        title TEXT, architect_name TEXT, area_m2 INTEGER, max_height REAL,
        style TEXT, price REAL, file_path TEXT, description TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        amount REAL, concept TEXT, buyer_name TEXT, buyer_email TEXT,
        buyer_phone TEXT, buyer_nif TEXT, method TEXT, status TEXT, timestamp TEXT
    )""")
    conn.commit(); conn.close()

def insert_plot(data: Dict):
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO plots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data['id'], data['title'], data['description'], data['lat'], data['lon'], data['m2'], data['height'],
               data['price'], data['type'], data['province'], data['locality'], data['owner_name'], data['owner_email'],
               data.get('image_path'), data.get('registry_note_path'), data['created_at']))
    conn.commit(); conn.close()

def insert_project(data: Dict):
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (data['id'], data['title'], data['architect_name'], data['area_m2'], data['max_height'], data['style'],
               data['price'], data.get('file_path'), data['description'], data['created_at']))
    conn.commit(); conn.close()

def insert_payment(data: Dict):
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO payments VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (data['payment_id'], data['amount'], data['concept'], data['buyer_name'], data['buyer_email'],
               data['buyer_phone'], data['buyer_nif'], data['method'], data['status'], data['timestamp'], data.get('card_last4')))
    conn.commit(); conn.close()

def get_all_plots():
    ensure_tables(); conn = get_conn(); import pandas as pd
    df = pd.read_sql_query('SELECT * FROM plots', conn); conn.close(); return df

def get_all_projects():
    ensure_tables(); conn = get_conn(); import pandas as pd
    df = pd.read_sql_query('SELECT * FROM projects', conn); conn.close(); return df

def get_plot_by_id(pid: str) -> Optional[Dict]:
    ensure_tables(); conn = get_conn(); c = conn.cursor(); c.execute('SELECT * FROM plots WHERE id=?', (pid,))
    row = c.fetchone(); conn.close()
    if not row: return None
    cols = ['id','title','description','lat','lon','m2','height','price','type','province','locality','owner_name','owner_email','image_path','registry_note_path','created_at']
    return dict(zip(cols,row))

def counts() -> Dict[str,int]:
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    out = {}
    for table in ['plots','projects','payments']:
        c.execute(f'SELECT COUNT(*) FROM {table}'); out[table] = c.fetchone()[0]
    conn.close(); return out
