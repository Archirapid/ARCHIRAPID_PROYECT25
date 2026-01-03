import fitz  # PyMuPDF
import google.genai as genai
from PIL import Image
import io
import os
import json
import base64
from dotenv import load_dotenv
import streamlit as st

def extraer_datos_catastral(pdf_path):
    """
    Función simplificada al máximo para extraer datos catastrales
    Configuración de máxima compatibilidad con Gemini API
    """
    try:
        # Cargar variables de entorno desde .env
        load_dotenv()

        # Verificar API KEY - Usar secrets de Streamlit para seguridad
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except KeyError:
            # Fallback a .env para desarrollo local
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return {"error": "No se encontró la clave GOOGLE_API_KEY en secrets de Streamlit ni en .env"}

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

        # Modelo a usar con máxima compatibilidad
        nombre_modelo = 'gemini-2.0-flash'

        # Forzar versión de API compatible
        os.environ["GOOGLE_API_USE_MTLS"] = "never"

        # Prompt corto para extraer datos catastrales
        prompt = """Extrae de esta nota catastral: referencia_catastral, superficie_grafica_m2, municipio.
        Devuelve solo JSON: {"referencia_catastral":"codigo","superficie_grafica_m2":numero,"municipio":"ciudad"}"""

        # Preparar contenidos para la API
        contents = [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": img_b64}}]}]

        # Usar el modelo directamente (sin sistema de fallback para ver errores reales)
        try:
            # Llamada a la IA
            response = client.models.generate_content(model=nombre_modelo, contents=contents)

            # Verificar que tenemos respuesta
            if not response or not response.candidates:
                return {"error": f"Respuesta vacía del modelo {nombre_modelo}"}

            # Limpiar respuesta (quitar backticks si los hay)
            text = response.candidates[0].content.parts[0].text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            # Verificar que no esté vacía
            if not text:
                return {"error": f"Respuesta vacía del modelo {nombre_modelo}"}

            # Convertir a diccionario Python
            try:
                resultado = json.loads(text)

                # Verificar que tenemos los campos esperados
                campos_requeridos = ['referencia_catastral', 'superficie_grafica_m2', 'municipio']
                if not all(campo in resultado for campo in campos_requeridos):
                    return {"error": f"Respuesta incompleta del modelo {nombre_modelo}: faltan campos requeridos"}

                # Éxito - devolver resultado
                return resultado

            except json.JSONDecodeError as json_error:
                return {"error": f"JSON inválido del modelo {nombre_modelo}: {str(json_error)}"}

        except Exception as model_error:
            return {"error": f"Error con modelo {nombre_modelo}: {str(model_error)}"}

    except Exception as e:
        error_msg = str(e).lower()

        # Manejo específico de errores comunes
        if 'quota' in error_msg or '429' in error_msg:
            return {"error": "Se ha agotado la cuota de la API de Gemini. Espera unos minutos para que se resetee automáticamente."}

        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return {"error": "La clave API de Gemini no es válida. Verifica tu GEMINI_API_KEY en el archivo .env"}

        elif 'network' in error_msg or 'connection' in error_msg:
            return {"error": "Error de conexión a internet. Verifica tu conexión y vuelve a intentarlo."}

        else:
            # Incluir el error técnico completo como se pidió
            return {"error": f"Error crítico al procesar el PDF. Detalles técnicos: {str(e)}"}

def get_ai_response(prompt: str, model_name: str = 'models/gemini-2.0-flash') -> str:
    """
    Función genérica para obtener respuesta de IA usando Gemini API
    
    Args:
        prompt: El prompt a enviar a la IA
        model_name: Nombre del modelo a usar
        
    Returns:
        str: Respuesta de la IA o mensaje de error
    """
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Verificar API KEY - Usar secrets de Streamlit para seguridad
        try:
            api_key = st.secrets["GOOGLE_API_KEY"]
        except KeyError:
            # Fallback a .env para desarrollo local
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return "Error: No se encontró la clave GOOGLE_API_KEY en secrets de Streamlit ni en .env"
        
        # Configurar API de Gemini
        client = genai.Client(api_key=api_key)
        
        # Preparar contenidos
        contents = [{"parts": [{"text": prompt}]}]
        
        # Crear modelo
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