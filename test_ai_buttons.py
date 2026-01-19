import sys
sys.path.append('.')
import sqlite3
from project_detail import get_project_by_id

# Verificar que podemos obtener el proyecto de prueba
try:
    project = get_project_by_id(1)  # ID del proyecto de prueba
    if project:
        print('✅ Proyecto obtenido correctamente desde project_detail.py')
        print(f'Título: {project.get("titulo", "N/A")}')
        print(f'OCR disponible: {"Sí" if project.get("ocr_text") else "No"}')
        if project.get("ocr_text"):
            ocr_len = len(project.get("ocr_text", ""))
            print(f'Longitud OCR: {ocr_len} caracteres')
    else:
        print('❌ No se pudo obtener el proyecto')
except Exception as e:
    print(f'❌ Error al obtener proyecto: {e}')

# Verificar que la función detalles_proyecto_v2 existe y se puede importar
try:
    from app import detalles_proyecto_v2
    print('✅ Función detalles_proyecto_v2 importada correctamente')
except ImportError as e:
    print(f'❌ Error importando función: {e}')
except Exception as e:
    print(f'❌ Error general: {e}')

print('\n🎯 La aplicación debería mostrar los botones AI cuando visites:')
print('http://localhost:8501')
print('Y navegues a la vista de detalles del proyecto "TEST FINAL PLANOS"')