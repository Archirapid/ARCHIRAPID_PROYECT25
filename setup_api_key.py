# setup_api_key.py - Configuración rápida de API key para pruebas
"""
Script para configurar temporalmente la API key de OpenRouter
Ejecuta: python setup_api_key.py
"""

import os
import sys

def setup_api_key():
    print("🔑 Configuración de API Key de OpenRouter para ARCHIRAPID")
    print("=" * 60)

    # Verificar si ya está configurada
    current_key = os.getenv("OPENROUTER_API_KEY")
    if current_key:
        print(f"✅ API Key ya configurada: {current_key[:10]}...")
        response = input("¿Quieres cambiarla? (s/n): ")
        if response.lower() != 's':
            print("Configuración mantenida.")
            return

    # Pedir nueva API key
    print("\n📝 Obtén tu API key gratuita en: https://openrouter.ai/keys")
    api_key = input("Introduce tu API key de OpenRouter: ").strip()

    if not api_key:
        print("❌ API key vacía. Configuración cancelada.")
        return

    # Configurar en el entorno actual
    os.environ["OPENROUTER_API_KEY"] = api_key

    print(f"✅ API Key configurada temporalmente: {api_key[:10]}...")
    print("\n⚠️  IMPORTANTE:")
    print("- Esta configuración es solo para esta sesión")
    print("- Para configuración permanente usa:")
    print("  PowerShell: $env:OPENROUTER_API_KEY = 'tu_api_key'")
    print("  CMD: setx OPENROUTER_API_KEY 'tu_api_key'")
    print("- Reinicia tu IDE/terminal después")

    # Verificar que funciona
    print("\n🔍 Probando conexión con IA...")
    try:
        from modules.marketplace.ai_engine import get_ai_response
        test_response = get_ai_response("Responde solo 'OK' si me lees")
        if "OK" in test_response.upper():
            print("✅ Conexión exitosa con OpenRouter!")
        else:
            print(f"⚠️  Respuesta recibida: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    setup_api_key()