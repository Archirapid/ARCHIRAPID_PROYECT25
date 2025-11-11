"""
Test de imports y sintaxis de app.py
"""
import sys
sys.path.insert(0, 'D:/ARCHIRAPID_PROYECT25')

try:
    import streamlit
    import folium
    from streamlit_folium import st_folium
    import pandas
    import sqlite3
    import os
    import uuid
    from datetime import datetime
    import base64
    import json
    print("✅ Todos los imports requeridos están disponibles")
except ImportError as e:
    print(f"❌ Error de import: {e}")
    sys.exit(1)

# Verificar sintaxis
try:
    with open('D:/ARCHIRAPID_PROYECT25/app.py', 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, 'app.py', 'exec')
    print("✅ Sintaxis del app.py correcta")
except SyntaxError as e:
    print(f"❌ Error de sintaxis en app.py: {e}")
    sys.exit(1)

print("\n✅ TODOS LOS TESTS PASADOS")
