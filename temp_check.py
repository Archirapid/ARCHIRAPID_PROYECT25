import sqlite3
import json
conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, files_json FROM projects LIMIT 3')
rows = cursor.fetchall()
for row in rows:
    print('ID:', row[0], 'Title:', row[1])
    if row[2]:
        try:
            files = json.loads(row[2])
            print('  Files:', files)
        except:
            print('  Files (raw):', row[2])
    print()
conn.close()