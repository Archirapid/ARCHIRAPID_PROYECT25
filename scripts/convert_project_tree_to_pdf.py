from pathlib import Path
import sys

src = Path('project_tree.txt')
pdf = Path('project_tree.pdf')

if not src.exists():
    print('ERROR: project_tree.txt not found')
    sys.exit(2)

text = src.read_text(encoding='utf-8', errors='replace')

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception as e:
    print('reportlab not available:', e)
    print('Attempting to install reportlab into the active Python...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab'])
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

c = canvas.Canvas(str(pdf), pagesize=A4)
width, height = A4
margin = 36
max_width = width - 2*margin
max_height = height - 2*margin

lines = text.splitlines()
line_height = 11
x = margin
y = height - margin - line_height
c.setFont('Courier', 10)

for ln in lines:
    # wrap long lines
    while ln:
        if c.stringWidth(ln, 'Courier', 10) <= max_width:
            c.drawString(x, y, ln)
            ln = ''
            y -= line_height
        else:
            # find wrap point
            approx_chars = int(len(ln) * (max_width / c.stringWidth(ln, 'Courier', 10)))
            part = ln[:max(10, approx_chars)]
            # backtrack to last space
            i = part.rfind(' ')
            if i <= 0:
                i = max(10, approx_chars)
            c.drawString(x, y, ln[:i])
            ln = ln[i:].lstrip()
            y -= line_height
        if y < margin + line_height:
            c.showPage()
            c.setFont('Courier', 10)
            y = height - margin - line_height

c.save()
print('PDF generado en', pdf.resolve())
