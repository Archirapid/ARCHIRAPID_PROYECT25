"""Tests for logging events in payment_flow idempotency and client creation."""
from pathlib import Path
import uuid, sqlite3, json
from src.payment_flow import finalize_payment
from src.db import ensure_tables
from src.logger import get_recent_events, log_debug

DB = Path('data.db')

def _setup_plot(plot_id: str, price: float):
    ensure_tables()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO plots (id,title,description,lat,lon,m2,height,price,type,province,locality,owner_name,owner_email,image_path,registry_note_path,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (plot_id,'Plot','Desc',0,0,100,10,price,'urbano','Madrid','', 'Owner','owner@test.com','','','2025-11-15'))
    conn.commit(); conn.close()

def _event_names():
    return [e.get('event') for e in get_recent_events(400)]

def test_logging_duplicate_reservation():
    pid = 'plot_log_dupe'
    price = 5000.0
    _setup_plot(pid, price)
    payment_id = uuid.uuid4().hex
    payment_data = {
        'payment_id': payment_id,
        'buyer_name': 'LogUser',
        'buyer_email': 'loguser@example.com',
        'amount': price * 0.10,
    }
    finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    # Force flush with a dummy event to ensure file write
    log_debug('test_flush')
    events = _event_names()
    assert 'reservation_created' in events
    assert 'reservation_duplicate_reuse' in events
    # correlation id is reservation_id; ensure mismatch not logged here
    log_file = Path('logs') / 'app.log'
    content = log_file.read_text(encoding='utf-8') if log_file.exists() else ''
    assert 'correlation_id' in content


def test_logging_client_creation_and_existing():
    pid = 'plot_log_client'
    price = 2500.0
    _setup_plot(pid, price)
    payment_id1 = uuid.uuid4().hex
    data1 = {
        'payment_id': payment_id1,
        'buyer_name': 'ClientA',
        'buyer_email': 'clienta@example.com',
        'amount': price * 0.10,
    }
    finalize_payment({'id': pid, 'price': price}, data1, DB)
    payment_id2 = uuid.uuid4().hex
    data2 = {
        'payment_id': payment_id2,
        'buyer_name': 'ClientA',
        'buyer_email': 'clienta@example.com',
        'amount': price * 0.10,
    }
    finalize_payment({'id': pid, 'price': price}, data2, DB)
    log_debug('test_flush')
    # Read entire log file to avoid window truncation during full suite
    log_file = Path('logs') / 'app.log'
    content = log_file.read_text(encoding='utf-8') if log_file.exists() else ''
    assert 'client_created' in content
    assert 'client_existing' in content
