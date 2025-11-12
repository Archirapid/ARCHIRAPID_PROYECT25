import sqlite3
import os

DB_PATH = "data.db"
BASE_PATH = r"d:\ARCHIRAPID_PROYECT25"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Update image paths
c.execute("SELECT id, image_path FROM plots WHERE image_path IS NOT NULL")
rows = c.fetchall()
for row_id, old_path in rows:
    if old_path and BASE_PATH.lower() in old_path.lower():
        new_path = old_path.replace(BASE_PATH + "\\", "").replace(BASE_PATH + "/", "")
        c.execute("UPDATE plots SET image_path = ? WHERE id = ?", (new_path, row_id))
        print(f"✅ {row_id}: {old_path} -> {new_path}")

# Update registry note paths
c.execute("SELECT id, registry_note_path FROM plots WHERE registry_note_path IS NOT NULL")
rows = c.fetchall()
for row_id, old_path in rows:
    if old_path and BASE_PATH.lower() in old_path.lower():
        new_path = old_path.replace(BASE_PATH + "\\", "").replace(BASE_PATH + "/", "")
        c.execute("UPDATE plots SET registry_note_path = ? WHERE id = ?", (new_path, row_id))
        print(f"✅ {row_id}: {old_path} -> {new_path}")

conn.commit()
conn.close()
print("\n✅ Rutas actualizadas a relativas en data.db")
