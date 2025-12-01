# generate_pdf.py
"""
Generación de Memoria Técnica PDF usando Ollama.
"""

from ollama_client import ask_ollama
from modules.marketplace.prompts import PROMPT_MEMORIA

def generate_memoria_pdf(footprint_m2, surface_m2):
    prompt = PROMPT_MEMORIA.format(footprint_m2=footprint_m2, surface_m2=surface_m2)
    text_ia = ask_ollama(prompt, model="llama3.1")
    # Aquí agregar lógica para generar PDF con el texto
    # Por ejemplo, usar reportlab o similar
    return text_ia