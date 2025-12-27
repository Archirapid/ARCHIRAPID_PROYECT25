import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import traceback

try:
    from modules.marketplace.utils import list_published_plots
    print('OK: imported list_published_plots')
except Exception:
    traceback.print_exc()

try:
    import src.db as db
    print('OK: imported src.db')
except Exception:
    traceback.print_exc()

try:
    print('Attempting to call db.ensure_tables()')
    db.ensure_tables()
    print('OK: db.ensure_tables() succeeded')
except Exception:
    traceback.print_exc()

try:
    plots = list_published_plots()
    print(f'list_published_plots returned {len(plots)}')
except Exception:
    traceback.print_exc()
