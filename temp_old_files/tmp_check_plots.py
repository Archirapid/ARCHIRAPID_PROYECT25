import sqlite3

conn = sqlite3.connect("archirapid.db")  # mismo nombre que en src/db.py
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT COUNT(*) AS n FROM plots")
print("Total filas en plots:", c.fetchone()["n"])

c.execute("SELECT id, title, status FROM plots")
for r in c.fetchall():
    print(r["id"], "|", r["title"], "|", r["status"])

conn.close()
