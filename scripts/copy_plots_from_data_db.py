import sqlite3
from pathlib import Path

SRC = Path('data.db')
DST = Path(r'C:/ARCHIRAPID_PROYECT25/database.db')

if not SRC.exists():
    print('Source data.db not found at', SRC.resolve())
    exit(1)

conn = sqlite3.connect(str(DST))
cur = conn.cursor()
# Attach source
cur.execute(f"ATTACH DATABASE '{str(SRC.resolve())}' AS srcdb")
# Ensure destination table exists (will be created by ensure_tables normally)
# Copy rows from srcdb.plots into main.plots; use column list to be safer
try:
    cur.execute('SELECT name FROM srcdb.sqlite_master WHERE type="table" AND name="plots"')
    if not cur.fetchone():
        print('No plots table in source DB')
    else:
        # We'll attempt to select common columns between source and destination
        # Get dest cols
        cur.execute("PRAGMA table_info(plots)")
        dst_cols = [r[1] for r in cur.fetchall()]
        cur.execute("PRAGMA srcdb.table_info(plots)")
        src_cols = [r[1] for r in cur.fetchall()]
        cols = [c for c in src_cols if c in dst_cols]
        if not cols:
            print('No common columns to copy')
        else:
            cols_sql = ','.join(cols)
            sql = f"INSERT OR REPLACE INTO main.plots ({cols_sql}) SELECT {cols_sql} FROM srcdb.plots"
            cur.execute(sql)
            conn.commit()
            print('Copied rows from data.db plots to database.db (columns:', cols_sql, ')')
except Exception as e:
    print('Error copying plots:', e)
finally:
    cur.execute("DETACH DATABASE srcdb")
    conn.close()
