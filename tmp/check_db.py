import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import db
import json

conn = db.get_conn()
cur = conn.cursor()
try:
    cur.execute("SELECT COUNT(*) as c FROM plots WHERE lat IS NOT NULL AND lon IS NOT NULL")
    r = cur.fetchone()
    print('plots_with_coords:', r['c'] if r else '0')
    cur.execute("SELECT id,title,lat,lon,price FROM plots WHERE lat IS NOT NULL AND lon IS NOT NULL LIMIT 10")
    rows = cur.fetchall()
    out = [dict(row) for row in rows]
    print(json.dumps(out, ensure_ascii=False, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    conn.close()
