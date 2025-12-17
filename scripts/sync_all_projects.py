import sqlite3
import json
from pathlib import Path

DB = Path(r"C:/ARCHIRAPID_PROYECT25/database.db")
conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# Ensure optional columns exist
for stmt in [
    "ALTER TABLE projects ADD COLUMN modelo_3d_path TEXT",
    "ALTER TABLE projects ADD COLUMN piscina INTEGER DEFAULT 0",
]:
    try:
        cur.execute(stmt)
        conn.commit()
    except Exception:
        pass

cur.execute("SELECT id, characteristics_json FROM projects")
rows = cur.fetchall()
if not rows:
    print('NO ROWS')
    conn.close()
    exit(0)

updated = 0
for row in rows:
    pid, ch_raw = row
    if not ch_raw:
        continue
    try:
        ch = json.loads(ch_raw)
    except Exception:
        continue
    habitaciones = ch.get('habitaciones')
    banos = ch.get('baños') if 'baños' in ch else ch.get('banos')
    plantas = ch.get('plantas')
    m2 = ch.get('m2_construidos')
    piscina = 1 if ch.get('piscina') else 0
    garaje = 1 if ch.get('garaje') else 0
    imagenes = ch.get('imagenes')
    modelo_3d = ch.get('modelo_3d_path')

    updates = {}
    if habitaciones is not None:
        try:
            updates['habitaciones'] = int(habitaciones)
        except Exception:
            pass
    if banos is not None:
        try:
            updates['banos'] = int(banos)
        except Exception:
            pass
    if plantas is not None:
        try:
            updates['plantas'] = int(plantas)
        except Exception:
            pass
    if m2 is not None:
        try:
            updates['m2_construidos'] = float(m2)
        except Exception:
            pass
    updates['garaje'] = int(bool(garaje))
    updates['piscina'] = int(bool(piscina))
    if imagenes:
        updates['foto_principal'] = imagenes
    if modelo_3d:
        updates['modelo_3d_path'] = modelo_3d

    if not updates:
        continue
    set_clause = ','.join([f"{k}=?" for k in updates.keys()])
    values = tuple(updates.values()) + (pid,)
    sql = f"UPDATE projects SET {set_clause} WHERE id=?"
    try:
        cur.execute(sql, values)
        conn.commit()
        updated += 1
    except Exception:
        continue

print(f'Updated {updated} projects')
conn.close()
