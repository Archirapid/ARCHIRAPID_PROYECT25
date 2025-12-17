import json
import sys
import os

# Ensure repo root is on sys.path so `src` package can be imported
sys.path.insert(0, os.path.abspath('.'))

try:
    from src import db
except Exception as e:
    print('ERROR importing db:', e)
    sys.exit(1)

try:
    resultados = db.list_fincas_filtradas('Madrid', 100.0, 200000.0)
    print('COUNT:', len(resultados))
    print(json.dumps(resultados[:5], ensure_ascii=False, indent=2))
except Exception as e:
    print('ERROR running query:', e)
    import traceback
    traceback.print_exc()
