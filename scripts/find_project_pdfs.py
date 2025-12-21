import sqlite3
import os
import json
from pathlib import Path

DB = r"C:/ARCHIRAPID_PROYECT25/database.db"
ROOT = Path(r"C:/ARCHIRAPID_PROYECT25")

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

    # Derive project folder from known fields
    candidates = []
    for k in ('foto_principal','modelo_3d_path'):
        v = data.get(k)
        if v and isinstance(v, str):
            candidates.append(v)
    # fallback: search uploads for id
    proj_id = data.get('id') or data.get('titulo') or data.get('rowid')

    found_pdfs = []
    # Try to resolve directory from candidates
    for c in candidates:
        p = Path(c)
        if not p.is_absolute():
            base = (ROOT / p).resolve().parent
        else:
            base = p.parent
        if base.exists():
            for f in base.rglob('*.pdf'):
                found_pdfs.append(str(f))
    # If none found, try searching uploads for any PDF containing project id
    if not found_pdfs and proj_id:
        uploads = ROOT / 'uploads'
        if uploads.exists():
            for f in uploads.rglob('*.pdf'):
                if str(proj_id) in str(f) or 'nota' in f.name.lower() or 'catastral' in f.name.lower():
                    found_pdfs.append(str(f))

    out = {
        'project_id': proj_id,
        'checked_dirs': [str((ROOT / c).resolve().parent) if not Path(c).is_absolute() else str(Path(c).parent) for c in candidates],
        'found_pdfs': sorted(list(set(found_pdfs)))
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
finally:
    conn.close()
