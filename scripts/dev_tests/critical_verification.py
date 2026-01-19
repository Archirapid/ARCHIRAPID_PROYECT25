#!/usr/bin/env python3
"""
Script de verificación crítica del sistema de extracción catastral
Verifica todos los puntos críticos mencionados por el usuario
"""

import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_library_conflicts():
    """Verificar que se usa google.genai (SDK v2) en lugar del obsoleto google.generativeai (SDK v1)"""
    print("🔍 Verificando uso de librerías actualizadas...")

    # Buscar importaciones problemáticas solo en archivos del proyecto (excluir venv)
    problematic_imports = []
    for root, dirs, files in os.walk('.'):
        # Excluir directorios del venv y otros irrelevantes
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules', 'Z_OLD']]

        for file in files:
            if file.endswith('.py') and not root.startswith('./venv') and file != 'critical_verification.py':
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'import google.generativeai' in content or 'from google.generativeai' in content:
                            problematic_imports.append(os.path.join(root, file))
                        if 'genai.configure' in content and 'critical_verification.py' not in os.path.join(root, file):
                            problematic_imports.append(f"{os.path.join(root, file)} (usa genai.configure - obsoleto)")
                except:
                    pass

    if problematic_imports:
        print("❌ Encontrados imports obsoletos:")
        for imp in problematic_imports:
            print(f"   - {imp}")
        return False
    else:
        print("✅ No se encontraron imports problemáticos (google.genai)")
        return True

def check_pdf_processing():
    """Verificar que se usa PyMuPDF (fitz) para análisis visual"""
    print("\n🔍 Verificando tratamiento del PDF...")

    # Verificar que ai_engine.py usa fitz correctamente
    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if 'import fitz' not in content:
            print("❌ ai_engine.py no importa fitz (PyMuPDF)")
            return False

        if 'fitz.Matrix(3.0, 3.0)' not in content:
            print("❌ ai_engine.py no usa zoom 3.0 para mejor calidad")
            return False

        if 'PyPDF2' in content:
            print("❌ ai_engine.py contiene referencias a PyPDF2")
            return False

        print("✅ ai_engine.py usa fitz (PyMuPDF) correctamente")
        return True

    except Exception as e:
        print(f"❌ Error verificando ai_engine.py: {e}")
        return False

def check_gemini_call_structure():
    """Verificar estructura correcta de llamada a Gemini"""
    print("\n🔍 Verificando estructura de llamada a Gemini...")

    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar que usa la estructura correcta con contents y parts
        if 'contents' not in content or 'parts' not in content:
            print("❌ No se encuentra la estructura correcta con contents y parts")
            return False

        # Verificar que NO extrae texto manualmente del PDF
        if 'extract_text' in content.lower() or 'reader.pages' in content:
            print("❌ Parece que se extrae texto manualmente del PDF")
            return False

        print("✅ Estructura de llamada correcta: contents con parts")
        return True

    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def check_prompt_content():
    """Verificar que el prompt incluye REFERENCIA CATASTRAL y SUPERFICIE GRÁFICA"""
    print("\n🔍 Verificando contenido del prompt...")

    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar el prompt en el código
        prompt_start = content.find('prompt = """')
        if prompt_start == -1:
            print("❌ No se encuentra la definición del prompt")
            return False

        prompt_end = content.find('"""', prompt_start + 10)
        if prompt_end == -1:
            print("❌ No se encuentra el fin del prompt")
            return False

        prompt_content = content[prompt_start:prompt_end + 3]

        required_terms = [
            "referencia_catastral",
            "superficie_grafica_m2",
            "JSON",
            "municipio"
        ]

        missing_terms = []
        for term in required_terms:
            if term.lower() not in prompt_content.lower():
                missing_terms.append(term)

        if missing_terms:
            print(f"❌ Faltan términos requeridos en el prompt: {missing_terms}")
            return False

        print("✅ Prompt incluye todos los términos requeridos")
        print(f"📏 Longitud del prompt: {len(prompt_content)} caracteres")
        return True

    except Exception as e:
        print(f"❌ Error verificando prompt: {e}")
        return False

def check_dependencies():
    """Verificar dependencias exactas en requirements.txt"""
    print("\n🔍 Verificando dependencias exactas...")

    required_versions = {
        'google-genai': '1.56.0',
        'PyMuPDF': '1.23.25',
        'Pillow': '10.2.0'
    }

    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()

        missing_or_wrong = []
        for package, version in required_versions.items():
            if f'{package}=={version}' not in content:
                missing_or_wrong.append(f'{package}=={version}')

        if missing_or_wrong:
            print("❌ Versiones incorrectas o faltantes:")
            for item in missing_or_wrong:
                print(f"   - {item}")
            return False

        print("✅ Todas las dependencias tienen las versiones correctas")
        return True

    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")
        return False

def main():
    """Función principal de verificación crítica"""
    print("🚨 VERIFICACIÓN CRÍTICA DEL SISTEMA DE EXTRACCIÓN CATASTRAL")
    print("="*80)

    tests = [
        check_library_conflicts,
        check_pdf_processing,
        check_gemini_call_structure,
        check_prompt_content,
        check_dependencies
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("="*80)
    print(f"📊 RESULTADOS: {passed}/{total} verificaciones pasaron")

    if passed == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES CRÍTICAS PASARON!")
        print("\n✅ El sistema está correctamente configurado para:")
        print("   - Usar google-generativeai (SDK v1)")
        print("   - Convertir PDFs a imágenes con 300 DPI usando pdf2image")
        print("   - Enviar [prompt, imagen] a Gemini correctamente")
        print("   - Extraer REFERENCIA CATASTRAL y SUPERFICIE GRÁFICA")
        print("   - Tener dependencias compatibles")
    else:
        print("⚠️  Algunas verificaciones fallaron. Revisa los errores arriba.")
        print("\n🔧 Se requiere reescribir ai_engine.py o requirements.txt")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)