#!/usr/bin/env python3
"""
Verificación técnica de los 3 detalles críticos especificados por el usuario
"""

import sys
import os

def check_import():
    """Verificar importación correcta: import google.generativeai as genai"""
    print("🔍 Verificando importación...")

    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if 'import google.generativeai as genai' in content:
            print("✅ Importación correcta: import google.generativeai as genai")
            return True
        else:
            print("❌ Importación incorrecta - debe ser: import google.generativeai as genai")
            return False
    except Exception as e:
        print(f"❌ Error verificando importación: {e}")
        return False

def check_pdf_conversion():
    """Verificar que usa PyMuPDF (fitz) en lugar de pdf2image (sin Poppler)"""
    print("\n🔍 Verificando conversión PDF (sin dependencias externas)...")

    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if 'import fitz' in content and 'pdf2image' not in content:
            print("✅ Usa PyMuPDF (fitz) - sin dependencias externas como Poppler")
            return True
        elif 'pdf2image' in content:
            print("❌ Todavía usa pdf2image - requiere Poppler en Windows")
            return False
        else:
            print("❌ No se encontró método de conversión PDF")
            return False
    except Exception as e:
        print(f"❌ Error verificando conversión PDF: {e}")
        return False

def check_model():
    """Verificar que usa gemini-1.5-flash (el más rápido para documentos)"""
    print("\n🔍 Verificando modelo Gemini...")

    try:
        with open('modules/marketplace/ai_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if "gemini-1.5-flash" in content:
            print("✅ Usa gemini-1.5-flash (el más rápido para documentos con imágenes)")
            return True
        else:
            print("❌ No usa gemini-1.5-flash")
            return False
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")
        return False

def check_dependencies():
    """Verificar que requirements.txt no incluye pdf2image"""
    print("\n🔍 Verificando dependencias...")

    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()

        if 'pdf2image' not in content:
            print("✅ requirements.txt no incluye pdf2image (evita dependencias externas)")
            return True
        else:
            print("❌ requirements.txt todavía incluye pdf2image")
            return False
    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")
        return False

def main():
    print("🔧 VERIFICACIÓN TÉCNICA DE LOS 3 DETALLES CRÍTICOS")
    print("="*60)

    tests = [
        check_import,
        check_pdf_conversion,
        check_model,
        check_dependencies
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "="*60)
    print(f"📊 RESULTADOS: {passed}/{total} verificaciones técnicas pasaron")

    if passed == total:
        print("🎉 ¡TODOS LOS DETALLES TÉCNICOS ESTÁN CORRECTOS!")
        print("\n✅ Configuración técnica optimizada:")
        print("   - Import: google.generativeai as genai")
        print("   - PDF: PyMuPDF (fitz) - sin Poppler")
        print("   - Modelo: gemini-1.5-flash (más rápido)")
        print("   - Dependencies: Sin pdf2image")
    else:
        print("⚠️  Algunos detalles técnicos necesitan corrección.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)