import pytesseract
from PIL import Image
import os
from pycatastro import PyCatastro

# Configurar ruta de Tesseract (absoluta, funciona desde D: o cualquier disco)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    """
    Extrae texto de una imagen usando Tesseract OCR.
    Retorna el texto extraído o un mensaje de error.
    """
    if not os.path.exists(image_path):
        return "Error: Archivo de imagen no encontrado."
    
    try:
        # Abrir imagen con PIL
        img = Image.open(image_path)
        # Extraer texto con OCR (idioma español para catastro)
        text = pytesseract.image_to_string(img, lang='spa')
        return text.strip() if text.strip() else "No se detectó texto en la imagen."
    except Exception as e:
        return f"Error en OCR: {str(e)}. Verifica que Tesseract esté instalado."

def analyze_catastro_image(image_path):
    """
    Analiza una imagen catastral y extrae datos clave usando OCR.
    Retorna un diccionario con texto crudo y datos procesados.
    """
    text = extract_text_from_image(image_path)
    
    # Procesamiento básico: buscar patrones comunes en documentos catastrales
    datos_procesados = {}
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        if 'superficie' in line_lower and 'm²' in line_lower:
            # Extraer número (ej: "Superficie: 450 m²")
            import re
            match = re.search(r'(\d+(?:\.\d+)?)\s*m²', line)
            if match:
                datos_procesados['superficie'] = float(match.group(1))
        elif 'propietario' in line_lower or 'titular' in line_lower:
            # Extraer nombre (básico, se puede mejorar)
            datos_procesados['propietario'] = line.split(':')[-1].strip() if ':' in line else line.strip()
        elif 'referencia' in line_lower or 'catastral' in line_lower:
            datos_procesados['referencia_catastral'] = line.split(':')[-1].strip() if ':' in line else line.strip()
    
    return {
        "texto_extraido": text,
        "datos_procesados": datos_procesados
    }

def obtener_datos_finca(provincia, municipio, ref_catastral):
    """
    Obtiene datos oficiales de una finca del Catastro usando APIs de pycatastro.
    Retorna un diccionario con datos catastrales o mensaje de error.
    """
    try:
        # Consulta por referencia catastral (RCCOOR)
        datos = PyCatastro.Consulta_RCCOOR(provincia, municipio, ref_catastral)
        
        # Procesar respuesta (asumiendo estructura de pycatastro)
        if datos and 'error' not in datos:
            return {
                "referencia_catastral": ref_catastral,
                "provincia": provincia,
                "municipio": municipio,
                "superficie": datos.get('superficie', 0),
                "lindes": datos.get('lindes', []),
                "coordenadas": datos.get('coordenadas', {}),
                "propietario": datos.get('propietario', 'No disponible'),
                "fuente": "API Catastro Oficial"
            }
        else:
            return {"error": "No se encontraron datos para la referencia catastral proporcionada."}
    except Exception as e:
        return {"error": f"Error al consultar Catastro: {str(e)}. Verifica conexión a internet y datos."}