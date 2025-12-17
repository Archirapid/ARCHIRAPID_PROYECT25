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
        try:
            c.execute("ALTER TABLE plots ADD COLUMN photo_paths TEXT")
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
        # Versión nueva simplificada (mantener compatibilidad con esquema anterior extenso)
        c.execute("""CREATE TABLE IF NOT EXISTS proposals (
            id TEXT PRIMARY KEY,
            architect_id TEXT,
            plot_id TEXT,
            proposal_text TEXT,
            estimated_budget REAL,
            deadline_days INTEGER,
            sketch_image_path TEXT,
            status TEXT,
            created_at TEXT,
            responded_at TEXT,
            delivery_format TEXT DEFAULT 'PDF',
            delivery_price REAL DEFAULT 1200,
            supervision_fee REAL DEFAULT 0,
            visa_fee REAL DEFAULT 0,
            total_cliente REAL DEFAULT 0,
            commission REAL DEFAULT 0,
            project_id TEXT
        )""")
        # Migraciones seguras para columnas nuevas usadas por nueva API insert_proposal
        try:
            c.execute("ALTER TABLE proposals ADD COLUMN message TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE proposals ADD COLUMN price REAL")
        except Exception:
            pass
        
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
        
        # Tabla additional_services (servicios post-proyecto: dirección obra, visados, modificaciones)
        c.execute("""CREATE TABLE IF NOT EXISTS additional_services (
            id TEXT PRIMARY KEY,
            proposal_id TEXT,
            client_id TEXT,
            architect_id TEXT,
            service_type TEXT,
            description TEXT,
            price REAL,
            commission REAL,
            total_cliente REAL,
            status TEXT,
            created_at TEXT,
            quoted_at TEXT,
            accepted_at TEXT,
            paid BOOLEAN DEFAULT 0
        )""")
        
        # Índices para servicios adicionales
        c.execute("CREATE INDEX IF NOT EXISTS idx_additional_services_client ON additional_services(client_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_additional_services_architect ON additional_services(architect_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_additional_services_proposal ON additional_services(proposal_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_additional_services_status ON additional_services(status)")

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
        # Insert or replace a project; architect_id is optional but supported so
        # that project creation from UI flows is reliably linked to an architect.
        c.execute("""INSERT OR REPLACE INTO projects (
            id,title,architect_name,architect_id,area_m2,max_height,style,price,file_path,description,created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            data['id'], data['title'], data.get('architect_name'), data.get('architect_id'),
            data.get('area_m2'), data.get('max_height'), data.get('style'), data.get('price'),
            data.get('file_path'), data.get('description'), data['created_at']
        ))

        # Record event for observability and tests
        try:
            from src.logger import log
            log('project_created', project_id=data['id'], architect_id=data.get('architect_id'), title=data.get('title'))
        except Exception:
            pass

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

def insert_architect(data: Dict):
    """Inserta o reemplaza un arquitecto."""
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT OR REPLACE INTO architects (
            id,name,email,phone,company,nif,created_at
        ) VALUES (?,?,?,?,?,?,?)""", (
            data['id'], data['name'], data['email'], data.get('phone'), data.get('company'), data.get('nif'), data['created_at']
        ))

def update_project_architect_id(project_id: str, architect_id: str):
    """Actualiza el arquitecto asociado a un proyecto."""
    ensure_tables()
    with transaction() as c:
        c.execute("UPDATE projects SET architect_id=? WHERE id=?", (architect_id, project_id))


def update_project_fields(project_id: str, fields: Dict):
    """Actualizar campos concretos de un proyecto.

    Sólo actualiza las columnas proporcionadas en `fields`.
    """
    if not fields:
        return
    ensure_tables()
    allowed = {
        'title','architect_name','architect_id','area_m2','max_height','style','price','file_path','description',
        'm2_construidos','m2_parcela_minima','m2_parcela_maxima','habitaciones','banos','garaje','plantas','certificacion_energetica',
        'tipo_proyecto','foto_principal','galeria_fotos','modelo_3d_glb','render_vr','planos_pdf','planos_dwg','memoria_pdf'
    }
    set_pairs = []
    values = []
    for k, v in fields.items():
        if k in allowed:
            set_pairs.append(f"{k}=?")
            values.append(v)
    if not set_pairs:
        return
    values.append(project_id)
    sql = f"UPDATE projects SET {', '.join(set_pairs)} WHERE id=?"
    with transaction() as c:
        c.execute(sql, tuple(values))

def get_plot_by_id(pid: str) -> Optional[Dict]:
    ensure_tables(); conn = get_conn(); c = conn.cursor(); c.execute('SELECT * FROM plots WHERE id=?', (pid,))
    row = c.fetchone(); conn.close()
    if not row:
        return None
    # Gracias a row_factory podemos acceder por nombre
    return {k: row[k] for k in row.keys()}


def get_all_provinces() -> list:
    """Devuelve la lista de provincias disponibles en la tabla `plots`.
    Retorna una lista de strings (puede estar vacía).
    """
    ensure_tables()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT province FROM plots WHERE province IS NOT NULL AND province<>'' ORDER BY province")
        rows = cur.fetchall()
        return [r[0] for r in rows if r[0]]
    finally:
        conn.close()


def get_featured_projects(limit: int = 3) -> list:
    """Devuelve proyectos destacados (por defecto los últimos `limit` publicados).
    Cada proyecto es un dict con campos: id,title,area_m2,price,foto_principal,description
    """
    ensure_tables()
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id,title,area_m2,price,foto_principal,description FROM projects ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        out = []
        for r in rows:
            out.append({cols[i]: r[i] for i in range(len(cols))})
        return out
    finally:
        conn.close()

def counts() -> Dict[str,int]:
    ensure_tables(); conn = get_conn(); c = conn.cursor()
    out = {}
    for table in ['plots','projects','payments']:
        c.execute(f'SELECT COUNT(*) FROM {table}'); out[table] = c.fetchone()[0]
    conn.close(); return out

def insert_proposal(data: Dict):
    """Inserta propuesta en la tabla proposals."""
    ensure_tables()
    with transaction() as c:
        # Detectar si columnas message/price existen (compatibilidad con esquema anterior)
        has_message = True
        has_price = True
        try:
            c.execute("SELECT message FROM proposals LIMIT 1")
        except Exception:
            has_message = False
        try:
            c.execute("SELECT price FROM proposals LIMIT 1")
        except Exception:
            has_price = False
        if has_message and has_price:
            c.execute("""INSERT OR REPLACE INTO proposals (
                id,plot_id,architect_id,project_id,message,price,status,created_at
            ) VALUES (?,?,?,?,?,?,?,?)""", (
                data['id'], data['plot_id'], data['architect_id'], data.get('project_id'), data.get('message'),
                data.get('price'), data.get('status','pending'), data['created_at']
            ))
        else:
            # Insert en columnas legacy (proposal_text, estimated_budget) mapeando valores
            c.execute("""INSERT OR REPLACE INTO proposals (
                id,architect_id,plot_id,proposal_text,estimated_budget,deadline_days,sketch_image_path,status,created_at,project_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?)""", (
                data['id'], data['architect_id'], data['plot_id'], data.get('message'), data.get('price'),
                data.get('deadline_days', 30), None, data.get('status','pending'), data['created_at'], data.get('project_id')
            ))

def get_proposals_for_plot(plot_id: str):
    ensure_tables(); conn = get_conn(); import pandas as pd
    try:
        df = pd.read_sql_query('SELECT * FROM proposals WHERE plot_id = ?', conn, params=(plot_id,))
    finally:
        conn.close()
    return df

def update_proposal_status(proposal_id: str, new_status: str):
    """Actualiza el estado de una propuesta (pending->accepted/rejected)."""
    ensure_tables()
    with transaction() as c:
        # Asegurar columna responded_at (legacy ya la tiene, pero migración defensiva)
        try:
            c.execute("ALTER TABLE proposals ADD COLUMN responded_at TEXT")
        except Exception:
            pass
        from datetime import datetime
        responded_at = datetime.utcnow().isoformat()
        try:
            c.execute("UPDATE proposals SET status=?, responded_at=? WHERE id=?", (new_status, responded_at, proposal_id))
        except Exception:
            # Si no existe responded_at, degradar sin timestamp
            c.execute("UPDATE proposals SET status=? WHERE id=?", (new_status, proposal_id))

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


# =====================================================
# SERVICIOS ADICIONALES (Post-Proyecto)
# =====================================================

def insert_additional_service(data: Dict):
    """Inserta un nuevo servicio adicional solicitado por cliente."""
    ensure_tables()
    with transaction() as c:
        c.execute("""INSERT INTO additional_services (
            id, proposal_id, client_id, architect_id, service_type, 
            description, price, commission, total_cliente, status, created_at, paid
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (
            data['id'], data.get('proposal_id'), data['client_id'], data['architect_id'],
            data['service_type'], data.get('description', ''), 
            data.get('price', 0), data.get('commission', 0), data.get('total_cliente', 0),
            data.get('status', 'solicitado'), data['created_at'], data.get('paid', 0)
        ))

def get_additional_services_by_client(client_id: str):
    """Obtiene todos los servicios adicionales de un cliente."""
    ensure_tables()
    conn = get_conn()
    import pandas as pd
    try:
        df = pd.read_sql_query("""
            SELECT s.*, a.name as architect_name, a.email as architect_email
            FROM additional_services s
            LEFT JOIN architects a ON s.architect_id = a.id
            WHERE s.client_id = ?
            ORDER BY s.created_at DESC
        """, conn, params=(client_id,))
    finally:
        conn.close()
    return df

def get_additional_services_by_architect(architect_id: str):
    """Obtiene todos los servicios adicionales para un arquitecto."""
    ensure_tables()
    conn = get_conn()
    import pandas as pd
    try:
        df = pd.read_sql_query("""
            SELECT s.*, c.name as client_name, c.email as client_email
            FROM additional_services s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.architect_id = ?
            ORDER BY s.created_at DESC
        """, conn, params=(architect_id,))
    finally:
        conn.close()
    return df

def update_additional_service_quote(service_id: str, price: float, commission_rate: float):
    """Arquitecto cotiza un servicio adicional (estado: solicitado -> cotizado)."""
    ensure_tables()
    commission = price * commission_rate
    total_cliente = price + commission
    
    with transaction() as c:
        from datetime import datetime
        quoted_at = datetime.utcnow().isoformat()
        c.execute("""UPDATE additional_services 
                     SET price=?, commission=?, total_cliente=?, status='cotizado', quoted_at=?
                     WHERE id=?""", 
                  (price, commission, total_cliente, quoted_at, service_id))

def update_additional_service_status(service_id: str, new_status: str):
    """Actualiza estado de servicio adicional (cotizado -> aceptado/rechazado)."""
    ensure_tables()
    with transaction() as c:
        from datetime import datetime
        if new_status == 'aceptado':
            accepted_at = datetime.utcnow().isoformat()
            c.execute("UPDATE additional_services SET status=?, accepted_at=? WHERE id=?", 
                      (new_status, accepted_at, service_id))
        else:
            c.execute("UPDATE additional_services SET status=? WHERE id=?", (new_status, service_id))

def mark_additional_service_paid(service_id: str):
    """Marca servicio adicional como pagado."""
    ensure_tables()
    with transaction() as c:
        c.execute("UPDATE additional_services SET paid=1 WHERE id=?", (service_id,))
