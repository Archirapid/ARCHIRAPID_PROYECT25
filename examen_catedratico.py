"""
🎓 EXAMEN CATEDRÁTICO - AUDITORÍA INTEGRAL ARCHIRAPID MVP
Fecha: 2025-11-17
Evaluador: Sistema de Análisis Quirúrgico
Objetivo: Verificar Matrícula de Honor
"""

import sqlite3
import os
import json
from datetime import datetime

print("\n" + "="*80)
print("🎓 EXAMEN CATEDRÁTICO - AUDITORÍA INTEGRAL")
print("="*80)

# ============================================================================
# 1. ANÁLISIS DE ESTRUCTURA DE BASE DE DATOS
# ============================================================================
print("\n📊 SECCIÓN 1: ESTRUCTURA DE BASE DE DATOS")
print("-" * 80)

db_path = "data.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Listar todas las tablas
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print(f"✅ Tablas encontradas: {len(tables)}")
for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"   - {table}: {count} registros")

# ============================================================================
# 2. INTEGRIDAD REFERENCIAL
# ============================================================================
print("\n🔗 SECCIÓN 2: INTEGRIDAD REFERENCIAL")
print("-" * 80)

# Verificar proyectos huérfanos (sin architect_id válido)
c.execute("""
    SELECT COUNT(*) 
    FROM projects 
    WHERE architect_id IS NOT NULL 
    AND architect_id NOT IN (SELECT id FROM architects)
""")
huerfanos = c.fetchone()[0]
if huerfanos > 0:
    print(f"❌ FALLO: {huerfanos} proyectos con architect_id inválido")
else:
    print(f"✅ PASS: Todos los proyectos tienen architect_id válido")

# Verificar proyectos sin architect_id
c.execute("SELECT COUNT(*) FROM projects WHERE architect_id IS NULL")
sin_arch = c.fetchone()[0]
if sin_arch > 0:
    print(f"⚠️  WARNING: {sin_arch} proyectos sin architect_id")
    c.execute("SELECT title FROM projects WHERE architect_id IS NULL")
    for title in c.fetchall():
        print(f"      - {title[0]}")
else:
    print(f"✅ PASS: Todos los proyectos tienen architect_id")

# Verificar proposals sin architect_id
c.execute("SELECT COUNT(*) FROM proposals WHERE architect_id IS NULL")
proposals_sin_arch = c.fetchone()[0]
if proposals_sin_arch > 0:
    print(f"⚠️  WARNING: {proposals_sin_arch} propuestas sin architect_id")
else:
    print(f"✅ PASS: Todas las propuestas tienen architect_id")

# ============================================================================
# 3. DUPLICADOS Y DATOS INCONSISTENTES
# ============================================================================
print("\n🔍 SECCIÓN 3: DUPLICADOS Y CONSISTENCIA")
print("-" * 80)

# Arquitectos duplicados por email
c.execute("""
    SELECT email, COUNT(*) as count 
    FROM architects 
    GROUP BY email 
    HAVING count > 1
""")
dup_emails = c.fetchall()
if dup_emails:
    print(f"❌ FALLO: Emails duplicados en architects:")
    for email, count in dup_emails:
        print(f"      {email} aparece {count} veces")
else:
    print(f"✅ PASS: No hay emails duplicados")

# Arquitectos con mismo nombre
c.execute("""
    SELECT name, COUNT(*) as count 
    FROM architects 
    GROUP BY LOWER(name) 
    HAVING count > 1
""")
dup_names = c.fetchall()
if dup_names:
    print(f"⚠️  WARNING: Nombres similares en architects:")
    for name, count in dup_names:
        c.execute("SELECT id, name, email FROM architects WHERE LOWER(name) = LOWER(?)", (name,))
        print(f"      '{name}' - {count} registros:")
        for arch in c.fetchall():
            print(f"         ID: {arch[0]}, Nombre: {arch[1]}, Email: {arch[2]}")
else:
    print(f"✅ PASS: No hay nombres duplicados")

# ============================================================================
# 4. ANÁLISIS DE PROYECTOS
# ============================================================================
print("\n🏗️  SECCIÓN 4: ANÁLISIS DE PROYECTOS")
print("-" * 80)

c.execute("SELECT COUNT(*) FROM projects")
total_proj = c.fetchone()[0]
print(f"Total proyectos: {total_proj}")

c.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN architect_id IS NOT NULL THEN 1 END) as con_arch,
        COUNT(CASE WHEN architect_id IS NULL THEN 1 END) as sin_arch,
        COUNT(CASE WHEN foto_principal IS NOT NULL THEN 1 END) as con_foto,
        COUNT(CASE WHEN galeria_fotos IS NOT NULL AND galeria_fotos != '[]' THEN 1 END) as con_galeria,
        COUNT(CASE WHEN planos_pdf IS NOT NULL THEN 1 END) as con_planos
    FROM projects
""")
stats = c.fetchone()
print(f"   Con architect_id: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
print(f"   Sin architect_id: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
print(f"   Con foto principal: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
print(f"   Con galería: {stats[4]} ({stats[4]/stats[0]*100:.1f}%)")
print(f"   Con planos PDF: {stats[5]} ({stats[5]/stats[0]*100:.1f}%)")

if stats[2] > 0:
    print(f"\n   ❌ FALLO CRÍTICO: {stats[2]} proyectos sin architect_id")
else:
    print(f"\n   ✅ EXCELENTE: Todos los proyectos tienen architect_id")

# ============================================================================
# 5. ANÁLISIS DE FINCAS (PLOTS)
# ============================================================================
print("\n🏞️  SECCIÓN 5: ANÁLISIS DE FINCAS")
print("-" * 80)

c.execute("SELECT COUNT(*) FROM plots")
total_plots = c.fetchone()[0]
print(f"Total fincas: {total_plots}")

c.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN client_id IS NOT NULL THEN 1 END) as con_cliente,
        COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as con_coords,
        COUNT(CASE WHEN area_m2 > 0 THEN 1 END) as con_area
    FROM plots
""")
plot_stats = c.fetchone()
print(f"   Con client_id: {plot_stats[1]} ({plot_stats[1]/plot_stats[0]*100:.1f}%)")
print(f"   Con coordenadas: {plot_stats[2]} ({plot_stats[2]/plot_stats[0]*100:.1f}%)")
print(f"   Con área válida: {plot_stats[3]} ({plot_stats[3]/plot_stats[0]*100:.1f}%)")

# ============================================================================
# 6. ANÁLISIS DE PROPUESTAS
# ============================================================================
print("\n💼 SECCIÓN 6: ANÁLISIS DE PROPUESTAS")
print("-" * 80)

c.execute("SELECT COUNT(*) FROM proposals")
total_proposals = c.fetchone()[0]
print(f"Total propuestas: {total_proposals}")

if total_proposals > 0:
    c.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN architect_id IS NOT NULL THEN 1 END) as con_arch,
            COUNT(CASE WHEN project_id IS NOT NULL THEN 1 END) as con_proj,
            COUNT(CASE WHEN plot_id IS NOT NULL THEN 1 END) as con_plot
        FROM proposals
    """)
    prop_stats = c.fetchone()
    print(f"   Con architect_id: {prop_stats[1]} ({prop_stats[1]/prop_stats[0]*100:.1f}%)")
    print(f"   Con project_id: {prop_stats[2]} ({prop_stats[2]/prop_stats[0]*100:.1f}%)")
    print(f"   Con plot_id: {prop_stats[3]} ({prop_stats[3]/prop_stats[0]*100:.1f}%)")

# ============================================================================
# 7. PRUEBA FUNCIONAL: CONSULTA DE PROYECTOS POR ARQUITECTO
# ============================================================================
print("\n🧪 SECCIÓN 7: PRUEBA FUNCIONAL")
print("-" * 80)

# Buscar arquitecto Raul villar
c.execute("SELECT id, name, email FROM architects WHERE name = 'Raul villar' AND email = 'raul@raul.com'")
raul = c.fetchone()

if raul:
    raul_id = raul[0]
    print(f"✅ Arquitecto encontrado: {raul[1]} ({raul[2]})")
    print(f"   ID: {raul_id}")
    
    # Consultar proyectos de Raul (simulando get_architect_projects)
    c.execute("""
        SELECT title, architect_id, created_at 
        FROM projects 
        WHERE architect_id = ? 
        ORDER BY created_at DESC
    """, (raul_id,))
    
    raul_projects = c.fetchall()
    print(f"\n   Proyectos visibles en UI: {len(raul_projects)}")
    
    if len(raul_projects) > 0:
        print(f"   ✅ PASS: get_architect_projects() devolverá {len(raul_projects)} proyectos")
        for i, proj in enumerate(raul_projects[:5], 1):  # Mostrar solo primeros 5
            print(f"      {i}. {proj[0]} ({proj[2]})")
    else:
        print(f"   ⚠️  WARNING: No hay proyectos visibles para este arquitecto")
    
    # Contar proyectos de Raul con architect_id NULL
    c.execute("""
        SELECT COUNT(*) 
        FROM projects 
        WHERE architect_name = 'Raul villar' AND architect_id IS NULL
    """)
    raul_null = c.fetchone()[0]
    
    if raul_null > 0:
        print(f"\n   ❌ FALLO: {raul_null} proyectos de Raul NO VISIBLES (architect_id NULL)")
        c.execute("""
            SELECT title, created_at 
            FROM projects 
            WHERE architect_name = 'Raul villar' AND architect_id IS NULL
            ORDER BY created_at DESC
        """)
        for title, created in c.fetchall():
            print(f"      - {title} ({created})")
    
else:
    print(f"❌ FALLO: No se encontró arquitecto 'Raul villar'")

# ============================================================================
# 8. VERIFICACIÓN DE ARCHIVOS
# ============================================================================
print("\n📁 SECCIÓN 8: VERIFICACIÓN DE ARCHIVOS")
print("-" * 80)

# Verificar que existen las carpetas de uploads
required_dirs = ['uploads', 'uploads/project_main', 'uploads/project_gallery', 
                 'uploads/project_plans_pdf', 'uploads/plot_registry']
for dir_path in required_dirs:
    if os.path.exists(dir_path):
        files = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
        print(f"   ✅ {dir_path}: {files} archivos")
    else:
        print(f"   ⚠️  {dir_path}: No existe")

# ============================================================================
# 9. CALIFICACIÓN FINAL
# ============================================================================
print("\n" + "="*80)
print("📋 CALIFICACIÓN FINAL")
print("="*80)

fallos_criticos = 0
warnings = 0

# Criterios de evaluación
if sin_arch > 0:
    fallos_criticos += 1
    print(f"❌ FALLO CRÍTICO: Proyectos sin architect_id")

if huerfanos > 0:
    fallos_criticos += 1
    print(f"❌ FALLO CRÍTICO: Proyectos con architect_id inválido")

if dup_emails:
    warnings += 1
    print(f"⚠️  WARNING: Emails duplicados en architects")

if dup_names:
    warnings += 1
    print(f"⚠️  WARNING: Nombres duplicados/similares en architects")

if raul_null > 0:
    fallos_criticos += 1
    print(f"❌ FALLO CRÍTICO: Proyectos de Raul no visibles")

print(f"\nRESUMEN:")
print(f"   Fallos críticos: {fallos_criticos}")
print(f"   Advertencias: {warnings}")

if fallos_criticos == 0 and warnings == 0:
    print(f"\n🏆 MATRÍCULA DE HONOR ✅")
    print(f"   Sistema perfecto, sin fallos ni advertencias")
elif fallos_criticos == 0:
    print(f"\n✅ APROBADO CON NOTABLE")
    print(f"   Sistema funcional con {warnings} advertencias menores")
else:
    print(f"\n❌ SUSPENSO")
    print(f"   Se requiere corrección de {fallos_criticos} fallos críticos")

conn.close()

print("\n" + "="*80)
print("FIN DEL EXAMEN")
print("="*80 + "\n")
