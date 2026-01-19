#!/usr/bin/env python3
"""
Script de validación de configuración de ARCHIRAPID
Verifica que todas las dependencias y configuraciones estén correctas.
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Verifica que el archivo .env existe y contiene la clave API."""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ ERROR: Archivo .env no encontrado")
        print("   Crea un archivo .env en la raíz del proyecto")
        return False

    with open(env_path, 'r') as f:
        content = f.read()

    if 'GROQ_API_KEY=' not in content:
        print("❌ ERROR: GROQ_API_KEY no encontrada en .env")
        return False

    # Verificar que no sea el placeholder
    if 'tu_clave_aqui' in content:
        print("❌ ERROR: GROQ_API_KEY tiene el placeholder, actualízala")
        return False

    print("✅ Archivo .env encontrado con GROQ_API_KEY")
    return True

def check_groq_api():
    """Verifica que la API de Groq funcione."""
    try:
        from modules.marketplace import ai_engine_groq as ai

        if not ai.validate_api_key():
            print("❌ ERROR: Clave API de Groq no válida")
            return False

        # Probar una llamada simple
        result = ai.generate_text("Responde solo con: TEST_OK", model_name='llama-3.3-70b-versatile')
        if "TEST_OK" in result:
            print("✅ API de Groq funcionando correctamente")
            return True
        else:
            print(f"❌ ERROR: Respuesta inesperada de Groq: {result}")
            return False

    except ImportError as e:
        print(f"❌ ERROR: No se puede importar ai_engine_groq: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Error al probar Groq API: {e}")
        return False

def check_dependencies():
    """Verifica que las dependencias principales estén instaladas."""
    required_modules = ['streamlit', 'groq', 'dotenv', 'PyPDF2']

    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"❌ ERROR: Módulos faltantes: {', '.join(missing)}")
        print("   Instala con: pip install " + " ".join(missing))
        return False

    print("✅ Todas las dependencias principales instaladas")
    return True

def main():
    """Función principal de validación."""
    print("🔍 Validando configuración de ARCHIRAPID...\n")

    all_good = True

    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("📁 Directorio de trabajo:", os.getcwd())

    # Verificar .env
    if not check_env_file():
        all_good = False

    # Verificar dependencias
    if not check_dependencies():
        all_good = False

    # Verificar API de Groq
    if not check_groq_api():
        all_good = False

    print("\n" + "="*50)

    if all_good:
        print("🎉 ¡Configuración correcta! ARCHIRAPID está listo.")
        print("\nPuedes ejecutar la aplicación con:")
        print("  streamlit run app.py")
        return 0
    else:
        print("❌ Configuración incompleta. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())