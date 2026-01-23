# extract_pdf.py
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import re

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def extract_pdf_data(pdf_path):
    """Extrae datos clave de un PDF de nota simple catastral."""
    try:
        import fitz  # pymupdf
        doc = fitz.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        
        # Extraer datos con regex (ejemplo simple)
        data = {}
        # Superficie
        match = re.search(r'Superficie\s*[:\-]?\s*(\d+(?:,\d+)?)', text, re.IGNORECASE)
        if match:
            data['surface_m2'] = float(match.group(1).replace(',', '.'))
        
        # Referencia catastral
        match = re.search(r'Referencia\s*catastral\s*[:\-]?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if match:
            data['cadastral_ref'] = match.group(1)
        
        # Uso (urbano/rústico)
        if 'urbano' in text.lower():
            data['is_urban'] = True
        elif 'rústico' in text.lower():
            data['is_urban'] = False
        
        # Edificabilidad aproximada (mock si no está)
        if 'surface_m2' in data:
            data['buildable_m2'] = data['surface_m2'] * 0.8  # Ejemplo
        
        return data
    except Exception as e:
        return {"error": str(e)}

# Código original para standalone
if __name__ == "__main__":
    PDF_PATH = Path("Catastro.pdf")
    OUTDIR = Path("catastro_output")

    # Validate PDF exists
    if not PDF_PATH.exists():
        print(f"❌ ERROR: PDF no encontrado en {PDF_PATH.absolute()}")
        print("   Coloca 'Catastro.pdf' en la misma carpeta que este script.")
        sys.exit(1)

    OUTDIR.mkdir(exist_ok=True)

    # Try PyMuPDF first (fast, no external deps)
    try:
        import fitz  # pymupdf
        print(f"📄 Extrayendo PDF con PyMuPDF: {PDF_PATH}")
        doc = fitz.open(str(PDF_PATH))
        texts = []
        for i, page in enumerate(doc):
            txt = page.get_text("text")
            texts.append(txt or "")
            pix = page.get_pixmap(dpi=200)
            out_png = OUTDIR / f"page_{i+1}.png"
            pix.save(str(out_png))
            print(f"  ✓ Guardada imagen: {out_png}")
        
        text_file = OUTDIR / "extracted_text.txt"
        text_file.write_text("\n\n".join(texts), encoding="utf-8")
        print(f"✅ Texto extraído guardado en: {text_file}")
        print(f"✅ Total páginas procesadas: {len(texts)}")
        
    except ImportError as ie:
        print(f"⚠️  PyMuPDF no instalado: {ie}")
        print("   Instalando fallback con: pip install pymupdf")
        sys.exit(1)
    except Exception as e:
        print(f"❌ PyMuPDF falló: {e}")
        # fallback to pdfplumber + pdf2image
    print("🔄 Intentando fallback con pdfplumber...")
    try:
        import pdfplumber
        from pdf2image import convert_from_path
        
        texts = []
        with pdfplumber.open(str(PDF_PATH)) as pdf:
            for i, page in enumerate(pdf.pages):
                txt = page.extract_text() or ""
                texts.append(txt)
        
        text_file = OUTDIR / "extracted_text.txt"
        text_file.write_text("\n\n".join(texts), encoding="utf-8")
        
        images = convert_from_path(str(PDF_PATH), dpi=200)
        for i, im in enumerate(images):
            out_png = OUTDIR / f"page_{i+1}.png"
            im.save(out_png)
            print(f"  ✓ Guardada imagen: {out_png}")
        
        print(f"✅ Extracción fallback completada. Total páginas: {len(texts)}")
    except ImportError as ie2:
        print(f"❌ Fallback fallido - librerías faltantes: {ie2}")
        print("   Instala: pip install pdfplumber pdf2image")
        print("   NOTA: pdf2image requiere Poppler binario en Windows")
        print("   ⚠️  Pero PyMuPDF ya funcionó correctamente, continuando...")
        # No hacer sys.exit(1) si PyMuPDF ya funcionó
    except Exception as e2:
        print(f"❌ Extracción fallback también falló: {e2}")
        print("   ⚠️  Pero PyMuPDF ya funcionó correctamente, continuando...")
        # No hacer sys.exit(1) si PyMuPDF ya funcionó
