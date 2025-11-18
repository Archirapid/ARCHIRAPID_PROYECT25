import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Corregir todos los proyectos de Raul con architect_id NULL
c.execute("""
    UPDATE projects 
    SET architect_id = 'e0e43fa3-5cc3-4ef9-a88c-bd6ebf094ac1' 
    WHERE architect_name = 'Raul villar' AND architect_id IS NULL
""")
affected = c.rowcount
conn.commit()

print(f"✅ Corregidos {affected} proyectos")

# Verificar resultado
c.execute("SELECT title, architect_id FROM projects WHERE architect_name = 'Raul villar' ORDER BY created_at DESC")
print("\n=== PROYECTOS DE RAUL DESPUÉS DE CORRECCIÓN ===\n")
for row in c.fetchall():
    print(f"• {row[0]}")
    print(f"  architect_id: {row[1]}\n")

conn.close()
