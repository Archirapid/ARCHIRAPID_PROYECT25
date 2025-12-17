import runpy
import os

# Proxy moved from pages/intranet_crm.py
runpy.run_path(os.path.join(os.path.dirname(__file__), '..', 'views', 'intranet_crm.py'), run_name='__main__')
