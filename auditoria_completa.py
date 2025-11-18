import sqlite3
import os

print("\n" + "="*70)
print("🔍 AUDITORÍA COMPLETA DEL SISTEMA")
print("="*70)

# 1. VERIFICAR BASE DE DATOS
print("\n1️⃣ VERIFICACIÓN DE BASE DE DATOS")
print("-" * 70)

db_path = "data.db"
if os.path.exists(db_path):
    print(f"✅ Base de datos encontrada: {db_path}")
    print(f"   Tamaño: {os.path.getsize(db_path):,} bytes")
else:
    print(f"❌ Base de datos NO encontrada: {db_path}")

# 2. CONTAR PROYECTOS
print("\n2️⃣ CONTEO DE PROYECTOS")
print("-" * 70)

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM projects")
total = c.fetchone()[0]
print(f"Total proyectos en DB: {total}")

c.execute("SELECT COUNT(*) FROM projects WHERE architect_name = 'Raul villar'")
raul_total = c.fetchone()[0]
print(f"Proyectos de Raul villar: {raul_total}")

c.execute("SELECT COUNT(*) FROM projects WHERE architect_id = 'e0e43fa3-5cc3-4ef9-a88c-bd6ebf094ac1'")
raul_con_id = c.fetchone()[0]
print(f"Proyectos con architect_id correcto: {raul_con_id}")

c.execute("SELECT COUNT(*) FROM projects WHERE architect_name = 'Raul villar' AND architect_id IS NULL")
raul_sin_id = c.fetchone()[0]
print(f"Proyectos de Raul con architect_id NULL: {raul_sin_id}")

# 3. LISTAR TODOS LOS PROYECTOS DE RAUL
print("\n3️⃣ LISTA DETALLADA DE PROYECTOS DE RAUL")
print("-" * 70)

c.execute("""
    SELECT title, architect_id, created_at 
    FROM projects 
    WHERE architect_name = 'Raul villar' 
    ORDER BY created_at DESC
""")

for i, row in enumerate(c.fetchall(), 1):
    title, arch_id, created = row
    id_status = "✅" if arch_id else "❌"
    print(f"{i}. {id_status} {title}")
    print(f"   architect_id: {arch_id}")
    print(f"   created_at: {created}\n")

# 4. VERIFICAR TABLA ARCHITECTS
print("\n4️⃣ VERIFICACIÓN TABLA ARCHITECTS")
print("-" * 70)

c.execute("SELECT id, name, email FROM architects WHERE name LIKE '%Raul%' OR name LIKE '%villar%'")
architects = c.fetchall()
if architects:
    for arch in architects:
        print(f"ID: {arch[0]}")
        print(f"Nombre: {arch[1]}")
        print(f"Email: {arch[2]}\n")
else:
    print("❌ No se encontró arquitecto Raul en la tabla architects")

# 5. VERIFICAR SCHEMA DE TABLA PROJECTS
print("\n5️⃣ SCHEMA DE TABLA PROJECTS")
print("-" * 70)

c.execute("PRAGMA table_info(projects)")
columns = c.fetchall()
for col in columns:
    col_id, name, type_, notnull, default, pk = col
    nullable = "NOT NULL" if notnull else "NULLABLE"
    print(f"{name:30} {type_:15} {nullable}")

# 6. BUSCAR PROBLEMAS COMUNES
print("\n6️⃣ DETECCIÓN DE PROBLEMAS")
print("-" * 70)

# Proyectos duplicados por título
c.execute("""
    SELECT title, COUNT(*) as count 
    FROM projects 
    GROUP BY title 
    HAVING count > 1
""")
duplicates = c.fetchall()
if duplicates:
    print("⚠️ PROYECTOS DUPLICADOS:")
    for dup in duplicates:
        print(f"   '{dup[0]}' aparece {dup[1]} veces")
else:
    print("✅ No hay títulos duplicados")

# Proyectos sin architect_id
c.execute("SELECT COUNT(*) FROM projects WHERE architect_id IS NULL")
sin_arch = c.fetchone()[0]
if sin_arch > 0:
    print(f"\n⚠️ HAY {sin_arch} PROYECTOS SIN architect_id")
else:
    print("\n✅ Todos los proyectos tienen architect_id")

conn.close()

print("\n" + "="*70)
print("FIN DE AUDITORÍA")
print("="*70 + "\n")
