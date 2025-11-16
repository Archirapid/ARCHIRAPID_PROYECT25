"""Seed demo dataset: 3 urban plots + 1 compatible project.
Idempotent: purges plots/projects/reservations/proposals then inserts curated demo records.
Run: python seed_demo.py
"""
import sqlite3, os, uuid, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')
NOW = datetime.datetime.utcnow().isoformat()

PLOTS = [
    {
        'id': 'finca_es_malaga',
        'title': 'Finca Urbana Málaga',
        'description': 'Parcela urbana costera ideal para vivienda mediterránea.',
        'lat': 36.7213,
        'lon': -4.4217,
        'm2': 900,
        'height': 12.0,
        'price': 185000,
        'type': 'urbana',
        'province': 'Málaga',
        'locality': 'Málaga',
        'owner_name': 'Demo Owner',
        'owner_email': 'owner1@example.com',
        'image_path': None,
        'registry_note_path': None,
        'created_at': NOW,
        'address': 'Av. Mediterráneo 1, Málaga',
        'owner_phone': '+34 600 111 111'
    },
    {
        'id': 'finca_es_madrid',
        'title': 'Finca Urbana Madrid',
        'description': 'Parcela urbana interior para vivienda familiar de dos plantas.',
        'lat': 40.4168,
        'lon': -3.7038,
        'm2': 3000,
        'height': 15.0,
        'price': 120000,
        'type': 'urbana',
        'province': 'Madrid',
        'locality': 'Madrid',
        'owner_name': 'Demo Owner',
        'owner_email': 'owner2@example.com',
        'image_path': None,
        'registry_note_path': None,
        'created_at': NOW,
        'address': 'Calle Central 10, Madrid',
        'owner_phone': '+34 600 222 222'
    },
    {
        'id': 'finca_pt_lisboa',
        'title': 'Finca Urbana Lisboa',
        'description': 'Parcela urbana premium para vivienda modular mediterránea.',
        'lat': 38.7223,
        'lon': -9.1393,
        'm2': 1500,
        'height': 14.0,
        'price': 210000,
        'type': 'urbana',
        'province': 'Lisboa',  # reuse province field for district
        'locality': 'Lisboa',
        'owner_name': 'Demo Owner',
        'owner_email': 'owner3@example.com',
        'image_path': None,
        'registry_note_path': None,
        'created_at': NOW,
        'address': 'Rua Atlântico 5, Lisboa',
        'owner_phone': '+351 910 333 333'
    },
]

PROJECT = {
    'id': 'proyecto_casa_modular',
    'title': 'Casa Modular Mediterránea',
    'architect_name': 'Demo Architect',
    'area_m2': 250,  # base area field
    'max_height': 9.0,
    'style': 'mediterraneo',
    'price': 220000,
    'file_path': None,
    'description': 'Vivienda unifamiliar modular optimizada para parcelas urbanas (250 m² construidos).',
    'created_at': NOW,
    # Extended compatibility fields (will be added via UPDATE after base insert)
    'm2_construidos': 250,
    'm2_parcela_minima': 800,
    'm2_parcela_maxima': 4000,
    'habitaciones': 4,
    'banos': 3,
    'garaje': 1,
    'plantas': 2,
    'certificacion_energetica': 'A',
    'tipo_proyecto': 'vivienda_unifamiliar'
}

EXTENDED_FIELDS = [
    'm2_construidos','m2_parcela_minima','m2_parcela_maxima','habitaciones','banos','garaje','plantas','certificacion_energetica','tipo_proyecto'
]


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
        c.execute('''INSERT INTO plots (id,title,description,lat,lon,m2,height,price,type,province,locality,owner_name,owner_email,image_path,registry_note_path,created_at,address,owner_phone)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                  (p['id'],p['title'],p['description'],p['lat'],p['lon'],p['m2'],p['height'],p['price'],p['type'],p['province'],p['locality'],p['owner_name'],p['owner_email'],p['image_path'],p['registry_note_path'],p['created_at'],p['address'],p['owner_phone']))

    # Insert base project columns
    c.execute('''INSERT INTO projects (id,title,architect_name,area_m2,max_height,style,price,file_path,description,created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?)''',
              (PROJECT['id'],PROJECT['title'],PROJECT['architect_name'],PROJECT['area_m2'],PROJECT['max_height'],PROJECT['style'],PROJECT['price'],PROJECT['file_path'],PROJECT['description'],PROJECT['created_at']))

    # Update extended fields
    set_clause = ', '.join(f"{f}=?" for f in EXTENDED_FIELDS)
    values = [PROJECT[f] for f in EXTENDED_FIELDS]
    values.append(PROJECT['id'])
    c.execute(f'UPDATE projects SET {set_clause} WHERE id=?', values)

    conn.commit()

    # Verification summary
    c.execute('SELECT COUNT(*) FROM plots'); plots_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM projects'); projects_count = c.fetchone()[0]
    c.execute('SELECT id,title,m2,province FROM plots ORDER BY title'); plot_rows = c.fetchall()
    c.execute('SELECT id,title,m2_construidos,m2_parcela_minima,m2_parcela_maxima FROM projects'); proj_row = c.fetchone()
    conn.close()

    print('SEED COMPLETED')
    print('plots:', plots_count)
    print('projects:', projects_count)
    print('plot sample:', plot_rows)
    print('project:', proj_row)

if __name__ == '__main__':
    seed()
