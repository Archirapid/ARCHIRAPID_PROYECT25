"""Test logger masking of sensitive data (emails, NIFs)."""
import os
from pathlib import Path
import pytest
from src.logger import log, FILE

def test_email_masking():
    """Emails should be masked to local[0]***@domain."""
    os.environ['LOG_MASK_SENSITIVE'] = '1'
    log('test_email', email='john.doe@example.com')
    lines = FILE.read_text(encoding='utf-8').strip().splitlines()
    last = lines[-1]
    assert 'j***@example.com' in last
    assert 'john.doe' not in last

def test_nif_masking():
    """NIFs should be masked to first+***+last."""
    os.environ['LOG_MASK_SENSITIVE'] = '1'
    log('test_nif', buyer_nif='12345678A')
    lines = FILE.read_text(encoding='utf-8').strip().splitlines()
    last = lines[-1]
    assert '1***A' in last
    assert '12345678A' not in last

def test_masking_disabled():
    """When LOG_MASK_SENSITIVE=0, data should not be masked."""
    os.environ['LOG_MASK_SENSITIVE'] = '0'
    log('test_unmask', email='alice@test.com', nif='87654321B')
    lines = FILE.read_text(encoding='utf-8').strip().splitlines()
    last = lines[-1]
    assert 'alice@test.com' in last
    assert '87654321B' in last
    # reset
    os.environ['LOG_MASK_SENSITIVE'] = '1'
