import runpy
import os

# Proxy moved from pages/arquitectos_portal.py
runpy.run_path(os.path.join(os.path.dirname(__file__), '..', 'views', 'arquitectos_portal.py'), run_name='__main__')
