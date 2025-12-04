"""Seed demo dataset: 3 urban plots + 1 compatible project.
Idempotent: purges plots/projects/reservations/proposals then inserts curated demo records.
Run: python seed_demo.py
"""
import sqlite3, os, uuid, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'archirapid.db')
NOW = datetime.datetime.utcnow().isoformat()

PLOTS = [
    {
        'id': 'finca_es_malaga',
        'title': 'Finca Urbana Málaga',
        'surface_m2': 900,
        'buildable_m2': 810,
        'is_urban': 1,
        'price': 185000,
        'lat': 36.7213,
        'lon': -4.4217,
        'status': 'published'
    },
    {
        'id': 'finca_es_madrid',
        'title': 'Finca Urbana Madrid',
        'surface_m2': 3000,
        'buildable_m2': 2700,
        'is_urban': 1,
        'price': 120000,
        'lat': 40.4168,
        'lon': -3.7038,
        'status': 'published'
    },
    {
        'id': 'finca_pt_lisboa',
        'title': 'Finca Urbana Lisboa',
        'surface_m2': 1500,
        'buildable_m2': 1350,
        'is_urban': 1,
        'price': 210000,
        'lat': 38.7223,
        'lon': -9.1393,
        'status': 'published'
    },
]

PROJECT = {
    'id': 'proyecto_casa_modular',
    'title': 'Casa Modular Mediterránea',
    'description': 'Vivienda unifamiliar modular optimizada para parcelas urbanas.',
    'area_m2': 250,
    'price': 220000,
    'files_json': None
}

EXTENDED_FIELDS = []


def seed():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f'Database not found at {DB_PATH}')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Purge relevant tables (avoid foreign key remnants)
    for table in ['proposals','reservations','projects','plots']:
        try:
            c.execute(f'DELETE FROM {table}')
        except Exception:
            pass

    # Insert plots
    for p in PLOTS:
        c.execute('''INSERT INTO plots (id,title,surface_m2,buildable_m2,is_urban,price,lat,lon,status,created_at)
                     VALUES (?,?,?,?,?,?,?,?,?,?)''',
                  (p['id'],p['title'],p['surface_m2'],p['buildable_m2'],p['is_urban'],p['price'],p['lat'],p['lon'],p['status'],NOW))

    # Insert base project columns
    c.execute('''INSERT INTO projects (id,title,description,area_m2,price,files_json,created_at)
                 VALUES (?,?,?,?,?,?,?)''',
              (PROJECT['id'],PROJECT['title'],PROJECT['description'],PROJECT['area_m2'],PROJECT['price'],PROJECT['files_json'],NOW))

    # Update extended fields
    # No extended fields

    conn.commit()

    # Verification summary
    c.execute('SELECT COUNT(*) FROM plots'); plots_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM projects'); projects_count = c.fetchone()[0]
    c.execute('SELECT id,title,surface_m2,price FROM plots ORDER BY title'); plot_rows = c.fetchall()
    c.execute('SELECT id,title,area_m2,price FROM projects'); proj_row = c.fetchone()
    conn.close()

    print('SEED COMPLETED')
    print('plots:', plots_count)
    print('projects:', projects_count)
    print('plot sample:', plot_rows)
    print('project:', proj_row)

if __name__ == '__main__':
    seed()
