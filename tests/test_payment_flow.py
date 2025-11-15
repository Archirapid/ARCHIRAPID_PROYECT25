"""Tests for payment_flow helper functions."""
from pathlib import Path
import uuid, sqlite3
from src.payment_flow import finalize_payment, determine_payment_type
from src.db import ensure_tables

DB = Path('data.db')

def _setup_plot(plot_id: str, price: float):
    ensure_tables()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO plots (id,title,description,lat,lon,m2,height,price,type,province,locality,owner_name,owner_email,image_path,registry_note_path,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (plot_id,'Test Plot','Desc',0,0,100,10,price,'urbano','Madrid','', 'Owner','owner@test.com','','','2025-11-15'))
    conn.commit(); conn.close()

def test_determine_payment_type():
    assert determine_payment_type(1000, 100) == 'reservation'
    assert determine_payment_type(1000, 999.99) == 'purchase'

def test_finalize_payment_reservation():
    pid = 'plot_res'
    price = 2000.0
    _setup_plot(pid, price)
    payment_data = {
        'payment_id': uuid.uuid4().hex,
        'buyer_name': 'Alice',
        'buyer_email': 'alice@example.com',
        'amount': price * 0.10,
    }
    result = finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    assert result['payment_type'] == 'reservation'
    # verify reservation exists
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT kind FROM reservations WHERE id=?", (result['reservation_id'],))
    row = c.fetchone(); conn.close()
    assert row and row[0] == 'reservation'

def test_finalize_payment_purchase():
    pid = 'plot_buy'
    price = 3000.0
    _setup_plot(pid, price)
    payment_data = {
        'payment_id': uuid.uuid4().hex,
        'buyer_name': 'Bob',
        'buyer_email': 'bob@example.com',
        'amount': price,  # full purchase
    }
    result = finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    assert result['payment_type'] == 'purchase'
    # verify client created
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id FROM clients WHERE email=?", (payment_data['buyer_email'],))
    row = c.fetchone(); conn.close()
    assert row is not None

def test_finalize_payment_idempotent():
    """Calling finalize_payment twice with same payment_id should not raise and reuse reservation."""
    pid = 'plot_dupe'
    price = 1500.0
    _setup_plot(pid, price)
    payment_id = uuid.uuid4().hex
    payment_data = {
        'payment_id': payment_id,
        'buyer_name': 'Carol',
        'buyer_email': 'carol@example.com',
        'amount': price * 0.10,
    }
    first = finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    second = finalize_payment({'id': pid, 'price': price}, payment_data, DB)
    assert first['reservation_id'] == second['reservation_id']
    assert first['payment_type'] == 'reservation'
    assert second['payment_type'] == 'reservation'
    # Ensure only one row exists
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reservations WHERE id=?", (payment_id,))
    count = c.fetchone()[0]; conn.close()
    assert count == 1
