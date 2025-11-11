# ocr_and_preprocess.py
import cv2
import numpy as np
from pathlib import Path
import json
import sys

IN_DIR = Path("catastro_output")
IMG_PATH = IN_DIR / "page_1.png"   # normalmente la página del plano
OUT_DIR = IN_DIR

# Validate input exists
if not IN_DIR.exists():
    print(f"❌ ERROR: Directorio no encontrado: {IN_DIR.absolute()}")
    print("   Ejecuta primero 'extract_pdf.py'")
    sys.exit(1)

if not IMG_PATH.exists():
    print(f"❌ ERROR: Imagen no encontrada: {IMG_PATH}")
    print("   Asegúrate de que extract_pdf.py generó las imágenes correctamente.")
    sys.exit(1)

print(f"🖼️  Procesando imagen: {IMG_PATH}")

# Load image
img = cv2.imread(str(IMG_PATH))
if img is None:
    print(f"❌ ERROR: No se pudo cargar la imagen {IMG_PATH}")
    sys.exit(1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print("  ✓ Imagen convertida a escala de grises")

# Denoise
gray = cv2.fastNlMeansDenoising(gray, h=10)
print("  ✓ Eliminación de ruido completada")

# Adaptive threshold (binarize)
th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY_INV, 25, 10)
print("  ✓ Binarización adaptativa aplicada")

# Morphology to close small holes
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)
print("  ✓ Morfología (cierre) aplicada")

# Save processed image
proc_path = OUT_DIR / "page_1_processed.png"
cv2.imwrite(str(proc_path), closed)
print(f"✅ Imagen procesada guardada: {proc_path}")

# OCR on original grayscale (better results than on binary)
ocr_success = False
ocr_text = ""
try:
    import pytesseract
    print("📝 Ejecutando OCR con Tesseract...")
    custom_config = r'--oem 3 --psm 6'
    ocr_text = pytesseract.image_to_string(gray, config=custom_config, lang='spa')
    ocr_file = IN_DIR / "ocr_text.txt"
    ocr_file.write_text(ocr_text, encoding="utf-8")
    print(f"✅ Texto OCR guardado: {ocr_file} ({len(ocr_text)} caracteres)")
    ocr_success = True
except ImportError:
    print("⚠️  pytesseract no instalado. Saltando OCR.")
    print("   Instala con: pip install pytesseract")
except Exception as e:
    print(f"⚠️  OCR falló: {e}")
    print("   Verifica que Tesseract esté instalado en el sistema:")
    print("   Windows: choco install tesseract  o descarga de https://github.com/UB-Mannheim/tesseract/wiki")

# Write summary
summary = {
    "original_image": str(IMG_PATH),
    "processed_image": str(proc_path),
    "ocr_success": ocr_success,
    "ocr_chars": len(ocr_text) if ocr_success else 0,
    "preprocessing": {
        "denoise": "fastNlMeansDenoising(h=10)",
        "binarization": "adaptiveThreshold GAUSSIAN_C",
        "morphology": "MORPH_CLOSE 3x3 kernel, 2 iterations"
    }
}
summary_file = IN_DIR / "process_summary.json"
summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"✅ Resumen guardado: {summary_file}")
print("✅ Procesamiento completado.")
