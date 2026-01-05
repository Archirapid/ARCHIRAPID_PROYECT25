import fitz  # PyMuPDF
import google.genai as genai
from groq import Groq
from PIL import Image
import io
import os
import json
import base64
from dotenv import load_dotenv
import streamlit as st
from src.models.finca import FincaMVP

def extraer_datos_catastral(pdf_path):
    """
    Función simplificada al máximo para extraer datos catastrales
    Compatible con Streamlit y con scripts, usando la misma lógica de API key que el resto.
    """
    try:
        # Cargar variables de entorno desde .env
        load_dotenv()
        print("DEBUG API KEY:", os.getenv("GEMINI_API_KEY"))

        api_key = None

        # Intentar usar st.secrets SOLO si estamos en Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass

        # Fallback a .env para desarrollo local
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return {"error": "No se encontró la clave GOOGLE_API_KEY en secrets de Streamlit ni GEMINI_API_KEY en .env"}

        # Configurar API de Gemini
        client = genai.Client(api_key=api_key)

        # Cargar PDF y convertir primera página a imagen
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Primera página
        pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))  # Zoom 3.0 para mejor calidad

        # Verificar que la imagen no esté vacía
        if pix.width == 0 or pix.height == 0:
            doc.close()
            return {"error": "La imagen generada del PDF está vacía o corrupta"}

        img_bytes = pix.tobytes()
        if not img_bytes or len(img_bytes) == 0:
            doc.close()
            return {"error": "No se pudieron generar bytes de imagen del PDF"}

        img = Image.open(io.BytesIO(img_bytes))
        doc.close()

        # Verificar dimensiones de la imagen
        if img.width == 0 or img.height == 0:
            return {"error": "La imagen procesada tiene dimensiones inválidas"}

        # Codificar imagen a base64
        img_b64 = base64.b64encode(img_bytes).decode()

        # Modelo a usar
        nombre_modelo = 'gemini-2.5-flash'

        # Forzar versión de API compatible
        os.environ["GOOGLE_API_USE_MTLS"] = "never"

        # Prompt corto para extraer datos catastrales
        prompt = """Extrae de esta nota catastral: referencia_catastral, superficie_grafica_m2, municipio.
Devuelve solo JSON: {"referencia_catastral":"codigo","superficie_grafica_m2":numero,"municipio":"ciudad"}"""

        # Preparar contenidos para la API
        contents = [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": img_b64
                    }
                }
            ]
        }]

        try:
            # Llamada a la IA
            response = client.models.generate_content(model=nombre_modelo, contents=contents)

            # Verificar que tenemos respuesta
            if not response or not response.candidates:
                return {"error": f"Respuesta vacía del modelo {nombre_modelo}"}

            # Limpiar respuesta
            text = response.candidates[0].content.parts[0].text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            if not text:
                return {"error": f"Respuesta vacía del modelo {nombre_modelo}"}

            # Convertir a diccionario Python
            try:
                resultado = json.loads(text)

                # Verificar que tenemos los campos esperados
                campos_requeridos = ['referencia_catastral', 'superficie_grafica_m2', 'municipio']
                if not all(campo in resultado for campo in campos_requeridos):
                    return {"error": f"Respuesta incompleta del modelo {nombre_modelo}: faltan campos requeridos"}

                return resultado

            except json.JSONDecodeError as json_error:
                return {"error": f"JSON inválido del modelo {nombre_modelo}: {str(json_error)}"}

        except Exception as model_error:
            return {"error": f"Error con modelo {nombre_modelo}: {str(model_error)}"}

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return {"error": "Se ha agotado la cuota de la API de Gemini. Espera unos minutos para que se resetee automáticamente."}
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return {"error": "La clave API de Gemini no es válida. Verifica tu GEMINI_API_KEY en el archivo .env"}
        elif 'network' in error_msg or 'connection' in error_msg:
            return {"error": "Error de conexión a internet. Verifica tu conexión y vuelve a intentarlo."}
        else:
            return {"error": f"Error crítico al procesar el PDF. Detalles técnicos: {str(e)}"}

def extraer_datos_nota_catastral(pdf_path: str) -> dict:
    """
    Extrae datos catastrales de una nota simple usando Gemini AI.
    
    Args:
        pdf_path (str): Ruta al archivo PDF de la nota catastral
        
    Returns:
        dict: Diccionario con los datos extraídos o error
            - referencia_catastral (str or None)
            - superficie_grafica_m2 (int or None) 
            - municipio (str or None)
            - O {"error": "mensaje de error"} si falla
    """
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Obtener API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "No se encontró GEMINI_API_KEY en el archivo .env"}
        
        # Configurar cliente Gemini
        client = genai.Client(api_key=api_key)
        
        # Abrir PDF y convertir primera página a imagen
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom x2
        img_bytes = pix.tobytes()
        img_b64 = base64.b64encode(img_bytes).decode()
        doc.close()
        
        # Prompt para extraer datos catastrales
        prompt = """Extrae de esta nota catastral: referencia_catastral, superficie_grafica_m2, municipio.
Devuelve solo JSON: {"referencia_catastral":"codigo","superficie_grafica_m2":numero,"municipio":"ciudad"}"""
        
        # Preparar contenido para la API
        contents = [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": img_b64}}
            ]
        }]
        
        # Llamada a Gemini
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        
        # Obtener respuesta
        text = resp.candidates[0].content.parts[0].text.strip()
        
        # Limpiar respuesta (remover ```json si existe)
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Parsear JSON
        data = json.loads(text)
        
        # Verificar que tenga los campos esperados (o None)
        return {
            "referencia_catastral": data.get("referencia_catastral"),
            "superficie_grafica_m2": data.get("superficie_grafica_m2"), 
            "municipio": data.get("municipio")
        }
        
    except Exception as e:
        return {"error": f"Error al procesar la nota catastral: {str(e)}"}

def get_ai_response(prompt: str, model_name: str = 'models/gemini-2.5-flash') -> str:
    """
    Función genérica para obtener respuesta de IA usando Gemini API.
    Compatible tanto con Streamlit como con scripts normales.
    """
    try:
        # Cargar variables de entorno (.env)
        load_dotenv()

        api_key = None

        # Intentar usar st.secrets SOLO si estamos en Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except:
            pass

        # Fallback a .env
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return "Error: No se encontró la clave GOOGLE_API_KEY en secrets de Streamlit ni en .env"

        # Configurar cliente Gemini
        client = genai.Client(api_key=api_key)

        # Preparar contenido
        contents = [{"parts": [{"text": prompt}]}]

        # Llamada al modelo
        response = client.models.generate_content(model=model_name, contents=contents)

        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "Error: No se pudo generar una respuesta válida"

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return "Error: Se ha agotado la cuota de la API de Gemini. Espera unos minutos."
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return "Error: La clave API de Gemini no es válida."
        elif 'network' in error_msg or 'connection' in error_msg:
            return "Error: Error de conexión a internet."
        else:
            return f"Error al procesar la solicitud: {str(e)}"

def analisis_finca_ia(datos_finca: dict) -> str:
    """
    Genera un análisis profesional de una finca usando IA.

    Args:
        datos_finca (dict): Diccionario con datos de la finca:
            - referencia_catastral: str
            - superficie_parcela: float
            - municipio: str
            - lat: float
            - lon: float

    Returns:
        str: Análisis generado por IA en formato Markdown
    """
    try:
        # Extraer datos del diccionario
        ref = datos_finca.get('referencia_catastral', 'No especificada')
        m2 = datos_finca.get('superficie_parcela', 0)
        municipio = datos_finca.get('municipio', 'No especificado')
        lat = datos_finca.get('lat', 0)
        lon = datos_finca.get('lon', 0)

        # Construir prompt profesional
        prompt = f"""
Eres un arquitecto experto en análisis de parcelas.

Genera un informe técnico claro, preciso y accionable sobre la siguiente finca:

- Referencia catastral: {ref}
- Superficie: {m2} m²
- Municipio: {municipio}
- Coordenadas: {lat}, {lon}

Incluye:
1. Resumen ejecutivo
2. Análisis urbanístico básico
3. Oportunidades y riesgos
4. Propuesta de uso óptimo
5. Estimación de edificabilidad
6. Recomendaciones arquitectónicas
7. Próximos pasos sugeridos

Formato: Markdown, con títulos y viñetas.
"""

        # Llamar al modelo Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Obtener respuesta
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "Error: No se pudo generar un análisis válido"

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return "Error: Se ha agotado la cuota de la API de Gemini. Espera unos minutos."
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return "Error: La clave API de Gemini no es válida."
        elif 'network' in error_msg or 'connection' in error_msg:
            return "Error: Error de conexión a internet."
        else:
            return f"Error al generar análisis: {str(e)}"

def generar_diseno_ia(finca: FincaMVP) -> dict:
    """
    Genera un diseño de vivienda usando IA basado en la finca proporcionada.
    
    Args:
        finca: Objeto FincaMVP con los datos de la finca
        
    Returns:
        dict: Diseño generado con estructura específica
    """
    # Construir el prompt con los datos de la finca
    finca_data = finca.a_dict()
    solar_virtual = finca.solar_virtual
    superficie_edificable = finca.superficie_edificable
    
    servicios_info = ""
    if finca.servicios.get("alcantarillado") is False:
        servicios_info += " - No hay alcantarillado: sugerir fosa séptica.\n"
    if finca.servicios.get("luz") is False:
        servicios_info += " - No hay luz: sugerir placas solares.\n"
    if finca.servicios.get("agua") is False:
        servicios_info += " - No hay agua: sugerir depósito.\n"
    
    prompt = f"""Basándote en esta finca, genera un diseño de vivienda.

Datos de la finca:
{json.dumps(finca_data, indent=2, ensure_ascii=False)}

Solar virtual: {solar_virtual}
Superficie edificable: {superficie_edificable} m²

Servicios disponibles:
{servicios_info}

Reglas estrictas:
- La suma de m2 de todas las estancias NO puede superar {superficie_edificable} m².
- Si supera, reduce automáticamente los m2.
- Máximo 2 plantas.
- Planta 0: zonas de día (salón, cocina, comedor)
- Planta 1: dormitorios y baños
- Incluye extras basados en servicios faltantes.

Devuelve SOLO un JSON con esta estructura exacta:
{{
  "total_m2": number,
  "plantas": number,
  "estancias": [
    {{
      "nombre": "string",
      "m2": number,
      "planta": number,
      "tipo": "dia|noche|servicio"
    }}
  ],
  "extras": {{
    "garaje": bool,
    "piscina": bool,
    "terraza": bool
  }}
}}

No incluyas comentarios, texto adicional ni campos inventados.
"""
    
    # Llamar a la IA
    response = get_ai_response(prompt)
    
    # Verificar si la respuesta es un error
    if response.startswith("Error:"):
        raise ValueError(f"Error de la IA: {response}")
    
    # Limpiar la respuesta
    if response.startswith('```json'):
        response = response[7:]
    if response.startswith('```'):
        response = response[3:]
    if response.endswith('```'):
        response = response[:-3]
    response = response.strip()
    
    # Parsear JSON
    try:
        resultado = json.loads(response)
        return resultado
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON de la IA: {e}. Respuesta: {response}")

from dotenv import load_dotenv
import os

def generate_text(prompt: str, model_name: str = 'llama-3.3-70b-versatile') -> str:
    """
    Genera texto usando Groq, compatible con Streamlit y con scripts.
    """
    try:
        # Cargar .env
        load_dotenv()

        api_key = None

        # Intentar usar st.secrets SOLO si estamos en Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass

        # Fallback a .env
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return "Error: No se encontró la clave GROQ_API_KEY en secrets de Streamlit ni GROQ_API_KEY en .env"

        # Configurar cliente Groq
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No se pudo generar una respuesta válida"

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return "Error: Se ha agotado la cuota de la API de Groq. Espera unos minutos."
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return "Error: La clave API de Groq no es válida."
        elif 'network' in error_msg or 'connection' in error_msg:
            return "Error: Error de conexión a internet."
        else:
            return f"Error al procesar la solicitud: {str(e)}"