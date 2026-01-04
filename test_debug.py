from modules.marketplace.ai_engine import extraer_datos_catastral
import os

# Verificar si existe un PDF de prueba
pdf_path = "tmp_test_memoria.pdf"
if os.path.exists(pdf_path):
    print(f"Probando con PDF: {pdf_path}")
    result = extraer_datos_catastral(pdf_path)
    print("Resultado:", result)
else:
    print(f"No se encontró el PDF de prueba: {pdf_path}")
    print("Archivos disponibles en el directorio:")
    import os
    for file in os.listdir("."):
        if file.endswith(".pdf"):
            print(f"  - {file}")