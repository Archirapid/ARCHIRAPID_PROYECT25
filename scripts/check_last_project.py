import sqlite3
import json
from pathlib import Path
DB = Path(r"C:/ARCHIRAPID_PROYECT25/database.db")
conn = sqlite3.connect(str(DB))
cursor = conn.cursor()
cursor.execute("SELECT title, habitaciones, banos, characteristics_json FROM projects ORDER BY id DESC LIMIT 1")
print(cursor.fetchone())
conn.close()
