import sqlite3
from pathlib import Path

DB = Path('archirapid.db')
if not DB.exists():
    print('ERROR: archirapid.db not found at', DB.resolve())
    raise SystemExit(2)

conn = sqlite3.connect(str(DB))
c = conn.cursor()

def cols(table):
    try:
        c.execute(f"PRAGMA table_info('{table}')")
        rows = c.fetchall()
        if not rows:
            print(f"Table '{table}' does not exist or has no columns.")
            return
        print(f"Columns for table '{table}':")
        for r in rows:
            # r: cid, name, type, notnull, dflt_value, pk
            print(f" - {r[1]}  (type={r[2]}, notnull={r[3]}, default={r[4]}, pk={r[5]})")
        print()
    except Exception as e:
        print('ERROR reading', table, e)

cols('plots')
cols('projects')

# Also show CREATE TABLE for context
for t in ('plots','projects'):
    try:
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,))
        row = c.fetchone()
        print(f"CREATE statement for {t}:")
        print(row[0] if row else '(not found)')
        print()
    except Exception as e:
        print('ERROR fetch create', t, e)

conn.close()
