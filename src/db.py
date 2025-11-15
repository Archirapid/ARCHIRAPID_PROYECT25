"""Base de datos centralizada para ArchiRapid (SQLite)."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional, Iterator

BASE_PATH = Path(__file__).parent.parent
DB_PATH = BASE_PATH / 'data.db'

def get_conn():
    """Devuelve conexión SQLite con row_factory habilitado para acceder por nombre de columna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def transaction() -> Iterator[sqlite3.Cursor]:
    """Context manager para operaciones atómicas.

    Uso:
        with transaction() as cur:
            cur.execute(...)
            cur.execute(...)
    Hace commit automático si no hay excepción; rollback si falla.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def ensure_tables():
    with transaction() as c:
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
            buyer_phone TEXT, buyer_nif TEXT, method TEXT, status TEXT, timestamp TEXT,
            card_last4 TEXT
        )""")

def insert_plot(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO plots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (data['id'], data['title'], data['description'], data['lat'], data['lon'], data['m2'], data['height'],
                   data['price'], data['type'], data['province'], data['locality'], data['owner_name'], data['owner_email'],
                   data.get('image_path'), data.get('registry_note_path'), data['created_at']))

def insert_project(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (data['id'], data['title'], data['architect_name'], data['area_m2'], data['max_height'], data['style'],
                   data['price'], data.get('file_path'), data['description'], data['created_at']))

def insert_payment(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO payments VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (data['payment_id'], data['amount'], data['concept'], data['buyer_name'], data['buyer_email'],
                   data['buyer_phone'], data['buyer_nif'], data['method'], data['status'], data['timestamp'], data.get('card_last4'), data.get('card_last4')))

def get_all_plots():
    ensure_tables(); conn = get_conn(); import pandas as pd
    try:
        df = pd.read_sql_query('SELECT * FROM plots', conn)
    finally:
        conn.close()
    return df

def get_all_projects():
    ensure_tables(); conn = get_conn(); import pandas as pd
    try:
        df = pd.read_sql_query('SELECT * FROM projects', conn)
    finally:
        conn.close()
    return df

def get_plot_by_id(pid: str) -> Optional[Dict]:
    ensure_tables(); conn = get_conn(); c = conn.cursor(); c.execute('SELECT * FROM plots WHERE id=?', (pid,))
    row = c.fetchone(); conn.close()
    if not row:
        return None
    # Gracias a row_factory podemos acceder por nombre
    return {k: row[k] for k in row.keys()}

def counts() -> Dict[str,int]:
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    out = {}
    for table in ['plots','projects','payments']:
        c.execute(f'SELECT COUNT(*) FROM {table}'); out[table] = c.fetchone()[0]
    conn.close(); return out
