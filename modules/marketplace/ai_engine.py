# modules/marketplace/ai_engine.py
import requests
import os

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
    # API Key de OpenRouter (setea OPENROUTER_API_KEY en entorno, o usa default)
    api_key = os.getenv("OPENROUTER_API_KEY", "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")
    
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