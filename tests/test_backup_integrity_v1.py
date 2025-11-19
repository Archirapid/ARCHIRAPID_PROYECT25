import json
import hashlib
import zipfile
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / 'backups'


def sha256_stream(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def test_manifest_matches_zip_contents():
    manifest_path = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0_MANIFEST.json'
    zip_path = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0.zip'
    assert manifest_path.exists(), 'Manifest missing'
    assert zip_path.exists(), 'Zip missing'

    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert 'files' in data
    manifest_files = data['files']

    # Unzip to temp location and compare files
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)
        tmp_root = Path(tmpdir)

        for rel, info in manifest_files.items():
            f = tmp_root / rel
            assert f.exists(), f'File in manifest missing from zip: {rel}'
            # Compute sha256 and compare
            sha = sha256_stream(f)
            assert sha == info['sha256'], f"Checksum mismatch for {rel}"


def test_zip_contains_database():
    zip_path = BACKUP_DIR / 'FUNCIONA_PERFECTO_V1.0.zip'
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path, 'r') as z:
        namelist = z.namelist()
        assert any('data.db' in n for n in namelist), 'data.db not present in backup'
