from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import datetime

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = ROOT / 'backups'
TS = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
archive_name = BACKUPS / f'archived_deleted_backups_{TS}.zip'

exclude_prefix = 'FUNCIONA_PERFECTO_V1.0'
exclude_archives_prefix = 'archived_deleted_backups_'

all_files = [p for p in BACKUPS.iterdir() if p.is_file()]
files_to_archive = [p for p in all_files if exclude_prefix not in p.name and not p.name.startswith(exclude_archives_prefix) and not p.name.startswith('archived')]

print('Archiving', len(files_to_archive), 'files...')
if files_to_archive:
    with ZipFile(archive_name, 'w', compression=ZIP_DEFLATED) as z:
        for p in files_to_archive:
            z.write(p, arcname=p.name)
    print('Created zip:', archive_name.name)
    archived_dir = BACKUPS / 'archived'
    archived_dir.mkdir(exist_ok=True)
    for p in files_to_archive:
        shutil.move(str(p), str(archived_dir / p.name))
        print('Moved:', p.name)
else:
    print('No files to archive (everything is V1.0 or already archived)')

# Copy V1.0 to V1.1
v1_files = [p for p in BACKUPS.iterdir() if p.name.startswith('FUNCIONA_PERFECTO_V1.0')]
print('V1 files:', [p.name for p in v1_files])
for p in v1_files:
    new_name = p.name.replace('FUNCIONA_PERFECTO_V1.0', 'FUNCIONA_PERFECTO_V1.1')
    dest = BACKUPS / new_name
    shutil.copy(p, dest)
    print('Copied', p.name, '->', new_name)

# DB backup
DB = ROOT / 'data.db'
backup_db = BACKUPS / f'data.db.backup_SAFE_{TS}.sqlite'
shutil.copy(DB, backup_db)
print('DB backup created:', backup_db.name)

# Save projects manifest for safety
try:
    from src.db import get_all_projects
    import json
    projs = get_all_projects()
    manifest_file = BACKUPS / f'current_projects_manifest_{TS}.json'
    with open(manifest_file, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(projs.to_dict(orient='records'), ensure_ascii=False, indent=2))
    print('Saved project manifest:', manifest_file.name)
except Exception as e:
    print('Could not save project manifest:', e)
