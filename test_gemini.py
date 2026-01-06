# import google.genai as genai  # Ya no se usa, ahora usamos Groq
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Usar variable de entorno para la API key (más seguro)
api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyBlvXO0R1Wr2OWAcZk4VcGDR0paKxQ9-Ys"

client = genai.Client(api_key=api_key)

# Listar modelos disponibles
print("Modelos disponibles:")
models = client.models.list()
for model in models:
    print(f"- {model.name}")

print("\nProbando con gemini-2.5-flash...")

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[{"parts":[{"text":"Hola"}]}]
)

print(resp.candidates[0].content.parts[0].text)