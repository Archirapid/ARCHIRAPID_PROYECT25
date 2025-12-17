# db_setup.py
import sqlite3
from pathlib import Path

DB_PATH = Path("archirapid.db")


def insertar_planes_iniciales(conn):
    """Inserta planes iniciales si la tabla `planes` está vacía.

    Planes a insertar:
      - Estudiante: precio 0.0, limite_proyectos 1
      - Básico: precio 99.0, limite_proyectos 3
      - Estándar: precio 179.0, limite_proyectos 6
      - Premium: precio 249.0, limite_proyectos 10
    """
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(1) FROM planes")
        cnt = c.fetchone()[0]
    except Exception:
        # tabla puede no existir todavía
        cnt = 0
    if cnt == 0:
        plans = [
            (None, 'Estudiante', 0.0, 1),
            (None, 'Básico', 99.0, 3),
            (None, 'Estándar', 179.0, 6),
            (None, 'Premium', 249.0, 10),
        ]
        c.executemany(
            "INSERT INTO planes (id, nombre_plan, precio_mensual, limite_proyectos) VALUES (?,?,?,?)",
            plans,
        )
        conn.commit()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # users (basic)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        role TEXT, -- 'architect','owner','client','admin'
        company TEXT,
        created_at TEXT
    )
    """)
    # architects table (profiles)
    c.execute("""
    CREATE TABLE IF NOT EXISTS architects (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        nif TEXT,
        plan TEXT,
        plan_limit INTEGER,
        plan_price REAL,
        created_at TEXT
    )
    """)
    # subscriptions/payments
    c.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id TEXT PRIMARY KEY,
        architect_id TEXT,
        plan TEXT,
        price REAL,
        created_at TEXT
    )
    """)
    # projects by architects
    c.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        architect_id TEXT,
        title TEXT,
        description TEXT,
        area_m2 REAL,
        price REAL,
        files_json TEXT,
        created_at TEXT
    )
    """)
    # plots / fincas
    c.execute("""
    CREATE TABLE IF NOT EXISTS plots (
        id TEXT PRIMARY KEY,
        owner_id TEXT,
        title TEXT,
        cadastral_ref TEXT,
        surface_m2 REAL,
        buildable_m2 REAL,
        is_urban INTEGER,
        vector_geojson TEXT,
        registry_note_path TEXT,
        price REAL,
        lat REAL,
        lon REAL,
        status TEXT, -- 'draft','published','reserved','sold'
        created_at TEXT
    )
    """)
    # reservations / purchases
    c.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id TEXT PRIMARY KEY,
        plot_id TEXT,
        buyer_name TEXT,
        buyer_email TEXT,
        amount REAL,
        kind TEXT, -- 'reservation' or 'purchase'
        created_at TEXT
    )
    """)
    # proposals from architects to owners
    c.execute("""
    CREATE TABLE IF NOT EXISTS proposals (
        id TEXT PRIMARY KEY,
        architect_id TEXT,
        plot_id TEXT,
        project_id TEXT,  -- added in sprint2
        proposal_text TEXT,
        estimated_budget REAL,
        deadline_days INTEGER,
        sketch_image_path TEXT,
        status TEXT,  -- 'pending','accepted','rejected'
        created_at TEXT,
        responded_at TEXT,
        delivery_format TEXT,  -- added in sprint2
        delivery_price REAL,   -- added in sprint2
        supervision_fee REAL,  -- added in sprint2
        visa_fee REAL,         -- added in sprint2
        total_cliente REAL,     -- added in sprint2
        commission REAL         -- added in sprint2
    )
    """)
    # commissions for architects
    c.execute("""
    CREATE TABLE IF NOT EXISTS commissions (
        id TEXT PRIMARY KEY,
        proposal_id TEXT,
        architect_id TEXT,
        client_id TEXT,
        amount REAL,
        paid INTEGER,  -- 0 or 1
        created_at TEXT
    )
    """)
    # payments from clients
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        proposal_id TEXT,
        client_id TEXT,
        amount REAL,
        status TEXT,  -- 'pending','completed','failed'
        created_at TEXT
    )
    """)
    # Tabla de planes (suscripciones) — se añade sin reemplazar tablas existentes
    c.execute("""
    CREATE TABLE IF NOT EXISTS planes (
        id INTEGER PRIMARY KEY,
        nombre_plan TEXT,
        precio_mensual REAL,
        limite_proyectos INTEGER
    )
    """)

    # Tabla de arquitectos (perfil comercial) vinculada a `planes`
    c.execute("""
    CREATE TABLE IF NOT EXISTS arquitectos (
        id INTEGER PRIMARY KEY,
        nombre TEXT,
        email TEXT UNIQUE,
        telefono TEXT,
        especialidad TEXT,
        plan_id INTEGER,
        FOREIGN KEY(plan_id) REFERENCES planes(id)
    )
    """)

    # Tabla de proyectos específicos de arquitectos (gestión interna)
    c.execute("""
    CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY,
        arquitecto_id INTEGER,
        titulo TEXT,
        estilo TEXT,
        m2_construidos REAL,
        presupuesto_ejecucion REAL,
        m2_parcela_minima REAL,
        alturas INTEGER,
        pdf_path TEXT,
        FOREIGN KEY(arquitecto_id) REFERENCES arquitectos(id)
    )
    """)

    # Tabla de ventas/proyectos (registro de transacciones y comisiones)
    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas_proyectos (
        id INTEGER PRIMARY KEY,
        proyecto_id INTEGER,
        cliente_email TEXT,
        tipo_compra TEXT,
        precio_venta REAL,
        comision_archirapid REAL,
        fecha TEXT
    )
    """)

    # Insertar planes iniciales sólo si la tabla `planes` está vacía
    insertar_planes_iniciales(conn)
    conn.commit()
    conn.close()
    print(f"DB initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()