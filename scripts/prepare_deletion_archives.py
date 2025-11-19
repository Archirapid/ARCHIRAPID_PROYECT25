from pathlib import Path
import json
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = ROOT / 'backups'
TS = __import__('datetime').datetime.utcnow().strftime('%Y%m%d_%H%M%S')

from src.db import get_all_projects, get_conn
projects = get_all_projects()

# find marina id
conn = get_conn()
cur = conn.cursor()
cur.execute("SELECT id FROM architects WHERE email=?", ('marina22@marina22.com',))
row = cur.fetchone()
marina_id = row['id'] if row else None
print('Marina id:', marina_id)

keep_titles = {'MARBELLA PRUEBA', 'LA PRUEBA 2'}
keep_ids = set()
for rec in projects.to_dict(orient='records'):
    if rec.get('architect_id') == marina_id and rec.get('title') in keep_titles:
        keep_ids.add(rec.get('id'))

print('Keep ids:', keep_ids)

# compute to_delete
all_recs = projects.to_dict(orient='records')
all_ids = [r['id'] for r in all_recs]
to_delete = [pid for pid in all_ids if pid not in keep_ids]

print('To delete count:', len(to_delete))

# Dump manifest of to_delete
manifest_file = BACKUPS / f'removed_projects_manifest_{TS}.json'
del_rows = [r for r in all_recs if r['id'] in to_delete]
manifest_file.write_text(json.dumps(del_rows, ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved manifest to:', manifest_file)

# list referenced files
file_fields = ['file_path','modelo_3d_glb','render_vr','planos_pdf','planos_dwg','memoria_pdf','foto_principal','galeria_fotos']
referenced_files = set()
for r in del_rows:
    for f in file_fields:
        val = r.get(f)
        if val:
            referenced_files.add(val)

print('Found referenced file entries:', len(referenced_files))

# Normalize and collect existing files
valid_files = []
for p in referenced_files:
    try:
        path = ROOT / p
    except Exception:
        # skip non-path entries
        continue
    if path.exists():
        valid_files.append(path)

print('Actual files found in FS for deletion:', len(valid_files))
# Save files list
files_manifest = BACKUPS / f'removed_projects_files_list_{TS}.json'
files_manifest.write_text(json.dumps([str(p.relative_to(ROOT)) for p in valid_files], ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved file list to', files_manifest)

# Zip these files
removed_files_zip = BACKUPS / f'removed_projects_files_{TS}.zip'
if valid_files:
    with ZipFile(removed_files_zip, 'w', compression=ZIP_DEFLATED) as z:
        for p in valid_files:
            z.write(p, arcname=str(p.relative_to(ROOT)))
    print('Archived files to', removed_files_zip)
else:
    print('No files to archive')

conn.close()
print('Prepared deletion archives and manifests.')
