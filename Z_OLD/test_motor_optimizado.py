#!/usr/bin/env python3
"""
SCRIPT DE TEST PARA MOTOR DE EXTRACCIÓN CATASTRAL OPTIMIZADO
Ejecuta este script cuando se resetee la cuota de API para verificar funcionamiento completo
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_motor_completo():
    """Test completo del motor de extracción catastral"""
    print("🚀 TEST COMPLETO - MOTOR EXTRACCIÓN CATASTRAL")
    print("=" * 50)

    try:
        # Importar el motor
        from modules.marketplace.ai_engine import extraer_datos_catastral
        print("✅ Motor importado correctamente")

        # Verificar API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY no encontrada en variables de entorno")
            return False
        print("✅ API Key configurada")

        # Verificar archivo PDF
        pdf_path = "MODELOS/Nota_Catastral_ejemplo.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ Archivo PDF no encontrado: {pdf_path}")
            return False
        print(f"✅ PDF encontrado: {pdf_path}")

        # Ejecutar extracción
        print("\n🔍 Ejecutando extracción con IA...")
        resultado = extraer_datos_catastral(pdf_path)

        # Verificar resultado
        if isinstance(resultado, dict) and "error" not in resultado:
            print("✅ Extracción exitosa!")
            print("\n📊 DATOS EXTRAÍDOS:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))

            # Validar campos requeridos
            campos_requeridos = ["referencia_catastral", "superficie_grafica_m2", "municipio", "coordenadas_utm_ejes"]
            campos_presentes = [campo for campo in campos_requeridos if campo in resultado]

            print(f"\n📋 Campos extraídos: {len(campos_presentes)}/{len(campos_requeridos)}")
            for campo in campos_requeridos:
                status = "✅" if campo in resultado else "❌"
                print(f"  {status} {campo}")

            return True

        else:
            print("❌ Error en extracción:")
            print(resultado)
            return False

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_conversion_sin_api():
    """Test solo de conversión PDF a imagen (sin consumir cuota)"""
    print("\n🔧 TEST CONVERSIÓN PDF (sin API)")
    print("-" * 30)

    try:
        import fitz
        from PIL import Image
        import io

        pdf_path = "MODELOS/Nota_Catastral_ejemplo.pdf"
        if not os.path.exists(pdf_path):
            print(f"❌ PDF no encontrado: {pdf_path}")
            return False

        # Convertir PDF a imagen
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        img = Image.open(io.BytesIO(pix.tobytes()))

        print(f"✅ Conversión exitosa: {img.size} píxeles")
        print(f"   - Ancho: {img.size[0]}px")
        print(f"   - Alto: {img.size[1]}px")
        print(f"   - Modo: {img.mode}")

        doc.close()
        return True

    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO TESTS DEL MOTOR OPTIMIZADO\n")

    # Test básico sin API
    conversion_ok = test_conversion_sin_api()

    if conversion_ok:
        print("\n" + "="*50)
        print("¿QUIERES EJECUTAR EL TEST COMPLETO CON API?")
        print("(Esto consumirá cuota de Gemini API)")
        respuesta = input("Escribe 'SI' para continuar: ").strip().upper()

        if respuesta == "SI":
            test_motor_completo()
        else:
            print("Test completo cancelado. Ejecuta este script cuando se resetee la cuota.")
    else:
        print("❌ Falló el test básico. Revisa la instalación de PyMuPDF.")