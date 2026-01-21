with open('c:/ARCHIRAPID_PROYECT25/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Eliminar las líneas 2343 y 2344 (0-indexed 2342 y 2343)
del lines[2342:2344]

with open('c:/ARCHIRAPID_PROYECT25/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Removed unused variable lines')