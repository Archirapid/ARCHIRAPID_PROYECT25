# create_test_pdf.py - Genera PDF de prueba con datos catastrales simulados
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

pdf_path = "Catastro.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)

# Título
c.setFont("Helvetica-Bold", 16)
c.drawString(100, 750, "NOTA SIMPLE CATASTRAL")

# Datos catastrales
c.setFont("Helvetica", 12)
c.drawString(100, 720, "Referencia catastral: 1234567AB0001C0001AB")
c.drawString(100, 690, "Superficie gráfica: 450,50 m²")
c.drawString(100, 660, "Uso: Residencial")
c.drawString(100, 630, "Coordenadas UTM (ETRS89 Huso 30):")
c.drawString(120, 610, "X: 441234.56 m")
c.drawString(120, 590, "Y: 4474321.78 m")

# Dibujar un rectángulo simulando el plano de linderos
c.setFont("Helvetica-Bold", 14)
c.drawString(200, 520, "REPRESENTACIÓN GRÁFICA")

c.setFont("Helvetica", 10)
c.drawString(150, 490, "Escala 1:500")

# Rectángulo principal (lindero)
c.setStrokeColorRGB(0, 0, 0)
c.setLineWidth(2)
c.rect(150, 250, 300, 200)

# Agregar algunas líneas interiores para simular edificación
c.setLineWidth(1)
c.setStrokeColorRGB(0.5, 0.5, 0.5)
c.rect(200, 300, 100, 80)

# Notas al pie
c.setFont("Helvetica", 8)
c.drawString(100, 180, "NORTE: Calle Principal")
c.drawString(100, 165, "SUR: Colindante con parcela 0002")
c.drawString(100, 150, "ESTE: Calle Secundaria")
c.drawString(100, 135, "OESTE: Colindante con parcela 0003")

# Información adicional
c.setFont("Helvetica", 10)
c.drawString(100, 100, "Documento generado con fines de prueba")
c.drawString(100, 85, "Fecha: 11/11/2025")

c.save()
print(f"✅ PDF de prueba creado: {pdf_path}")
