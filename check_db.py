import sqlite3
conn = sqlite3.connect('archirapid.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
conn.close()
print('Tablas en la base de datos:')
for table in tables:
    print('-', table[0])