import sqlite3

conn = sqlite3.connect('C:/ARCHIRAPID_PROYECT25/data.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tablas en la DB:')
for t in tables:
    print(f'  - {t[0]}')

# Count plots
cursor.execute('SELECT COUNT(*) FROM plots')
print(f'\nTotal plots: {cursor.fetchone()[0]}')

# Sample plot
cursor.execute('SELECT id, address, lat, lon FROM plots LIMIT 3')
plots = cursor.fetchall()
print('\nPrimeros 3 plots:')
for p in plots:
    print(f'  ID: {p[0]}, Address: {p[1]}, Lat: {p[2]}, Lon: {p[3]}')

conn.close()
