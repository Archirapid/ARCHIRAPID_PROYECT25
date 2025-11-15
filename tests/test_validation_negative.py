import io
import pytest
from src.utils_validation import validate_email, validate_nif, file_size_ok, first_error

class DummyUpload:
    def __init__(self, size_bytes: int):
        self._data = b'x' * size_bytes
    def getvalue(self):
        return self._data
    @property
    def name(self):
        return 'dummy.bin'
    def read(self):
        return self._data

@pytest.mark.parametrize("email", ["", "sin-arroba.com", "a@b", "user@domain", "user@domain.c"])
def test_invalid_emails(email):
    assert not validate_email(email)

@pytest.mark.parametrize("nif", ["", "123", "ABCDEFGH", "1234567", "123456789", "1234567Z9"])  # formatos incorrectos
def test_invalid_nif(nif):
    assert not validate_nif(nif)

def test_filesize_too_large():
    big = DummyUpload(size_bytes=11 * 1024 * 1024)  # 11MB
    assert not file_size_ok(big)

def test_first_error_priority_email():
    err = first_error(email="malo", phone="123456", nif="12345678Z")
    assert err == "Email inválido"

def test_first_error_nif():
    # Email válido, NIF inválido
    err = first_error(email="test@example.com", phone="123456", nif="BAD123")
    assert err == "NIF inválido"

def test_first_error_phone_short():
    err = first_error(email="test@example.com", phone="12", nif="12345678Z")
    assert err == "Teléfono demasiado corto"
