"""Tests para flujo de compra completa (100% del precio)."""
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
              (plot_id,'Plot','Desc',0,0,100,10,price,'urbano','Madrid','', 'Owner','owner@test.com','','','2025-11-15'))
    conn.commit(); conn.close()

def test_purchase_full_price():
    """Test compra completa (100% del precio)."""
    pid = 'plot_purchase_full'
    price = 5000.0
    _setup_plot(pid, price)
    
    payment_id = uuid.uuid4().hex
    data = {
        'payment_id': payment_id,
        'buyer_name': 'Buyer Full',
        'buyer_email': 'buyer@example.com',
        'amount': price,  # 100%
    }
    
    result = finalize_payment({'id': pid, 'price': price}, data, DB)
    
    assert result['payment_type'] == 'purchase'
    assert result['client_id'] is not None
    assert result['reservation_id'] == payment_id
    
    # Verificar reserva en BD
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT kind, amount FROM reservations WHERE id=?', (payment_id,))
    row = c.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == 'purchase'
    assert float(row[1]) == price

def test_purchase_determines_correctly():
    """Test que determine_payment_type detecta compra correctamente."""
    assert determine_payment_type(10000, 10000) == 'purchase'
    assert determine_payment_type(10000, 9500) == 'purchase'  # 95%
    assert determine_payment_type(10000, 1000) == 'reservation'  # 10%
    assert determine_payment_type(10000, 1001) == 'reservation'  # ~10%

def test_purchase_with_new_client():
    """Test compra creando cliente nuevo."""
    pid = 'plot_purchase_new_client'
    price = 8000.0
    _setup_plot(pid, price)
    
    unique_email = f"newbuyer_{uuid.uuid4().hex[:6]}@example.com"
    payment_id = uuid.uuid4().hex
    data = {
        'payment_id': payment_id,
        'buyer_name': 'New Buyer',
        'buyer_email': unique_email,
        'amount': price,
    }
    
    result = finalize_payment({'id': pid, 'price': price}, data, DB)
    
    assert result['payment_type'] == 'purchase'
    assert result['client_id'] is not None
    
    # Verificar cliente en BD
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT name FROM clients WHERE email=?', (unique_email,))
    row = c.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == 'New Buyer'
