"""Payment flow helper functions for ArchiRapid.

Separates side-effect logic of finalizing a payment (reservation or purchase)
from the Streamlit UI so we can unit test it directly.
"""
from __future__ import annotations
from typing import Dict
from datetime import datetime
import sqlite3, uuid
from pathlib import Path
from src.logger import log_debug, log_warn

def determine_payment_type(plot_price: float, amount: float) -> str:
    """Return 'reservation' if amount is ~10% of plot price, else 'purchase'."""
    reserve_target = round(plot_price * 0.10, 2)
    amt = round(amount, 2)
    # Consider reservation if within 1% tolerance of 10% price
    if abs(amt - reserve_target) / reserve_target <= 0.01:
        return 'reservation'
    # Purchase if amount >= 90% of plot price
    if amt >= plot_price * 0.90:
        return 'purchase'
    # Default to reservation for any other partial amount
    return 'reservation'

def finalize_payment(selected_plot: Dict, payment_data: Dict, db_path: Path) -> Dict[str,str]:
    """Finalize payment: insert reservation and ensure client exists.

    Args:
        selected_plot: dict with at least 'id' and 'price'.
        payment_data: dict with payment fields (payment_id, buyer_name, buyer_email, amount, buyer_phone?, buyer_nif?).
        db_path: Path to SQLite DB file.
    Returns:
        dict with reservation_id, client_id, payment_type.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        price = float(selected_plot.get('price', 0.0))
        ptype = determine_payment_type(price, float(payment_data['amount']))
        rid = payment_data['payment_id']

        # Idempotency / duplicate protection: if reservation id already exists, reuse.
        c.execute('SELECT id, kind, amount FROM reservations WHERE id = ?', (rid,))
        existing = c.fetchone()
        if existing:
            stored_kind = existing[1] if existing[1] else ptype
            existing_amount = existing[2]
            # Detect amount mismatch on duplicate attempts
            if float(existing_amount) != float(payment_data['amount']):
                log_warn('reservation_amount_mismatch', reservation_id=rid, previous_amount=existing_amount, new_amount=payment_data['amount'], correlation_id=rid)
            log_debug('reservation_duplicate_reuse', reservation_id=rid, kind=stored_kind, correlation_id=rid)
        else:
            # Insert new reservation
            c.execute('''INSERT INTO reservations (id, plot_id, buyer_name, buyer_email, amount, kind, created_at)
                         VALUES (?,?,?,?,?,?,?)''', (
                rid,
                selected_plot['id'],
                payment_data['buyer_name'],
                payment_data['buyer_email'],
                payment_data['amount'],
                ptype,
                datetime.utcnow().isoformat()
            ))
            stored_kind = ptype
            log_debug('reservation_created', reservation_id=rid, kind=stored_kind, plot_id=selected_plot['id'], correlation_id=rid)
        # Ensure client exists (lookup by email, create if missing)
        c.execute('SELECT id FROM clients WHERE email = ?', (payment_data['buyer_email'],))
        row = c.fetchone()
        if row:
            client_id = row[0]
            log_debug('client_existing', client_id=client_id, email=payment_data['buyer_email'], correlation_id=rid)
        else:
            client_id = str(uuid.uuid4())
            try:
                c.execute('''INSERT INTO clients (id, name, email, phone, address, preferences, created_at)
                             VALUES (?,?,?,?,?,?,?)''', (
                    client_id,
                    payment_data['buyer_name'],
                    payment_data['buyer_email'],
                    payment_data.get('buyer_phone', ''),
                    '',  # address empty
                    '',  # preferences empty
                    datetime.utcnow().isoformat()
                ))
                log_debug('client_created', client_id=client_id, email=payment_data['buyer_email'], correlation_id=rid)
            except sqlite3.IntegrityError:
                # Race condition: someone created the client concurrently, resolve by selecting again
                c.execute('SELECT id FROM clients WHERE email = ?', (payment_data['buyer_email'],))
                r2 = c.fetchone()
                if r2:
                    client_id = r2[0]
                    log_warn('client_race_resolved', email=payment_data['buyer_email'], client_id=client_id, correlation_id=rid)
                else:
                    raise
        conn.commit()
        return {
            'reservation_id': rid,
            'client_id': client_id,
            'payment_type': stored_kind
        }
    finally:
        conn.close()
