import sqlite3
import json
from pathlib import Path

DB = Path(r"C:/ARCHIRAPID_PROYECT25/database.db")
conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# Ensure columna modelo_3d_path exists
try:
    cur.execute("ALTER TABLE projects ADD COLUMN modelo_3d_path TEXT")
    conn.commit()
except Exception:
    pass

# Ensure piscina column exists
try:
    cur.execute("ALTER TABLE projects ADD COLUMN piscina INTEGER DEFAULT 0")
    conn.commit()
except Exception:
    pass

cur.execute("SELECT * FROM projects ORDER BY rowid DESC LIMIT 1")
row = cur.fetchone()
if not row:
    print('NO ROWS')
    conn.close()
    exit(0)
cols = [d[0] for d in cur.description]
proj = dict(zip(cols, row))
print('Found project id=', proj.get('id'))
ch_raw = proj.get('characteristics_json')
if not ch_raw:
    print('No characteristics_json')
    conn.close()
    exit(0)
try:
    ch = json.loads(ch_raw)
except Exception as e:
    print('Invalid JSON:', e)
    conn.close()
    exit(1)

# Normalize keys
habitaciones = ch.get('habitaciones')
banos = ch.get('baños') if 'baños' in ch else ch.get('banos')
plantas = ch.get('plantas')
m2 = ch.get('m2_construidos')
piscina = 1 if ch.get('piscina') else 0
garaje = 1 if ch.get('garaje') else 0
imagenes = ch.get('imagenes')
modelo_3d = ch.get('modelo_3d_path')

# Prepare update
updates = {}
if habitaciones is not None:
    updates['habitaciones'] = int(habitaciones)
if banos is not None:
    updates['banos'] = int(banos)
if plantas is not None:
    updates['plantas'] = int(plantas)
if m2 is not None:
    try:
        updates['m2_construidos'] = float(m2)
    except Exception:
        pass
updates['garaje'] = int(bool(garaje))
updates['piscina'] = int(bool(piscina))
# Map image to foto_principal or galeria_fotos
if imagenes:
    updates['foto_principal'] = imagenes
# Modelo 3D
if modelo_3d:
    updates['modelo_3d_path'] = modelo_3d

if not updates:
    print('No updates to apply')
    conn.close()
    exit(0)

set_clause = ','.join([f"{k}=?" for k in updates.keys()])
values = tuple(updates.values()) + (proj.get('id'),)
sql = f"UPDATE projects SET {set_clause} WHERE id=?"
cur.execute(sql, values)
conn.commit()
print('Updated project', proj.get('id'))
# Show updated row
cur.execute("SELECT id,title,habitaciones,banos,plantas,m2_construidos,garaje,piscina,foto_principal,modelo_3d_path,characteristics_json FROM projects WHERE id=?", (proj.get('id'),))
print(cur.fetchone())
conn.close()
