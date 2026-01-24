import re

# Leer el archivo
with open('c:\\ARCHIRAPID_PROYECT25\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar la función detalles_proyecto_v2
func_match = re.search(r'def detalles_proyecto_v2\(.*?\):\s*"""[^"]*?"""\s*from modules\.marketplace import client_panel\s*client_panel\.show_selected_project_panel\(None, project_id\)', content, re.DOTALL)

if func_match:
    func_end = func_match.end()

    # Encontrar donde comienza el código principal (después de las líneas vacías)
    main_code_start = re.search(r'\n\n# Lógica de navegación robusta', content[func_end:])

    if main_code_start:
        main_start_pos = func_end + main_code_start.start()

        # Mantener solo la función y el código principal
        new_content = content[:func_end] + '\n\n' + content[main_start_pos:]

        # Escribir el archivo corregido
        with open('c:\\ARCHIRAPID_PROYECT25\\app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Código suelto eliminado correctamente")
    else:
        print("No se encontró el inicio del código principal")
else:
    print("No se encontró la función detalles_proyecto_v2")