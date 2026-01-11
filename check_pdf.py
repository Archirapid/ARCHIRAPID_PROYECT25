import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Ver todos los proyectos y sus memoria_pdf
cursor.execute('SELECT id, title, memoria_pdf FROM projects')
rows = cursor.fetchall()
conn.close()

print('Todos los proyectos y sus memoria_pdf:')
for row in rows:
    pdf = row[2] if row[2] else 'None'
    print(f'ID: {row[0]}, Title: {row[1]}, PDF: {pdf}')