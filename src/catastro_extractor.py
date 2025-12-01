import fitz  # PyMuPDF
import pandas as pd
import os
import pytesseract
from PIL import Image

# Configurar Tesseract (ajusta el path si es diferente)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verificar si Tesseract está instalado
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract OCR instalado: {version}")
except Exception as e:
    print(f"Tesseract no encontrado: {e}. Instala Tesseract desde https://github.com/UB-Mannheim/tesseract/wiki")

def extraer_datos_catastro(pdf_path):
    """
    Extrae datos de un PDF catastral: texto, tablas y plano/imagen.

    Args:
        pdf_path (str): Ruta al archivo PDF

    Returns:
        dict: Diccionario con 'texto', 'tablas' (lista de DataFrames), 'plano' (ruta a imagen o None), 'texto_ocr' (texto de OCR)
    """
    datos = {'texto': '', 'tablas': [], 'plano': None, 'texto_ocr': ''}

    try:
        doc = fitz.open(pdf_path)

        # Extraer texto de todas las páginas
        for page in doc:
            texto_pagina = page.get_text()
            datos['texto'] += texto_pagina + '\n'

            # Extraer tablas (PyMuPDF 1.23+ soporta detección automática)
            try:
                tables = page.find_tables()
                for table in tables:
                    df = pd.DataFrame(table.extract())
                    if not df.empty:
                        datos['tablas'].append(df)
            except Exception as e:
                print(f"Error extrayendo tablas: {e}")

            # Extraer imágenes/plano (primera imagen encontrada)
            if datos['plano'] is None:
                img_list = page.get_images(full=True)
                if img_list:
                    xref = img_list[0][0]
                    try:
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]

                        # Guardar en uploads/
                        uploads_dir = "uploads"
                        if not os.path.exists(uploads_dir):
                            os.makedirs(uploads_dir)

                        plano_path = os.path.join(uploads_dir, "plano_finca.png")
                        with open(plano_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        datos['plano'] = plano_path
                    except Exception as e:
                        print(f"Error extrayendo imagen: {e}")

        # Aplicar OCR al plano extraído si existe
        if datos['plano'] and os.path.exists(datos['plano']):
            try:
                img = Image.open(datos['plano'])
                texto_ocr = pytesseract.image_to_string(img, lang='spa')  # Español
                datos['texto_ocr'] = texto_ocr
                print(f"OCR aplicado: {len(texto_ocr)} caracteres extraídos")
            except Exception as e:
                print(f"Error en OCR: {e}")
                datos['texto_ocr'] = f"Error OCR: {str(e)}"

        doc.close()

    except Exception as e:
        print(f"Error procesando PDF: {e}")
        datos['texto'] = f"Error: {str(e)}"

    return datos