# ocr_and_preprocess.py
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from pathlib import Path
import json
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("PASO 2: OCR Y PREPROCESADO DE IMAGEN CATASTRAL")
print("=" * 60)

# 🔍 1. VERIFICAR TESSERACT
try:
    import pytesseract
    # Buscar Tesseract en ubicaciones comunes de Windows y Linux
    possible_paths = [
        r"D:\tesseract-5.5.1\tesseract.exe",
        r"E:\tesseract-5.5.1\tesseract.exe",
        r"E:\Tesseract-5.5.1\tesseract.exe",
        r"E:\tesseract\tesseract.exe",
        r"E:\Tesseract-OCR\tesseract.exe",
        r"E:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
    ]
    
    tesseract_found = False
    for tess_path in possible_paths:
        if Path(tess_path).exists():
            pytesseract.pytesseract.tesseract_cmd = tess_path
            tesseract_found = True
            print(f"✅ Tesseract encontrado: {tess_path}")
            break
    
    if not tesseract_found:
        print("⚠️ Tesseract no encontrado en rutas estándar. OCR se ejecutará sin configurar ruta.")
        print("   Si falla, instala Tesseract o configura pytesseract.tesseract_cmd")
except ImportError:
    print("⚠️ pytesseract no instalado. Saltando OCR (solo preprocesado de imagen)")
    pytesseract = None

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

print(f"✅ Imagen encontrada: {IMG_PATH}")

# Load image
print("\n🔄 Procesando imagen...")
img = cv2.imread(str(IMG_PATH))
if img is None:
    print(f"❌ ERROR: No se pudo cargar la imagen {IMG_PATH}")
    sys.exit(1)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(f"   Dimensiones: {gray.shape[1]}x{gray.shape[0]} px")
print("  ✓ Imagen convertida a escala de grises")

# Denoise
print("   Eliminando ruido...")
gray = cv2.fastNlMeansDenoising(gray, h=10)
print("  ✓ Eliminación de ruido completada")

# Adaptive threshold (binarize)
print("   Binarizando...")
th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY_INV, 25, 10)
print("  ✓ Binarización adaptativa aplicada")

# Morphology to close small holes
print("   Aplicando cierre morfológico...")
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)
print("  ✓ Morfología (cierre) aplicada")

# Save processed image
proc_path = OUT_DIR / "page_1_processed.png"
cv2.imwrite(str(proc_path), closed)
print(f"✅ Imagen procesada guardada: {proc_path}")

# OCR on original grayscale (better results than on binary)
print("\n🔍 Ejecutando OCR (puede tardar 10-30 segundos)...")
ocr_success = False
ocr_text = ""
try:
    if pytesseract is None:
        raise ImportError("pytesseract no está disponible")
    
    custom_config = r'--oem 3 --psm 6'
    # Intentar primero con español
    try:
        ocr_text = pytesseract.image_to_string(gray, config=custom_config, lang='spa')
        print(f"✅ OCR completado (español): {len(ocr_text)} caracteres")
    except:
        # Si falla español, intentar inglés
        ocr_text = pytesseract.image_to_string(gray, config=custom_config)
        print(f"✅ OCR completado (inglés): {len(ocr_text)} caracteres")
    
    ocr_file = IN_DIR / "ocr_text.txt"
    ocr_file.write_text(ocr_text, encoding="utf-8")
    print(f"✅ Texto OCR guardado: {ocr_file}")
    ocr_success = True
    
    # Mostrar preview
    print("\n" + "=" * 60)
    print("PREVIEW DEL TEXTO EXTRAÍDO (primeras 400 caracteres):")
    print("=" * 60)
    print(ocr_text[:400])
    print("=" * 60)
    
except ImportError:
    print("⚠️  pytesseract no instalado. Saltando OCR.")
    print("   Instala con: pip install pytesseract")
except Exception as e:
    print(f"⚠️  OCR falló: {e}")
    print("   Verifica que Tesseract esté instalado en el sistema:")
    print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")

# Write summary
summary = {
    "original_image": str(IMG_PATH),
    "processed_image": str(proc_path),
    "ocr_success": ocr_success,
    "ocr_chars": len(ocr_text) if ocr_success else 0,
    "ocr_lines": len(ocr_text.splitlines()) if ocr_success else 0,
    "image_dimensions": f"{gray.shape[1]}x{gray.shape[0]}",
    "preprocessing": {
        "denoise": "fastNlMeansDenoising(h=10)",
        "binarization": "adaptiveThreshold GAUSSIAN_C",
        "morphology": "MORPH_CLOSE 3x3 kernel, 2 iterations"
    }
}
summary_file = IN_DIR / "process_summary.json"
summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n✅ Resumen guardado: {summary_file}")

print("\n" + "=" * 60)
print("✅ PROCESO COMPLETADO")
print("=" * 60)
print(f"\n📁 Archivos generados en: {OUT_DIR.absolute()}")
print(f"   1. page_1_processed.png - Imagen procesada (blanco/negro)")
if ocr_success:
    print(f"   2. ocr_text.txt - Texto extraído por OCR")
print(f"   3. process_summary.json - Resumen del proceso")
print("\n💡 SIGUIENTE PASO: Revisa los archivos y luego ejecuta vectorize_plan.py")

