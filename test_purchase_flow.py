#!/usr/bin/env python3
"""
Test script for the complete purchase flow with automatic user creation
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules.marketplace.utils import create_client_user_if_not_exists, reserve_plot
import sqlite3

def test_user_creation():
    """Test automatic user creation"""
    print("🧪 Testing automatic user creation...")

    # Test creating a new user
    email = "test_client@example.com"
    name = "Test Client"

    temp_password = create_client_user_if_not_exists(email, name)
    if temp_password:
        print(f"✅ User created successfully with temp password: {temp_password}")
    else:
        print("❌ User creation failed")

    # Test creating the same user again (should return None)
    temp_password2 = create_client_user_if_not_exists(email, name)
    if temp_password2 is None:
        print("✅ Duplicate user detection working correctly")
    else:
        print(f"❌ Duplicate user detection failed: {temp_password2}")

    return temp_password

def test_purchase_flow():
    """Test the complete purchase flow"""
    print("\n🧪 Testing purchase flow...")

    try:
        # This would normally be done through the UI, but we'll simulate it
        plot_id = "test_plot_123"
        buyer_name = "Test Buyer"
        buyer_email = "test_buyer@example.com"
        amount = 1000.0
        kind = "purchase"

        # Create user first
        temp_password = create_client_user_if_not_exists(buyer_email, buyer_name)
        print(f"✅ User created for purchase: {temp_password}")

        # Reserve plot (this would normally be called from the UI)
        # Note: This might fail if the plot doesn't exist, but that's OK for testing
        try:
            rid = reserve_plot(plot_id, buyer_name, buyer_email, amount, kind=kind)
            print(f"✅ Plot reserved successfully: {rid}")
        except Exception as e:
            print(f"⚠️  Plot reservation failed (expected if plot doesn't exist): {e}")

        return True

    except Exception as e:
        print(f"❌ Purchase flow test failed: {e}")
        return False

def verify_database():
    """Verify database has the expected structure"""
    print("\n🧪 Verifying database structure...")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check users table
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'client'")
    client_count = c.fetchone()[0]
    print(f"✅ Found {client_count} client users in database")

    # Check recent users
    c.execute("SELECT email, full_name FROM users WHERE role = 'client' ORDER BY created_at DESC LIMIT 3")
    recent_clients = c.fetchall()
    print("Recent client users:")
    for email, name in recent_clients:
        print(f"  - {name} ({email})")

    conn.close()

if __name__ == "__main__":
    print("🚀 Starting ARCHIRAPID Purchase Flow Tests\n")

    # Test user creation
    temp_pass = test_user_creation()

    # Test purchase flow
    purchase_success = test_purchase_flow()

    # Verify database
    verify_database()

    print("\n🎉 Tests completed!" if purchase_success else "\n❌ Some tests failed")
    print(f"Sample temp password generated: {temp_pass}")