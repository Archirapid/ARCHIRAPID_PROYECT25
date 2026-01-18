import os
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

def validate_api_key() -> bool:
    """
    Valida que la clave API de Groq esté disponible y sea válida.
    """
    try:
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            try:
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    api_key = st.secrets["GROQ_API_KEY"]
            except:
                pass

        if not api_key:
            return False

        # Verificar que la clave tenga el formato correcto
        if not api_key.startswith("gsk_"):
            return False

        return True
    except:
        return False

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
        if not api_key:
            # Fallback a st.secrets
            try:
                if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                    api_key = st.secrets["GROQ_API_KEY"]
            except:
                pass

        if not api_key:
            return "❌ **Error de configuración**: No se encontró la clave GROQ_API_KEY.\n\n**Solución**: Crea un archivo `.env` en la raíz del proyecto con:\n```\nGROQ_API_KEY=tu_clave_aqui\n```\n\nObtén tu clave en: https://console.groq.com/"

        if not api_key.startswith("gsk_"):
            return "❌ **Error de clave**: La clave API de Groq debe comenzar con 'gsk_'.\n\nVerifica tu clave en https://console.groq.com/"

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
            return "❌ Error: No se pudo generar una respuesta válida desde Groq."

    except Exception as e:
        error_msg = str(e).lower()

        if 'quota' in error_msg or '429' in error_msg:
            return "⏳ **Cuota agotada**: Se ha excedido el límite de uso de la API de Groq.\n\nEspera unos minutos antes de intentar nuevamente."
        elif 'key' in error_msg or 'invalid' in error_msg or 'unauthorized' in error_msg:
            return "❌ **Clave inválida**: La clave API de Groq no es válida.\n\nVerifícala en https://console.groq.com/"
        elif 'network' in error_msg or 'connection' in error_msg:
            return "🌐 **Error de conexión**: Verifica tu conexión a internet."
        else:
            return f"❌ **Error inesperado**: {str(e)}\n\nSi el problema persiste, contacta al soporte."