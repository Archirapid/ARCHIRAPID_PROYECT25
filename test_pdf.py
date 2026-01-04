import sys
import fitz
import google.genai as genai
import base64
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

if len(sys.argv) < 2:
    print("Uso: python test_pdf.py archivo.pdf")
    sys.exit(1)

pdf_path = sys.argv[1]
print("Probando con PDF:", pdf_path)

# Abrir PDF
doc = fitz.open(pdf_path)
page = doc.load_page(0)
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
img_bytes = pix.tobytes()
img_b64 = base64.b64encode(img_bytes).decode()

prompt = """Extrae de esta nota catastral: referencia_catastral, superficie_grafica_m2, municipio.
Devuelve solo JSON: {"referencia_catastral":"codigo","superficie_grafica_m2":numero,"municipio":"ciudad"}"""

contents = [{
    "parts": [
        {"text": prompt},
        {"inline_data": {"mime_type": "image/png", "data": img_b64}}
    ]
}]

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents
)

text = resp.candidates[0].content.parts[0].text.strip()

print("Respuesta cruda de la IA:")
print(repr(text))  # Mostrar con repr para ver caracteres especiales

# Limpiar respuesta como en ai_engine.py
if text.startswith('```json'):
    text = text[7:]
if text.startswith('```'):
    text = text[3:]
if text.endswith('```'):
    text = text[:-3]
text = text.strip()

print("Respuesta limpia:")
print(repr(text))

try:
    data = json.loads(text)
    print("JSON parseado:")
    print(data)
except Exception as e:
    print("ERROR al parsear JSON:", e)