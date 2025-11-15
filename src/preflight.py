"""Preflight health checks for ArchiRapid application.
Run these before launching main app or in tests to ensure environment consistency.
"""
from pathlib import Path
import os, sqlite3
from typing import Dict
from src.db import ensure_tables, counts

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
    return {
        'dirs': check_directories(),
        'files': check_files(),
        'db': check_db(),
        'write_perms': check_write_permissions(),
    }

if __name__ == '__main__':
    import json
    print(json.dumps(run_all(), indent=2, ensure_ascii=False))
