import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la función completa
old_pattern = r'def detalles_proyecto_v2\(project_id: str\):.*?(?=def |\Z)'
new_function = '''def detalles_proyecto_v2(project_id: str):
    """Muestra la página de vista previa de un proyecto arquitectónico - VERSIÓN V2"""
    from modules.marketplace import client_panel
    client_panel.show_selected_project_panel(None, project_id)'''

new_content = re.sub(old_pattern, new_function, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Función reemplazada exitosamente')