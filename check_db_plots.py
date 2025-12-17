from src import db


def main():
    # Ensure tables/migrations are applied
    db.ensure_tables()

    conn = db.get_conn()
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(plots);")
        rows = cur.fetchall()

        print("Columns in 'plots':")
        for r in rows:
            # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
            cid = r[0]
            name = r[1]
            typ = r[2]
            notnull = r[3]
            dflt = r[4]
            pk = r[5]
            print(f"- {name} (type={typ}, notnull={notnull}, default={dflt}, pk={pk})")

        # Now print all rows from plots with selected columns for readability
        print('\nRows in "plots":')
        try:
            cur.execute("SELECT id, title, province, locality, lat, lon, m2, price FROM plots ORDER BY created_at DESC;")
            plot_rows = cur.fetchall()
            if not plot_rows:
                print("(no rows found in plots)")
            else:
                for pr in plot_rows:
                    pid, title, province, locality, lat, lon, m2, price = pr
                    print(f"- id={pid} | title={title} | province={province} | locality={locality} | lat={lat} | lon={lon} | m2={m2} | price={price}")
        except Exception as e:
            print(f"Could not query plots rows: {e}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
