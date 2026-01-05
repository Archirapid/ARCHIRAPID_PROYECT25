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

        # Intentar usar st.secrets SOLO si estamos en Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass

        # Fallback a .env
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return "Error: No se encontró la clave GROQ_API_KEY en secrets de Streamlit ni GROQ_API_KEY en .env"

        # Configurar cliente Groq
        client = Groq(api_key=api_key)

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