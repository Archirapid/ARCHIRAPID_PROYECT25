# ollama_client.py
"""
IA LOCAL para ARCHIRAPID usando Ollama.
No depende de OpenAI, Azure ni nada de pago.
Llamada universal, lista para todos los prompts.
"""

import subprocess
import json
import tempfile

def ask_ollama(prompt, model="llama3.1"):
    """
    Envía un prompt a Ollama y devuelve texto o JSON limpio.
    model puede ser: llama3.1, mistral, phi3, qwen2.5, deepseek, etc.
    """
    try:
        cmd = ["ollama", "run", model, prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout.strip()

        # Si parece JSON, devolver JSON parseado
        try:
            return json.loads(output)
        except:
            return output

    except Exception as e:
        return {"error": str(e)}