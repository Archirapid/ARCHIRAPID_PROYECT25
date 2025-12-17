import runpy
import os

# Proxy: execute the canonical view implementation from /views
runpy.run_path(os.path.join(os.path.dirname(__file__), '..', 'views', 'ai_configurator.py'), run_name='__main__')

# (moved from pages/ai_configurator.py)
