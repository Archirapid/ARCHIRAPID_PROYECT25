"""Tests para validación de uploads de archivos."""
import pytest
import io
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import save_file

class MockUploadedFile:
    """Mock de Streamlit UploadedFile para testing."""
    def __init__(self, name, content, mime_type, size):
        self.name = name
        self._content = content
        self.type = mime_type
        self.size = size
    
    def getvalue(self):
        return self._content
    
    def getbuffer(self):
        return self._content

def test_save_file_valid_image():
    """Test guardado de imagen válida."""
    # Crear mock de imagen JPEG pequeña (header JPEG válido)
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'\x00' * 100
    mock_file = MockUploadedFile(
        name='test.jpg',
        content=jpeg_header,
        mime_type='image/jpeg',
        size=len(jpeg_header)
    )
    
    try:
        path = save_file(
            mock_file, 
            prefix='test',
            max_size_mb=1,
            allowed_mime_types=['image/jpeg', 'image/png']
        )
        assert Path(path).exists()
        assert 'test_' in path
        # Cleanup
        if Path(path).exists():
            Path(path).unlink()
    except Exception as e:
        # Si falla por magic no instalado, skip
        if 'magic' in str(e).lower():
            pytest.skip("python-magic not available")
        raise

def test_save_file_exceeds_size_limit():
    """Test rechazo de archivo que excede límite de tamaño."""
    # Crear archivo grande (11MB simulado)
    large_content = b'A' * (11 * 1024 * 1024)
    mock_file = MockUploadedFile(
        name='large.jpg',
        content=large_content,
        mime_type='image/jpeg',
        size=len(large_content)
    )
    
    with pytest.raises(ValueError, match='Archivo demasiado grande'):
        save_file(mock_file, prefix='test', max_size_mb=10)

def test_save_file_without_mime_validation():
    """Test guardado sin validación MIME (modo permisivo)."""
    content = b'test content'
    mock_file = MockUploadedFile(
        name='test.txt',
        content=content,
        mime_type='text/plain',
        size=len(content)
    )
    
    path = save_file(mock_file, prefix='test', max_size_mb=1)
    assert Path(path).exists()
    # Cleanup
    if Path(path).exists():
        Path(path).unlink()

def test_save_file_pdf_valid():
    """Test guardado de PDF válido."""
    # PDF header válido
    pdf_header = b'%PDF-1.4\n' + b'\x00' * 200
    mock_file = MockUploadedFile(
        name='doc.pdf',
        content=pdf_header,
        mime_type='application/pdf',
        size=len(pdf_header)
    )
    
    try:
        path = save_file(
            mock_file,
            prefix='pdf_test',
            max_size_mb=10,
            allowed_mime_types=['application/pdf']
        )
        assert Path(path).exists()
        # Cleanup
        if Path(path).exists():
            Path(path).unlink()
    except Exception as e:
        if 'magic' in str(e).lower():
            pytest.skip("python-magic not available")
        raise
