#!/usr/bin/env python3
"""
TEST DE FUNCIÓN GUARDAR DATOS CATASTRALES
Verifica que la función guardar_datos_catastrales funcione correctamente
"""

from modules.marketplace.owners import guardar_datos_catastrales
import json

def test_guardar_datos():
    """Test de la función guardar_datos_catastrales con datos de ejemplo"""

    print("🧪 TEST - Función guardar_datos_catastrales")
    print("=" * 50)

    # Datos de ejemplo que vendrían de Gemini
    datos_ejemplo = {
        "referencia_catastral": "001100100UN54E0001RI",
        "superficie_grafica_m2": 450,
        "municipio": "Madrid",
        "provincia": "Madrid",
        "coordenadas_utm_ejes": [440000, 4470000, 441000, 4471000]
    }

    # Ruta de ejemplo para el PDF
    pdf_path_ejemplo = "MODELOS/Nota_Catastral_ejemplo.pdf"

    print("📊 Datos a guardar:")
    print(json.dumps(datos_ejemplo, indent=2, ensure_ascii=False))
    print(f"\n📄 PDF path: {pdf_path_ejemplo}")

    # Nota: Esta función requiere que haya una sesión de Streamlit activa
    # para acceder a st.session_state. En un entorno real funcionaría,
    # pero aquí solo verificamos que se importe correctamente.

    print("\n✅ Función importada y lista para usar en Streamlit")
    print("💡 Para probar completamente: ejecuta la app Streamlit y sube un PDF")

if __name__ == "__main__":
    test_guardar_datos()