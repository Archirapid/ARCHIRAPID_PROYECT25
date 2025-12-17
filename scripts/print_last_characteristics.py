import sys
import os
import json

# Ensure repository root is on sys.path so `from src import db` works
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src import db

conn = db.get_conn()
cur = conn.cursor()
cur.execute("SELECT id, characteristics_json FROM projects ORDER BY rowid DESC LIMIT 1")
r = cur.fetchone()
if r:
    print(json.dumps(dict(r), ensure_ascii=False))
else:
    print("NOT FOUND")
conn.close()
