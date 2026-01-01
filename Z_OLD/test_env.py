#!/usr/bin/env python3
"""
TEST RÁPIDO DE CARGA DE VARIABLES DE ENTORNO
Verifica que la API key se carga correctamente en el contexto de la app
"""

from dotenv import load_dotenv
import os

def test_env_loading():
    print("🔍 TEST DE CARGA DE VARIABLES DE ENTORNO")
    print("=" * 50)

    # Cargar .env (como hace app.py)
    load_dotenv()
    print("✅ .env cargado")

    # Verificar GEMINI_API_KEY
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("✅ GEMINI_API_KEY encontrada")
        print(f"   Longitud: {len(api_key)} caracteres")
        print(f"   Prefijo: {api_key[:20]}...")
    else:
        print("❌ GEMINI_API_KEY NO encontrada")
        return False

    # Verificar que se puede configurar google.generativeai
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print("✅ google.generativeai configurado correctamente")
    except Exception as e:
        print(f"❌ Error configurando google.generativeai: {e}")
        return False

    # Verificar que la función de extracción se puede importar
    try:
        from modules.marketplace.ai_engine import extraer_datos_catastral
        print("✅ Función extraer_datos_catastral importada correctamente")
    except Exception as e:
        print(f"❌ Error importando función: {e}")
        return False

    print("\n🎯 RESULTADO: Variables de entorno cargadas correctamente")
    print("La aplicación Streamlit debería funcionar ahora.")
    return True

if __name__ == "__main__":
    test_env_loading()