import google.generativeai as genai
import os

# Carga tu nueva clave aquí
os.environ["GEMINI_API_KEY"] = "AIzaSyDHJTZHL9gRUYk-lLXBT7uJP1zC5LWsiqc"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('gemini-2.0-flash')

# Prueba rápida de texto para confirmar que la llave funciona
response = model.generate_content("Hola, ¿estás activa con esta nueva clave?")
print(response.text)