"""Basic health diagnostics for ArchiRapid workspace.
Run: python health.py
Outputs a JSON-ish dict with key metrics.
"""
from __future__ import annotations
import os, json, sqlite3, platform, psutil
from pathlib import Path
from datetime import datetime
from src.logger import get_recent_events

DB_FILE = Path('data.db')
LOG_LIMIT = 300


def collect_health():
    proc = psutil.Process(os.getpid())
    mem = proc.memory_info().rss
    disk = psutil.disk_usage(str(Path('.').resolve()))
    events = get_recent_events(LOG_LIMIT)
    errors = [e for e in events if e.get('level') == 'ERROR']
    mismatches = [e for e in events if e.get('event') == 'reservation_amount_mismatch']
    db_size = DB_FILE.stat().st_size if DB_FILE.exists() else 0
    latest_mismatch = mismatches[-1] if mismatches else None
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'process_memory_bytes': mem,
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
        },
        'db': {
            'path': str(DB_FILE),
            'exists': DB_FILE.exists(),
            'size_bytes': db_size,
            'tables': get_table_count(DB_FILE) if DB_FILE.exists() else None,
        },
        'log': {
            'scanned_events': len(events),
            'error_events': len(errors),
            'mismatch_events': len(mismatches),
            'latest_mismatch': latest_mismatch,
        }
    }

def get_table_count(db_path: Path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        n = cur.fetchone()[0]
        conn.close()
        return n
    except Exception:
        return None


def main():
    data = collect_health()
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
