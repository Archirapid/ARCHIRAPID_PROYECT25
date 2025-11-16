"""Script para arreglar indentación del bloque de arquitecto logueado"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar el inicio del bloque problemático (línea 2145)
# y agregar 4 espacios de indentación hasta la línea del except (antes de elif page == 'clientes')

in_arch_logged_block = False
fixed_lines = []

for i, line in enumerate(lines, 1):
    # Detectar inicio del bloque de arquitecto logueado
    if i == 2145 and line.strip().startswith('with col_name:'):
        in_arch_logged_block = True
        fixed_lines.append(line)
    # Detectar fin del bloque (línea con except Exception)
    elif 'except Exception as e:' in line and 'arquitectos' in line:
        in_arch_logged_block = False
        fixed_lines.append(line)
    # Si estamos en el bloque y la línea NO está vacía, agregar indentación
    elif in_arch_logged_block and line.strip():
        # Solo agregar indentación si no es una línea que ya tiene suficiente
        if not line.startswith('            '):  # Ya tiene 12+ espacios
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Guardar archivo corregido
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentación corregida")
