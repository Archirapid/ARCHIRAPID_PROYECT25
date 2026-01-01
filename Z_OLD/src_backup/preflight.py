"""Preflight health checks for ArchiRapid application.
Run these before launching main app or in tests to ensure environment consistency.
"""
from pathlib import Path
import os, sqlite3
from typing import Dict
from src.db import ensure_tables, counts
from datetime import datetime, timedelta
import re

REQUIRED_DIRS = [
    Path('uploads'),
    Path('logs'),
    Path('assets/branding'),
]

REQUIRED_FILES = [
    Path('requirements.txt'),
]

OPTIONAL_FILES = [
    Path('assets/branding/logo.png'),
]

def check_directories() -> Dict[str, bool]:
    return {str(p): p.exists() for p in REQUIRED_DIRS}

def check_files() -> Dict[str, bool]:
    out = {str(p): p.exists() for p in REQUIRED_FILES}
    for p in OPTIONAL_FILES:
        out[str(p)] = p.exists()
    return out

def check_db() -> Dict:
    ensure_tables()
    # Try simple query
    try:
        c = counts()
        return {"ok": True, "counts": c}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def check_write_permissions() -> Dict[str, bool]:
    results = {}
    for p in REQUIRED_DIRS:
        try:
            p.mkdir(exist_ok=True)
            test_file = p / '.write_test'
            test_file.write_text('ok', encoding='utf-8')
            test_file.unlink()
            results[str(p)] = True
        except Exception:
            results[str(p)] = False
    return results

def run_all() -> Dict:
    report = {
        'dirs': check_directories(),
        'files': check_files(),
        'db': check_db(),
        'write_perms': check_write_permissions(),
    }
    # Log retention purge (>30 días) para archivos app.log.YYYYMMDD_HHMMSS
    logs_dir = Path('logs')
    now = datetime.utcnow()
    pattern = re.compile(r'app\.log\.(\d{8}_\d{6})$')
    purged = []
    for f in logs_dir.glob('app.log.*'):
        m = pattern.match(f.name)
        if not m:
            continue
        try:
            dt = datetime.strptime(m.group(1), '%Y%m%d_%H%M%S')
            if (now - dt) > timedelta(days=30):
                f.unlink()
                purged.append(f.name)
        except Exception:
            continue
    report['log_retention'] = {'purged': purged}
    return report

if __name__ == '__main__':
    import json
    print(json.dumps(run_all(), indent=2, ensure_ascii=False))
