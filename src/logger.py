"""Logger simple para ArchiRapid."""
from pathlib import Path
from datetime import datetime

LOG_PATH = Path('logs')
LOG_PATH.mkdir(exist_ok=True)
FILE = LOG_PATH / 'app.log'

def log(event: str, **data):
    try:
        line = {
            'ts': datetime.utcnow().isoformat(),
            'event': event,
            **data
        }
        with FILE.open('a', encoding='utf-8') as f:
            f.write(str(line) + '\n')
    except Exception:
        pass
