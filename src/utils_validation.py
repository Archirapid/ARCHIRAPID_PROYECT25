"""Utilidades de validación para formularios y pagos."""
import re
from typing import Optional
import html

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NIF_REGEX = re.compile(r"^[0-9]{7,8}[A-Za-z]$")

def validate_email(value: str) -> bool:
    if not value: return False
    return bool(EMAIL_REGEX.match(value.strip()))

def validate_nif(value: str) -> bool:
    if not value: return False
    return bool(NIF_REGEX.match(value.strip()))

def file_size_ok(file, max_mb: int = 10) -> bool:
    """Verifica tamaño de archivo subido (Streamlit UploadedFile)."""
    if not file: return True
    return len(file.getvalue()) <= max_mb * 1024 * 1024

def first_error(email: str, phone: str, nif: str) -> Optional[str]:
    if not validate_email(email):
        return "Email inválido"
    if phone and len(phone) < 6:
        return "Teléfono demasiado corto"
    if nif and not validate_nif(nif):
        return "NIF inválido"
    return None

def html_safe(value: str) -> str:
    """Escapa contenido para inserción segura en HTML (previene inyección básica)."""
    if value is None:
        return ''
    return html.escape(str(value), quote=True)
