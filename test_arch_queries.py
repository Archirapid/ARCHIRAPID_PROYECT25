import sqlite3
import pandas as pd

DB_PATH = 'data.db'

print("Test 1: Query simple a architects")
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM architects", conn)
    conn.close()
    print(f"✅ OK - {df.shape[0]} architects encontrados")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\nTest 2: Query con WHERE a architects")
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM architects WHERE email = ?", conn, params=('test@test.com',))
    conn.close()
    print(f"✅ OK - {df.shape[0]} results")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\nTest 3: Query a subscriptions")
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM subscriptions WHERE architect_id = ? AND status = 'active'", conn, params=('test',))
    conn.close()
    print(f"✅ OK - {df.shape[0]} subscriptions")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\nTest 4: Query a projects con architect_id")
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM projects WHERE architect_id = ?", conn, params=('test',))
    conn.close()
    print(f"✅ OK - {df.shape[0]} projects")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\nTest 5: Verificar columnas de projects")
try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA table_info(projects)")
    cols = [row[1] for row in c.fetchall()]
    conn.close()
    print(f"✅ Columnas projects ({len(cols)}):")
    for col in cols:
        print(f"   - {col}")
except Exception as e:
    print(f"❌ ERROR: {e}")
