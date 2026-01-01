#!/usr/bin/env python3
"""
EJEMPLO SIMPLE DE USO - Extracción de datos catastrales
Para novatos: este script muestra cómo usar la función extraer_datos_catastral
"""

from modules.marketplace.ai_engine import extraer_datos_catastral
import json

def ejemplo_uso():
    """Ejemplo simple de cómo usar la función"""

    # Ruta al PDF de la nota catastral
    pdf_path = "MODELOS/Nota_Catastral_ejemplo.pdf"

    print("🔍 Extrayendo datos de nota catastral...")
    print(f"📄 Archivo: {pdf_path}")
    print("-" * 50)

    # Llamar a la función
    resultado = extraer_datos_catastral(pdf_path)

    # Mostrar resultado
    if "error" in resultado:
        print("❌ Error en extracción:")
        print(resultado["error"])
        if "raw_response" in resultado:
            print("\nRespuesta cruda de la IA:")
            print(resultado["raw_response"])
    else:
        print("✅ ¡Extracción exitosa!")
        print("\n📊 DATOS EXTRAÍDOS:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Mostrar campos específicos
        print("\n🔸 Campos encontrados:")
        for campo, valor in resultado.items():
            print(f"  {campo}: {valor}")

if __name__ == "__main__":
    ejemplo_uso()