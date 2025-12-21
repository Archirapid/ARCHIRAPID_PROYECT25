import sqlite3
import os
import json
from pathlib import Path

DB = r"C:/ARCHIRAPID_PROYECT25/database.db"
ROOT = Path(r"C:/ARCHIRAPID_PROYECT25")

out = {}
if not Path(DB).exists():
    print(json.dumps({"error": "database not found", "path": DB}))
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()
try:
    cur.execute("SELECT rowid,* FROM projects ORDER BY rowid DESC LIMIT 1")
    row = cur.fetchone()
    if not row:
        print(json.dumps({"error": "no projects found"}))
        raise SystemExit(0)
    cols = [d[0] for d in cur.description]
    data = dict(zip(cols, row))

    # Candidate keys to check
    candidate_keys = []
    for k in data.keys():
        lk = k.lower()
        if any(x in lk for x in ('foto','imagen','image','modelo','3d','model','memoria','pdf','document','path','file','files','registry','note')):
            candidate_keys.append(k)

    results = {}
    for k in candidate_keys:
        v = data.get(k)
        if isinstance(v, bytes):
            try:
                v = v.decode('utf-8')
            except Exception:
                v = str(v)
        entry = {"raw_value": v}
        checked_path = None
        exists = False
        if v and isinstance(v, str) and v.strip() != '':
            p = Path(v)
            if not p.is_absolute():
                checked_path = str((ROOT / v).resolve())
            else:
                checked_path = str(p)
            exists = os.path.exists(checked_path)
        entry["path_checked"] = checked_path
        entry["exists"] = exists
        results[k] = entry

    summary = {
        "rowid": data.get('rowid'),
        "id": data.get('id'),
        "title": data.get('title') or data.get('titulo'),
        "checked_files": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
finally:
    conn.close()
