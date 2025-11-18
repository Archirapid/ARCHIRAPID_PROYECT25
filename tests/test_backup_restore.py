import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app.py'
BACKUPS = ROOT / 'backups'


def sha256_of_text(path: Path):
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def test_latest_backup_matches_app():
    # Find latest backup file matching pattern
    backups = sorted([p for p in BACKUPS.glob('app.py.backup_*') if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    assert backups, 'No backups found in backups/'
    latest = backups[0]
    # There should be a .sha256 file too
    sha_file = latest.with_suffix('.sha256')
    assert sha_file.exists(), f"Missing sha256 for backup {latest}"
    expected = sha_file.read_text().strip()
    actual = sha256_of_text(APP)
    assert expected == actual, f"app.py differs from backup {latest}. Expected sha {expected}, got {actual}"
    # Also assert file contents are identical
    assert latest.read_text(encoding='utf-8') == APP.read_text(encoding='utf-8')
