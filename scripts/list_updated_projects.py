import sqlite3
DB='C:/ARCHIRAPID_PROYECT25/database.db'
conn=sqlite3.connect(DB)
cur=conn.cursor()
cur.execute("SELECT id,title,modelo_3d_glb FROM projects WHERE modelo_3d_glb = ?", ('static/modelos/design_model.glb',))
rows=cur.fetchall()
for r in rows:
    print(r)
print('TOTAL', len(rows))
conn.close()
