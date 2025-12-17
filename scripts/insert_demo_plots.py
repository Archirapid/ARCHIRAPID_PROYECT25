import sqlite3, json

conn = sqlite3.connect("archirapid.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

plots_ejemplo = [
    ("finca_es_malaga", "Finca Urbana Málaga", "REF-MA-001", 900, 300, 185000.0, 36.7213, -4.4217, "draft", json.dumps([]), None),
    ("finca_es_madrid", "Finca Urbana Madrid", "REF-MD-001", 750, 250, 220000.0, 40.4168, -3.7038, "draft", json.dumps([]), None),
    ("finca_pt_lisboa", "Finca Urbana Lisboa", "REF-LI-001", 1500, 500, 210000.0, 38.7223, -9.1393, "draft", json.dumps([]), None),
]

c.executemany("""
INSERT INTO plots
(id, title, cadastral_ref, surface_m2, buildable_m2, price, lat, lon, status, photo_paths, registry_note_path)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", plots_ejemplo)

conn.commit()

c.execute("SELECT COUNT(*) AS n FROM plots")
row = c.fetchone()
try:
    total = row["n"]
except Exception:
    total = row[0]
print("Total filas en plots tras insertar:", total)

c.execute("SELECT id, title, status FROM plots")
for r in c.fetchall():
    try:
        print(r["id"], "|", r["title"], "|", r["status"])
    except Exception:
        print(r[0], "|", r[1], "|", r[2])

conn.close()
