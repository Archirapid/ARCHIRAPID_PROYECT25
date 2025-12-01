# modules/marketplace/ai_engine.py
from ollama_client import ask_ollama

def ai_process(prompt, model="llama3.1"):
    """
    Motor IA centralizado para ARCHIRAPID.
    Aquí puedes cambiar el modelo para toda la plataforma.
    """
    return ask_ollama(prompt, model=model)