# db_setup.py
import sqlite3
from pathlib import Path

DB_PATH = Path("archirapid.db")

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
    conn.commit()
    conn.close()
    print(f"DB initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()