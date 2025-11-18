import shutil
import subprocess
import zipfile
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def test_create_funciona_perfecto_backup():
    # Run the Python backup script
    script = ROOT / 'backups' / 'create_backup_FUNCIONA_PERFECTO.py'
    assert script.exists(), "Script create_backup_FUNCIONA_PERFECTO.py no existe"

    subprocess.run(['python', str(script)], check=True, cwd=str(ROOT))

    zip_path = ROOT / 'backups' / 'FUNCIONA_PERFECTO.zip'
    assert zip_path.exists(), "Backup zip no creado"

    # Try to extract in a temp dir and check essential files
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmp)

        # checks
        root = Path(tmp)
        assert (root / 'app.py').exists(), "app.py faltante en el backup"
        assert (root / 'requirements.txt').exists(), "requirements.txt faltante en el backup"
        assert (root / 'src').exists(), "src faltante en el backup"
