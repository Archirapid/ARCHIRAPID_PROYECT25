"""
Genera un diseño de vivienda usando Gemini, a partir de una finca FincaMVP y su solar_virtual.
"""
from src.models.finca import FincaMVP
import json
import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="


def generar_diseno_ia(finca: FincaMVP):
    """
    Genera un JSON de diseño de vivienda usando Gemini, a partir de los datos de la finca y solar_virtual.
    """
    prompt = f"""
Eres un arquitecto experto. Genera un JSON de propuesta de vivienda para esta parcela:

Datos de la finca:
{json.dumps(finca.a_dict(), ensure_ascii=False, indent=2)}

Plano solar_virtual:
{json.dumps(finca.solar_virtual, ensure_ascii=False)}

Superficie edificable disponible: {finca.superficie_edificable:.2f} m2

Devuelve solo un JSON con la propuesta de distribución de la vivienda, habitaciones, superficies y orientación.
"""
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not found in environment variable GEMINI_API_KEY")
    url = GEMINI_API_URL + api_key
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    resp.raise_for_status()
    result = resp.json()
    # Extraer el JSON generado por Gemini
    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        # Buscar el primer bloque JSON en el texto
        start = text.find('{')
        end = text.rfind('}') + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        raise RuntimeError(f"Error extrayendo JSON de Gemini: {e}\nRespuesta: {result}")
