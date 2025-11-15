import pytest
from pathlib import Path

def test_requirements_present():
    req = Path('requirements.txt')
    assert req.exists(), 'requirements.txt missing'
    text = req.read_text(encoding='utf-8')
    assert 'streamlit' in text
    assert 'pdf2image' in text
    assert 'pytest' in text

def test_compute_edificability_cached():
    from archirapid_extract.compute_edificability import build_report
    # Primera llamada
    r1 = build_report()
    # Segunda llamada (usa cache lru)
    r2 = build_report()
    assert r1 is r2  # mismo objeto gracias al cache

