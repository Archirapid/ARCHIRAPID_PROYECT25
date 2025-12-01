# modules/marketplace/prompts.py

PROMPT_VALIDATE_PROJECT = """
Eres validador técnico de ARCHIRAPID.
Comprueba que el proyecto entregado contiene:
- Memoria Descriptiva
- Memoria Constructiva
- CTE compliance
- Planos: situación, plantas, alzados, secciones, cimentación, estructura
- Instalaciones: fontanería, electricidad, climatización
- Mediciones y presupuesto (PEM/PEC)
- Pliego de condiciones
- Estudio de seguridad y salud

Devuelve JSON con:
{{"completo": bool, "faltan": [...], "sugerencias": [...]}}
"""

PROMPT_GENERATE_PROJECT_CARD = """
Genera una ficha comercial JSON para marketplace con:
- nombre, superficie_construida, habitaciones, baños, estilo, coste_estimado, descripción(80 palabras), tags
Salida en JSON.
"""

PROMPT_EXTRACT_CATASTRAL = """
Extrae del siguiente texto OCR:
- referencia_catastral
- superficie_m2
- uso (urbano/rustico/industrial)
- servicios (agua,luz,alcantarillado)
- coordenadas si aparecen
Devuelve JSON.
"""

PROMPT_DESIGN_FROM_PARCEL = """
Eres arquitecto virtual. Dada la parcela con superficie {surface_m2} m2 y edificabilidad {buildable_m2} m2,
genera 3 alternativas de anteproyecto: "compacta", "familiar", "patio-centric".
Para cada alternativa devuelve JSON con: superficie_construida, distribución_estancias, nº_plantas, orientación, materiales_sugeridos, coste_estimado.
"""

PROMPT_MEMORIA = """
Redacta una memoria descriptiva y constructiva profesional para una vivienda unifamiliar de {footprint_m2} m2 en parcela {surface_m2} m2.
Incluye sistemas constructivos, cumplimiento CTE, propuestas sostenibles, resumen económico.
Máximo 500 palabras.
"""

PROMPT_3D_INSTRUCTIONS = """
Genera instrucciones geométricas JSON para crear un modelo 3D: muros (coordenadas 3D), aperturas (ventanas/puertas), alturas, materiales.
Salida: JSON estructurado.
"""

PROMPT_RENDER = """
high-end architectural render, ultrarealistic, modern detached house, sustainable materials, natural lighting, landscaped garden, 8k photography style
Negative prompt: cartoon, watermark, text, lowres, deformed, artifacts
"""