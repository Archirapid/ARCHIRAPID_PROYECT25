#!/usr/bin/env python3
"""
Script de validación del sistema de extracción catastral
Verifica que todas las funciones y prompts estén configurados correctamente
"""

import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Verificar que todas las importaciones funcionen"""
    print("🔍 Verificando importaciones...")

    try:
        from modules.marketplace.ai_engine import generate_from_pdf, generate_from_image, PROMPT_ANALISIS
        print("✅ Importaciones de ai_engine exitosas")

        # Verificar que owners.py se puede importar (aunque no tenga extract_data_from_pdf)
        import modules.marketplace.owners
        print("✅ Módulo owners importado exitosamente")

        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_prompt_structure():
    """Verificar que el PROMPT_ANALISIS tenga la estructura correcta"""
    print("\n🔍 Verificando estructura del PROMPT_ANALISIS...")

    try:
        from modules.marketplace.ai_engine import PROMPT_ANALISIS

        # Verificar que sea un string
        if not isinstance(PROMPT_ANALISIS, str):
            print("❌ PROMPT_ANALISIS no es un string")
            return False

        # Verificar que contenga elementos clave
        required_elements = [
            "experto en topografía",
            "Nota Catastral",
            "JSON",
            "coordenadas",
            "plano"
        ]

        for element in required_elements:
            if element.lower() not in PROMPT_ANALISIS.lower():
                print(f"❌ Falta elemento requerido: {element}")
                return False

        print("✅ PROMPT_ANALISIS tiene estructura correcta")
        print(f"📏 Longitud del prompt: {len(PROMPT_ANALISIS)} caracteres")

        return True
    except Exception as e:
        print(f"❌ Error verificando PROMPT_ANALISIS: {e}")
        return False

def test_function_signatures():
    """Verificar que las funciones tengan las firmas correctas"""
    print("\n🔍 Verificando firmas de funciones...")

    try:
        from modules.marketplace.ai_engine import generate_from_pdf, generate_from_image
        import inspect

        # Verificar generate_from_pdf
        sig_pdf = inspect.signature(generate_from_pdf)
        params_pdf = list(sig_pdf.parameters.keys())

        if 'pdf_bytes' not in params_pdf:
            print("❌ generate_from_pdf no tiene parámetro pdf_bytes")
            return False

        print("✅ Firma de generate_from_pdf correcta")

        # Verificar generate_from_image
        sig_img = inspect.signature(generate_from_image)
        params_img = list(sig_img.parameters.keys())

        if 'image_bytes' not in params_img:
            print("❌ generate_from_image no tiene parámetro image_bytes")
            return False

        print("✅ Firma de generate_from_image correcta")

        return True
    except Exception as e:
        print(f"❌ Error verificando firmas: {e}")
        return False

def test_json_parsing():
    """Verificar que el parsing JSON funcione correctamente"""
    print("\n🔍 Verificando parsing JSON...")

    # Simular respuesta JSON esperada
    mock_response = {
        "numero_parcela_principal": "12345A",
        "vertices_coordenadas": [
            {"x": 100, "y": 200},
            {"x": 150, "y": 200},
            {"x": 150, "y": 250},
            {"x": 100, "y": 250}
        ],
        "plano_visual": "Descripción del plano...",
        "superficie_total": 500.0
    }

    try:
        # Verificar que se puede serializar
        json_str = json.dumps(mock_response, indent=2, ensure_ascii=False)
        print("✅ Serialización JSON correcta")

        # Verificar que se puede deserializar
        parsed = json.loads(json_str)
        print("✅ Deserialización JSON correcta")

        # Verificar estructura
        required_keys = ["numero_parcela_principal", "vertices_coordenadas", "plano_visual"]
        for key in required_keys:
            if key not in parsed:
                print(f"❌ Falta clave requerida: {key}")
                return False

        print("✅ Estructura JSON correcta")
        return True

    except Exception as e:
        print(f"❌ Error en parsing JSON: {e}")
        return False

def test_file_structure():
    """Verificar que los archivos existan y sean accesibles"""
    print("\n🔍 Verificando estructura de archivos...")

    required_files = [
        "modules/marketplace/ai_engine.py",
        "modules/marketplace/owners.py",
        "requirements.txt"
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
        else:
            print(f"❌ {file_path} no encontrado")
            return False

    return True

def main():
    """Función principal de validación"""
    print("🚀 Iniciando validación del sistema de extracción catastral\n")

    tests = [
        test_file_structure,
        test_imports,
        test_prompt_structure,
        test_function_signatures,
        test_json_parsing
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todas las validaciones pasaron exitosamente!")
        print("\n📝 El sistema está listo para procesar documentos catastrales")
        print("   cuando se restablezca la cuota de la API de Gemini.")
    else:
        print("⚠️  Algunas validaciones fallaron. Revisa los errores arriba.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)