import sqlite3
from pathlib import Path

DB = Path(r"C:/ARCHIRAPID_PROYECT25/database.db")
print(f"Using DB: {DB}")
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
# Check if projects table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
row = cur.fetchone()
if row:
    print('Table projects already exists')
else:
    print('Table projects does not exist — creating')
    cur.execute('''CREATE TABLE projects (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        area_m2 REAL,
        price REAL,
        characteristics_json TEXT,
        architect_name TEXT,
        architect_id TEXT,
        created_at TEXT
    )''')
    conn.commit()
    print('Table projects created')
# Show schema
cur.execute("PRAGMA table_info(projects)")
cols = cur.fetchall()
print('projects schema:')
for c in cols:
    print(c)
conn.close()
