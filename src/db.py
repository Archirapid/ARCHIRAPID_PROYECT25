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
        # Migración segura: agregar columnas nuevas si no existen
        try:
            c.execute("ALTER TABLE plots ADD COLUMN address TEXT")
        except Exception:
            pass  # Columna ya existe
        try:
            c.execute("ALTER TABLE plots ADD COLUMN owner_phone TEXT")
        except Exception:
            pass  # Columna ya existe
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
        c.execute("""CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT, email TEXT, phone TEXT, address TEXT, preferences TEXT, created_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            plot_id TEXT, buyer_name TEXT, buyer_email TEXT, amount REAL, kind TEXT, created_at TEXT
        )""")
        
        # Tabla architects (arquitectos registrados)
        c.execute("""CREATE TABLE IF NOT EXISTS architects (
            id TEXT PRIMARY KEY,
            name TEXT, email TEXT UNIQUE, phone TEXT, company TEXT, nif TEXT,
            created_at TEXT
        )""")
        
        # Tabla subscriptions (suscripciones de arquitectos)
        c.execute("""CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            architect_id TEXT,
            plan_type TEXT,
            price REAL,
            monthly_proposals_limit INTEGER,
            commission_rate REAL,
            status TEXT,
            start_date TEXT,
            end_date TEXT,
            created_at TEXT
        )""")
        
        # Tabla proposals (propuestas de arquitectos a propietarios)
        c.execute("""CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            plot_id TEXT,
            architect_id TEXT,
            project_id TEXT,
            message TEXT,
            price REAL,
            status TEXT,
            created_at TEXT
        )""")
        
        # Migración segura: agregar columnas nuevas a projects si no existen
        try:
            c.execute("ALTER TABLE projects ADD COLUMN architect_id TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN m2_construidos INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN m2_parcela_minima INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN m2_parcela_maxima INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN habitaciones INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN banos INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN garaje INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN plantas INTEGER")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN certificacion_energetica TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN tipo_proyecto TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN foto_principal TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN galeria_fotos TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN modelo_3d_glb TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN planos_pdf TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN planos_dwg TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE projects ADD COLUMN memoria_pdf TEXT")
        except Exception:
            pass
        
        # Índices para mejorar filtrado futuro
        c.execute("CREATE INDEX IF NOT EXISTS idx_plots_province ON plots(province)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_projects_style ON projects(style)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_projects_architect ON projects(architect_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_architect ON subscriptions(architect_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_proposals_plot ON proposals(plot_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_proposals_architect ON proposals(architect_id)")
        # Índice único para email de clientes (si hay duplicados previos fallará, lo capturamos)
        try:
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")
        except Exception:
            pass
        # Índices adicionales para acelerar búsquedas de reservas
        c.execute("CREATE INDEX IF NOT EXISTS idx_reservations_plot ON reservations(plot_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_reservations_kind ON reservations(kind)")

def insert_plot(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO plots (
            id,title,description,lat,lon,m2,height,price,type,province,locality,owner_name,owner_email,image_path,registry_note_path,created_at,address,owner_phone
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (data['id'], data['title'], data['description'], data['lat'], data['lon'], data['m2'], data['height'],
         data['price'], data['type'], data['province'], data['locality'], data['owner_name'], data['owner_email'],
         data.get('image_path'), data.get('registry_note_path'), data['created_at'], data.get('address'), data.get('owner_phone')))

def insert_project(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO projects (
            id,title,architect_name,area_m2,max_height,style,price,file_path,description,created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (data['id'], data['title'], data['architect_name'], data['area_m2'], data['max_height'], data['style'],
         data['price'], data.get('file_path'), data['description'], data['created_at']))

def insert_payment(data: Dict):
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO payments (
            payment_id,amount,concept,buyer_name,buyer_email,buyer_phone,buyer_nif,method,status,timestamp,card_last4
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (data['payment_id'], data['amount'], data['concept'], data['buyer_name'], data['buyer_email'],
         data['buyer_phone'], data['buyer_nif'], data['method'], data['status'], data['timestamp'], data.get('card_last4')))

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

# Cache ligera en memoria para counts (TTL segundos)
_COUNTS_CACHE: Dict[str,int] | None = None
_COUNTS_TS: float | None = None
_COUNTS_TTL = 5  # segundos

def cached_counts() -> Dict[str,int]:
    import time
    global _COUNTS_CACHE, _COUNTS_TS
    now = time.time()
    if _COUNTS_CACHE is None or _COUNTS_TS is None or (now - _COUNTS_TS) > _COUNTS_TTL:
        _COUNTS_CACHE = counts()
        _COUNTS_TS = now
    return _COUNTS_CACHE.copy()
