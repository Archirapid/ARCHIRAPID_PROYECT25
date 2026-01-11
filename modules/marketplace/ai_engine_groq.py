import os
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

def generate_text(prompt: str, model_name: str = 'llama-3.3-70b-versatile') -> str:
    """
    Genera texto usando Groq, compatible con Streamlit y con scripts.
    """
    try:
        # Cargar .env
        load_dotenv()

        api_key = None

        # Primero intentar .env
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            print(f"DEBUG: Clave cargada desde .env, longitud: {len(api_key)}")
        else:
            # Fallback a st.secrets
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    api_key = st.secrets["GROQ_API_KEY"]
                    print(f"DEBUG: Clave cargada desde st.secrets, longitud: {len(api_key)}")
            except:
                pass

        if not api_key:
            return "Error: No se encontró la clave GROQ_API_KEY en .env ni en secrets de Streamlit"

        # Inyectar clave en el entorno para que Groq la detecte
        os.environ["GROQ_API_KEY"] = api_key

        # Inicializar cliente sin parámetros (Groq leerá la clave del entorno)
        client = Groq()

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "Error: No se pudo generar una respuesta válida"

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return "Error: Se ha agotado la cuota de la API de Groq. Espera unos minutos."
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return "Error: La clave API de Groq no es válida."
        elif 'network' in error_msg or 'connection' in error_msg:
            return "Error: Error de conexión a internet."
        else:
            return f"Error al procesar la solicitud: {str(e)}"