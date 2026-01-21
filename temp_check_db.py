import sqlite3
import json
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cur.fetchall()
print('Tablas:', [t[0] for t in tables])
# Ver proyectos
try:
    cur.execute('SELECT id, title, nombre FROM projects LIMIT 10')
    projects = cur.fetchall()
    print('Proyectos en projects:')
    for p in projects:
        print(f'ID: {p[0]}, Title: {p[1]}, Nombre: {p[2] if len(p)>2 else "N/A"}')
except Exception as e:
    print(f'Tabla projects error: {e}')
try:
    cur.execute('SELECT id, nombre, title FROM proyectos LIMIT 10')
    proyectos = cur.fetchall()
    print('Proyectos en proyectos:')
    for p in proyectos:
        print(f'ID: {p[0]}, Nombre: {p[1]}, Title: {p[2] if len(p)>2 else "N/A"}')
except Exception as e:
    print(f'Tabla proyectos error: {e}')
conn.close()