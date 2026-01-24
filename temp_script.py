
# Leer el archivo línea por línea y encontrar la función
lines = []
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar la línea de la función
func_start = None
for i, line in enumerate(lines):
    if 'def detalles_proyecto_v2(project_id: str):' in line:
        func_start = i
        break

if func_start is not None:
    # Encontrar el final de la función (st.stop())
    func_end = None
    for i in range(func_start, len(lines)):
        if 'st.stop()' in lines[i]:
            func_end = i
            break
    
    if func_end is not None:
        # Crear nueva función
        new_lines = [
            'def detalles_proyecto_v2(project_id: str):\n',
            '    \
\\Muestra
la
página
de
vista
previa
de
un
proyecto
arquitectónico
-
VERSIÓN
V2\\\\n',
            '    from modules.marketplace import client_panel\n',
            '    client_panel.show_selected_project_panel(None, project_id)\n'
        ]
        
        # Reemplazar las líneas
        lines[func_start:func_end+1] = new_lines
        
        # Escribir el archivo
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print('Función reemplazada exitosamente')
    else:
        print('No se encontró el final de la función')
else:
    print('No se encontró la función')

