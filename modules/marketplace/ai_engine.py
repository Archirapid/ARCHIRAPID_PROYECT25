import google.generativeai as genai
import streamlit as st
import os
import json
import PIL.Image
import io

# Configuración inicial
# Intentamos leer de st.secrets, luego variable de entorno
try:
    API_KEY = st.secrets["general"]["GOOGLE_API_KEY"]
except Exception:
    API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GOOGLE_API_KEY no encontrada.")

def get_gemini_model():
    """Devuelve instancia del modelo configurado."""
    # Using gemini-2.5-flash - latest model with good free tier limits
    return genai.GenerativeModel('models/gemini-2.5-flash')

def generate_text(prompt: str) -> str:
    """Genera respuesta de texto usando Gemini 1.5 Flash."""
    if not API_KEY:
        return "Error: API Key de Google no configurada."
    
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en IA: {str(e)}"

def generate_from_image(prompt: str, image_bytes: bytes) -> str:
    """
    Analiza una imagen (o PDF convertido) usando Gemini Vision.
    """
    if not API_KEY:
         return "Error: API Key no configurada."
    
    try:
        model = get_gemini_model()
        # Convert bytes to PIL Image
        idx = 0
        try:
             img = PIL.Image.open(io.BytesIO(image_bytes))
        except Exception:
             return "Error: Formato de imagen no soportado o corrupto."

        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"Error en Visión IA: {str(e)}"

def generate_from_pdf(prompt: str, pdf_bytes: bytes) -> str:
    """
    Analiza un PDF convirtiéndolo a imágenes y usando Gemini Vision.
    Procesa todas las páginas del PDF y combina la información extraída.
    """
    if not API_KEY:
        return "Error: API Key no configurada."
    
    try:
        from pdf2image import convert_from_bytes
        import tempfile
        
        # Convert PDF to images (all pages)
        images = convert_from_bytes(pdf_bytes, dpi=200)
        
        if not images:
            return "Error: No se pudieron extraer imágenes del PDF."
        
        model = get_gemini_model()
        
        # If multiple pages, analyze all and combine
        if len(images) > 1:
            # Analyze all pages together for better context
            content_parts = [prompt]
            for idx, img in enumerate(images[:5]):  # Limit to first 5 pages to avoid token limits
                content_parts.append(f"Página {idx+1}:")
                content_parts.append(img)
            
            response = model.generate_content(content_parts)
            return response.text
        else:
            # Single page - direct analysis
            response = model.generate_content([prompt, images[0]])
            return response.text
            
    except ImportError:
        return "Error: pdf2image no está instalado. Instala con: pip install pdf2image"
    except Exception as e:
        return f"Error procesando PDF: {str(e)}"

# Alias para compatibilidad con módulos antiguos (gemelo_digital)
get_ai_response = generate_text

def plan_vivienda(superficie_finca: int, habitaciones: int, garage: bool = False) -> dict:
    """Genera distribución en JSON usando Gemini."""
    model = get_gemini_model()
    prompt = f"""
    Actúa como arquitecto experto. Para una finca de {superficie_finca} m² (edificabilidad max 33% = {int(superficie_finca*0.33)} m²),
    diseña una casa con {habitaciones} habitaciones. Garage incluido: {"Sí" if garage else "No"}.
    
    Responde ÚNICAMENTE con un JSON válido (sin markdown ```json) con esta estructura:
    {{
        "habitaciones": [{{"nombre": "Salón", "m2": 25, "dim": "5x5"}}, ...],
        "garage": {{"m2": 20}} (solo si se pidió),
        "total_m2": 100,
        "descripcion": "Breve descripción del concepto arquitectónico."
    }}
    """
    try:
        resp = model.generate_content(prompt)
        text = resp.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def generate_sketch_svg(rooms_data: list, total_m2: int) -> str:
    """
    Pide a Gemini que genere un código SVG simple que represente la distribución en planta.
    """
    model = get_gemini_model()
    rooms_str = json.dumps(rooms_data)
    prompt = f"""
    Genera un código SVG válido de un plano de planta arquitectónico esquemático (floor plan).
    Datos de estancias: {rooms_str}.
    Superficie total: {total_m2} m².
    
    Requisitos:
    - Vista superior 2D.
    - Usa rectángulos simples.
    - Etiqueta cada habitación con texto SVG.
    - Estilo moderno, líneas negras, fondo blanco o gris claro.
    - Tamaño viewBox="0 0 500 500" o similar, ajustado.
    - Responde ÚNICAMENTE con el código <svg>...</svg>, nada más.
    """
    try:
        resp = model.generate_content(prompt)
        svg_code = resp.text
        # Extraer solo el bloque svg si hay texto alrededor
        if "<svg" in svg_code:
            start = svg_code.find("<svg")
            end = svg_code.find("</svg>") + 6
            svg_code = svg_code[start:end]
        return svg_code
    except Exception as e:
        return f"<svg><text>Error generando plano: {e}</text></svg>"