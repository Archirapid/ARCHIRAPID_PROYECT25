#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix client tabs - remove Propuestas Recibidas"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la línea del radio del cliente
import re

# Patrón para encontrar la línea del radio
pattern = r"client_tab = st\.radio\('',\s*\[.*?Propuestas Recibidas.*?Buscar Fincas.*?\],\s*horizontal=True,\s*key='client_tab_radio'\)"

# Reemplazo
replacement = "client_tab = st.radio('Seleccione una opción:', ['📊 Mi Perfil', '🛠️ Servicios Adicionales', '🗺️ Buscar Fincas'], horizontal=True, key='client_tab_radio', label_visibility='collapsed')"

# Aplicar cambio
new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Tab 'Propuestas Recibidas' eliminado del panel cliente")
else:
    print("❌ No se encontró el patrón para reemplazar")
    # Mostrar línea actual
    for i, line in enumerate(content.split('\n'), 1):
        if 'client_tab' in line and 'Propuestas Recibidas' in line:
            print(f"Línea {i}: {line[:150]}")
