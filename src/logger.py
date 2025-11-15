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
        # Mask sensitive fields (emails, nif) unless disabled
        mask_enabled = os.environ.get('LOG_MASK_SENSITIVE', '1') == '1'
        def _mask_email(v: str) -> str:
            if '@' not in v: return v
            local, dom = v.split('@', 1)
            if not local: return v
            return local[0] + '***@' + dom
        def _mask_nif(v: str) -> str:
            if len(v) < 3: return v
            return v[0] + '***' + v[-1]
        masked = {}
        for k, v in data.items():
            if mask_enabled and isinstance(v, str) and k.lower() in {'email','buyer_email','owner_email','nif','buyer_nif'}:
                if 'email' in k.lower():
                    masked[k] = _mask_email(v)
                else:
                    masked[k] = _mask_nif(v)
            else:
                masked[k] = v
        line = {
            'ts': datetime.utcnow().isoformat(),
            'level': level,
            'event': event,
            **masked
        }
        import json
        with FILE.open('a', encoding='utf-8') as f:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')
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
    import json
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            out.append({'raw': ln})
    return out
