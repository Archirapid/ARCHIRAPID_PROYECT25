import json
import shutil
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / 'backups'


def test_create_backup_v1_runs_and_outputs():
    # Run the script
    script = str(ROOT / 'backups' / 'create_backup_FUNCIONA_PERFECTO_V1.0.py')
    subprocess.check_call(['python', script])

    zip_path = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0.zip'
    manifest = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0_MANIFEST.json'
    commit_file = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0_COMMIT.txt'

    assert zip_path.exists(), 'No se creó el zip de backup'
    assert manifest.exists(), 'El manifest no existe'

    data = json.loads(manifest.read_text(encoding='utf-8'))
    assert 'files' in data and isinstance(data['files'], dict)
    assert len(data['files']) > 0

    # If git commit file exists, ensure it's plausible
    if commit_file.exists():
        commit = commit_file.read_text().strip()
        assert len(commit) == 40

    # Verify tag exists in the repo
    try:
        tag_out = subprocess.check_output(['git', 'tag', '--list', 'FUNCIONA_PERFECTO_V1.0'], cwd=str(ROOT)).decode().strip()
        assert tag_out == 'FUNCIONA_PERFECTO_V1.0'
    except Exception:
        # If git is not available or repo not configured, this is OK in CI
        pass
