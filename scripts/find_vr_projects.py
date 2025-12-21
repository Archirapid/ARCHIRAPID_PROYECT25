from src import db

conn = db.get_conn()
cur = conn.cursor()
q = "SELECT id,title,modelo_3d_glb,modelo_3d_path FROM projects WHERE modelo_3d_glb IS NOT NULL OR modelo_3d_path LIKE '%.glb' LIMIT 10"
cur.execute(q)
rows = cur.fetchall()
if not rows:
    print('NO_PROJECTS')
else:
    for r in rows:
        d = dict(r)
        print(d)
conn.close()
