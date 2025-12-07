# modules/marketplace/ai_engine.py
import requests
import os
import json

def ai_process(prompt, model="llama3.1"):
    """
    Motor IA centralizado para ARCHIRAPID.
    Cambiado a OpenRouter para rendimiento en MVP.
    Ollama desactivado: para activar, cambia a ask_ollama(prompt, model).
    """
    return get_ai_response(prompt)

def get_ai_response(prompt: str) -> str:
    """
    Capa de abstracción para respuestas de IA.
    Proveedor por defecto: OpenRouter (modelo: mistral) - Más rápido que Ollama local.
    
    Ollama local: Instalado pero desactivado en este MVP por rendimiento.
    Para activar Ollama: Cambia la llamada en ai_process() a ask_ollama(prompt).
    
    Hugging Face API: Opcional, agregar como alternativa.
    Para cambiar proveedor: Modifica esta función.
    """
    # API Key de OpenRouter (setea OPENROUTER_API_KEY en entorno)
    # Para configurar en Windows: setx OPENROUTER_API_KEY "tu_clave_aqui"
    # Para configurar en PowerShell: $env:OPENROUTER_API_KEY = "tu_clave_aqui"
    # Reinicia la terminal después de configurar
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY no configurada. Setea la variable de entorno."
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error en IA: {str(e)}. Verifica API key o conexión."


def plan_vivienda(superficie_finca: int, habitaciones: int, garage: bool) -> dict:
    """
    Genera un plan de vivienda en JSON usando IA.
    - Calcula automáticamente m2 construibles (33% de la finca).
    - Solicita a la IA un JSON estructurado con habitaciones y m².
    - Devuelve un dict parseado listo para usar en visualización 3D.

    Args:
        superficie_finca: Superficie total de la finca en m²
        habitaciones: Número de habitaciones deseadas
        garage: Si incluye garage

    Returns:
        dict: Plan estructurado con habitaciones, garage y total_m2, o dict con error
    """
    m2_construccion = int(superficie_finca * 0.33)

    prompt = f"""
    Cliente con finca de {superficie_finca} m².
    Construcción permitida: {m2_construccion} m².
    Desea {habitaciones} habitaciones y garage: {"sí" if garage else "no"}.

    Genera un JSON estructurado con:
    - Lista de habitaciones (nombre y m²).
    - Garage si aplica (m²).
    - Total_m2 construido.

    IMPORTANTE: Responde ÚNICAMENTE con JSON válido, sin texto adicional.

    Ejemplo de salida:
    {{
      "habitaciones": [
        {{"nombre": "Dormitorio principal", "m2": 15}},
        {{"nombre": "Dormitorio secundario", "m2": 12}},
        {{"nombre": "Salón", "m2": 25}},
        {{"nombre": "Cocina", "m2": 10}}
      ],
      "garage": {{"m2": 20}},
      "total_m2": 82
    }}
    """

    respuesta = get_ai_response(prompt)

    try:
        plan_json = json.loads(respuesta)
        # Validación básica del JSON
        if "habitaciones" not in plan_json or "total_m2" not in plan_json:
            return {"error": "JSON incompleto - faltan campos requeridos", "raw": respuesta}
        return plan_json
    except json.JSONDecodeError:
        # Si la IA devuelve texto no válido, devolvemos un dict con error
        return {"error": "Respuesta IA no es JSON válido", "raw": respuesta}