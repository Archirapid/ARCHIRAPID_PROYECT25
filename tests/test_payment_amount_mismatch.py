"""Test amount mismatch logging when same payment_id used with different amount."""
from pathlib import Path
import uuid, sqlite3
from src.payment_flow import finalize_payment
from src.db import ensure_tables
from src.logger import get_recent_events

DB = Path('data.db')

def _setup_plot(plot_id: str, price: float):
    ensure_tables()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO plots (id,title,description,lat,lon,m2,height,price,type,province,locality,owner_name,owner_email,image_path,registry_note_path,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (plot_id,'Plot','Desc',0,0,100,10,price,'urbano','Madrid','', 'Owner','owner@test.com','','','2025-11-15'))
    conn.commit(); conn.close()

def test_amount_mismatch_event():
    pid = 'plot_mismatch'
    price = 4000.0
    _setup_plot(pid, price)
    payment_id = uuid.uuid4().hex
    # First reservation with correct 10%
    data1 = {
        'payment_id': payment_id,
        'buyer_name': 'MismatchUser',
        'buyer_email': 'mm@example.com',
        'amount': round(price * 0.10,2),
    }
    finalize_payment({'id': pid, 'price': price}, data1, DB)
    # Second call with different amount (simulate incorrect replay)
    data2 = dict(data1)
    data2['amount'] = data1['amount'] + 5.0  # change amount
    finalize_payment({'id': pid, 'price': price}, data2, DB)
    events = get_recent_events(300)
    names = [e.get('event') for e in events]
    assert 'reservation_amount_mismatch' in names
    # Ensure original amount not overwritten
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute('SELECT amount FROM reservations WHERE id=?', (payment_id,))
    row = c.fetchone(); conn.close()
    assert row is not None
    assert float(row[0]) == data1['amount']
