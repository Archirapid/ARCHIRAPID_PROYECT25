import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print("Tablas existentes:")
for t in tables:
    print(f"  - {t}")

# Verificar si architects existe
if 'architects' in tables:
    c.execute("SELECT COUNT(*) FROM architects")
    count = c.fetchone()[0]
    print(f"\narchitects: {count} registros")
else:
    print("\n❌ Tabla 'architects' NO existe")

conn.close()
