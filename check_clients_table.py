import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Listar tablas
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]

print("\n📊 TABLAS EN BASE DE DATOS:")
print("="*50)
for table in tables:
    print(f"  ✓ {table}")
    
# Ver si existe tabla clients
if 'clients' in tables:
    c.execute("SELECT COUNT(*) FROM clients")
    count = c.fetchone()[0]
    print(f"\n✅ Tabla 'clients' EXISTE con {count} registros")
    
    if count > 0:
        c.execute("SELECT id, name, email FROM clients LIMIT 3")
        print("\n  Ejemplos:")
        for row in c.fetchall():
            print(f"    - {row[1]} ({row[2]})")
else:
    print(f"\n❌ Tabla 'clients' NO EXISTE")

print(f"\nTotal tablas: {len(tables)}")

conn.close()
