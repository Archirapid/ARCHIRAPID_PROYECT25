"""Logger simple para ArchiRapid."""
from pathlib import Path
from datetime import datetime
import os

LOG_PATH = Path('logs')
LOG_PATH.mkdir(exist_ok=True)
FILE = LOG_PATH / 'app.log'

VALID_LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}

def log_exceptions(fn):
    """Decorator para registrar excepciones de funciones críticas.

    Registra nivel ERROR con nombre de función y tipo de excepción, luego re-lanza.
    """
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            log_error('exception', func=fn.__name__, err=str(e), type=e.__class__.__name__)
            raise
    return wrapper

def log(event: str, level: str = "INFO", **data):
    """Escribe una línea de log estructurada.

    Args:
        event: Nombre del evento (ej: 'plot_insert').
        level: Nivel de severidad (DEBUG, INFO, WARN, ERROR).
        **data: Campos adicionales.
    """
    try:
        if level not in VALID_LEVELS:
            level = "INFO"
        # Rotación por tamaño si supera umbral
        max_bytes = int(os.environ.get('LOG_MAX_BYTES', '1048576'))  # 1MB por defecto
        current_size = FILE.stat().st_size if FILE.exists() else 0
        # Rotar ANTES de escribir la nueva línea si ya alcanzó o superó umbral
        if current_size >= max_bytes:
            from datetime import datetime as _dt
            ts = _dt.utcnow().strftime('%Y%m%d_%H%M%S')
            rotated = FILE.parent / f"app.log.{ts}"
            try:
                if FILE.exists():
                    FILE.rename(rotated)
            except Exception:
                pass
        line = {
            'ts': datetime.utcnow().isoformat(),
            'level': level,
            'event': event,
            **data
        }
        with FILE.open('a', encoding='utf-8') as f:
            f.write(str(line) + '\n')
    except Exception:
        pass

def log_error(event: str, **data):
    log(event, level="ERROR", **data)

def log_warn(event: str, **data):
    log(event, level="WARN", **data)

def log_debug(event: str, **data):
    log(event, level="DEBUG", **data)

def get_recent_events(limit: int = 50):
    """Devuelve las últimas líneas del log parseadas a dict si es posible."""
    if not FILE.exists():
        return []
    lines = FILE.read_text(encoding='utf-8').strip().splitlines()[-limit:]
    out = []
    for ln in lines:
        try:
            # eval seguro: formatea con dict() pero usamos json fallback si se cambia formato
            if ln.startswith('{') and ln.endswith('}'):  # naive check
                # Transform single quotes to double quotes for JSON
                j = ln.replace("'", '"')
                import json
                out.append(json.loads(j))
            else:
                out.append({'raw': ln})
        except Exception:
            out.append({'raw': ln})
    return out
