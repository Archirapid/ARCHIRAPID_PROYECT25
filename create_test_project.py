import sqlite3
import json

# Conectar a la base de datos
conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()

# Crear tabla proyectos con columna ocr_text si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS proyectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arquitecto_id INTEGER,
    titulo TEXT,
    estilo TEXT,
    m2_construidos REAL,
    presupuesto_ejecucion REAL,
    m2_parcela_minima REAL,
    alturas INTEGER,
    pdf_path TEXT,
    ocr_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Texto OCR de ejemplo (simulando texto extraído de un PDF de planos)
ocr_sample = """
PLANO DE SITUACIÓN
ESCALA 1:500

PROYECTO: CASA UNIFAMILIAR EN ZONA URBANA
REFERENCIA CATASTRAL: 123456789
MUNICIPIO: Madrid
PROVINCIA: Madrid

DESCRIPCIÓN DEL INMUEBLE:
- Superficie construida: 240 m²
- Superficie parcela: 800 m²
- Número de plantas: 2
- Habitaciones: 3
- Baños: 2
- Garaje: Sí
- Jardín: Sí

CARACTERÍSTICAS CONSTRUCTIVAS:
- Estructura: Hormigón armado
- Cubierta: Teja cerámica
- Fachada: Ladrillo caravista
- Carpintería exterior: PVC
- Carpintería interior: Madera

INSTALACIONES:
- Electricidad: 220V monofásica
- Agua: Red municipal
- Gas: Natural
- Calefacción: Gas natural
- Aire acondicionado: Split

NORMATIVA APLICABLE:
- Código Técnico de la Edificación (CTE)
- Normativa municipal de Madrid
- Ley de Ordenación de la Edificación (LOE)

MEMORIA DESCRIPTIVA:
La vivienda se organiza en dos plantas. La planta baja contiene el salón-comedor,
cocina, baño y garaje. La planta primera alberga las tres habitaciones y el baño principal.
El diseño incorpora elementos de eficiencia energética y sostenibilidad.
"""

# Insertar proyecto de prueba
cursor.execute('''
INSERT INTO proyectos (titulo, arquitecto_id, estilo, m2_construidos, presupuesto_ejecucion,
                      m2_parcela_minima, alturas, pdf_path, ocr_text)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'TEST FINAL PLANOS',
    1,
    'Moderno',
    240.0,
    85000.0,
    800.0,
    2,
    'uploads/test_planos.pdf',
    ocr_sample
))

project_id = cursor.lastrowid
conn.commit()
conn.close()

print(f'✅ Proyecto de prueba creado con ID: {project_id}')
print('Título: TEST FINAL PLANOS')
print(f'OCR text length: {len(ocr_sample)} caracteres')
print('Primeros 200 caracteres del OCR:')
print(ocr_sample[:200] + '...')