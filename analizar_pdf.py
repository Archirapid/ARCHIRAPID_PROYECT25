import PyPDF2

pdf_path = "MODELOS/Nota_Catastral_ejemplo.pdf"

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    num_pages = len(reader.pages)
    
    print(f"📄 Total de páginas: {num_pages}")
    
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        print(f"\n--- PÁGINA {i} ---")
        print(f"Longitud del texto: {len(text)} caracteres")
        
        # Check for keywords
        if "INFORMACIÓN GRÁFICA" in text.upper() or "PLANO" in text.upper():
            print("✅ Contiene: PLANO o INFORMACIÓN GRÁFICA")
        if "COORDENADAS" in text.upper() or "UTM" in text.upper():
            print("✅ Contiene: COORDENADAS o UTM")
        if "350" in text or "745" in text:
            print("✅ Contiene números que podrían ser coordenadas UTM")
        
        # Show first 200 chars
        print(f"Primeros 200 caracteres:\n{text[:200]}")