#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO DEL ENTORNO API
Verifica configuración de .env, API keys y conexión con Gemini
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

def diagnostico_completo():
    """
    Realiza un diagnóstico completo del entorno API
    """
    print("🔍 DIAGNÓSTICO COMPLETO DEL ENTORNO API")
    print("=" * 60)

    # 1. Ruta actual del programa
    ruta_actual = os.getcwd()
    print("📁 Ruta actual del programa: {}".format(ruta_actual))

    # 2. Listar archivos en la carpeta actual
    print("\n📋 Archivos en la carpeta actual:")
    try:
        archivos = list(Path(ruta_actual).iterdir())
        archivos_visibles = [f for f in archivos if not f.name.startswith('.')]
        archivos_ocultos = [f for f in archivos if f.name.startswith('.')]

        print("  Archivos visibles ({}):".format(len(archivos_visibles)))
        for archivo in sorted(archivos_visibles)[:10]:  # Mostrar máximo 10
            print("    - {}".format(archivo.name))
        if len(archivos_visibles) > 10:
            print("    ... y {} más".format(len(archivos_visibles) - 10))

        print("  Archivos ocultos ({}):".format(len(archivos_ocultos)))
        for archivo in sorted(archivos_ocultos):
            print("    - {}".format(archivo.name))

        # Verificar específicamente .env
        env_path = Path(ruta_actual) / '.env'
        if env_path.exists():
            print("\n✅ Archivo .env ENCONTRADO")
            # Leer contenido (con cuidado)
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    lineas = contenido.split('\n')
                    print("  Contenido ({} líneas):".format(len(lineas)))
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('#'):
                            if '=' in linea:
                                clave = linea.split('=')[0]
                                print("    - {}: [CONFIGURADO]".format(clave))
                            else:
                                print("    - {}".format(linea))
            except Exception as e:
                print("  ❌ Error leyendo .env: {}".format(e))
        else:
            print("\n❌ Archivo .env NO ENCONTRADO")
    except Exception as e:
        print("❌ Error listando archivos: {}".format(e))

    # 3. Cargar variables de entorno
    print("\n🔑 CARGANDO VARIABLES DE ENTORNO...")
    load_dotenv()
    print("✅ load_dotenv() ejecutado")

    # 4. Verificar GEMINI_API_KEY
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("✅ GEMINI_API_KEY encontrada")
        print("   Longitud: {} caracteres".format(len(api_key)))
        print("   Prefijo: {}****".format(api_key[:4]))
        print("   Sufijo: ****{}".format(api_key[-4:]))
    else:
        print("❌ GEMINI_API_KEY NO encontrada")
        print("   Variables de entorno disponibles:")
        for key, value in os.environ.items():
            if 'GEMINI' in key.upper() or 'API' in key.upper():
                print("   - {}: {}...".format(key, value[:10]))

    # 5. Probar conexión con Gemini
    print("\n🤖 PROBANDO CONEXIÓN CON GEMINI...")
    if not api_key:
        print("❌ No se puede probar conexión - API key no encontrada")
        return False

    try:
        # Configurar API
        genai.configure(api_key=api_key)
        print("✅ API configurada correctamente")

        # Intentar crear modelo
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Modelo gemini-2.0-flash creado correctamente")
        except Exception as model_error:
            print("❌ Error creando modelo gemini-2.0-flash: {}".format(model_error))
            # Intentar con modelo alternativo
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                print("✅ Modelo alternativo gemini-1.5-pro creado correctamente")
            except Exception as alt_error:
                print("❌ Error creando modelo alternativo: {}".format(alt_error))
                return False

        # Listar modelos disponibles para verificar
        print("\n📋 Verificando modelos disponibles...")
        try:
            available_models = genai.list_models()
            vision_models = [m for m in available_models if 'vision' in str(m).lower() or 'gemini' in str(m).lower()]
            print("  Modelos disponibles ({}):".format(len(vision_models)))
            for model_info in vision_models[:5]:  # Mostrar primeros 5
                print("    - {}".format(model_info.name))
            if len(vision_models) > 5:
                print("    ... y {} más".format(len(vision_models) - 5))
        except Exception as list_error:
            print("  ❌ Error listando modelos: {}".format(list_error))

        # Intentar una llamada simple (puede fallar por cuota)
        try:
            response = model.generate_content("Hola, ¿estás funcionando?")
            print("✅ Conexión exitosa con Gemini API")
            print("   Respuesta: {}...".format(response.text[:50]))
            return True

        except Exception as api_error:
            error_str = str(api_error).lower()

            if 'quota' in error_str or '429' in error_str:
                print("⚠️  CUOTA AGOTADA - La API funciona pero has excedido el límite")
                print("   Espera unos minutos para el reset automático")
                return True  # La API funciona, solo es cuota
            elif 'key' in error_str or 'invalid' in error_str:
                print("❌ ERROR DE API KEY - La clave no es válida")
                return False
            else:
                print("❌ ERROR DESCONOCIDO en llamada API: {}".format(api_error))
                return False

    except Exception as setup_error:
        error_str = str(setup_error).lower()
        if 'key' in error_str or 'invalid' in error_str:
            print("❌ ERROR DE CONFIGURACIÓN - API key inválida")
        else:
            print("❌ ERROR DE CONFIGURACIÓN: {}".format(setup_error))
        return False

def diagnostico_rapido():
    """
    Versión simplificada para usar en ai_engine.py
    """
    # Cargar .env
    load_dotenv()

    # Verificar API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Buscando .env en: {}".format(os.getcwd()))
        return {"error": "GEMINI_API_KEY no encontrada en variables de entorno"}

    # Configurar y probar
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        # No hacer llamada real aquí para evitar consumir cuota
        return {"status": "ok", "api_key_loaded": True}
    except Exception as e:
        return {"error": "Error configurando Gemini: {}".format(e)}

if __name__ == "__main__":
    # Ejecutar diagnóstico completo
    success = diagnostico_completo()

    print("\n" + "=" * 60)
    if success:
        print("🎯 RESULTADO: Entorno configurado correctamente")
        print("   La aplicación debería funcionar sin problemas de API key")
    else:
        print("❌ RESULTADO: Hay problemas de configuración")
        print("   Revisa la configuración del .env y la API key")

    print("\n💡 Para usar en ai_engine.py, agrega al principio:")
    print("   from diagnostico_api import diagnostico_rapido")
    print("   result = diagnostico_rapido()")
    print("   if 'error' in result: return result")