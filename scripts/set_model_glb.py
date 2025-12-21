import sqlite3
from pathlib import Path
DB = Path('C:/ARCHIRAPID_PROYECT25/database.db')
conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM projects WHERE modelo_3d_glb IS NULL OR trim(modelo_3d_glb) = ''")
count = cur.fetchone()[0]
print('TO_UPDATE', count)
if count>0:
    cur.execute("UPDATE projects SET modelo_3d_glb = ? WHERE modelo_3d_glb IS NULL OR trim(modelo_3d_glb) = ''", ('static/modelos/design_model.glb',))
    conn.commit()
    print('UPDATED', cur.rowcount)
else:
    print('NO_CHANGES')
conn.close()
