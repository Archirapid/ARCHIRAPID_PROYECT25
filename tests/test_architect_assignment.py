import uuid
from datetime import datetime

from src.db import insert_architect, insert_project, update_project_architect_id, get_all_projects, ensure_tables


def test_update_project_architect_id():
    ensure_tables()
    # Crear proyecto de prueba
    proj_id = f"proj_test_{uuid.uuid4().hex[:6]}"
    insert_project({
        'id': proj_id,
        'title': 'Proyecto Test Arquitecto',
        'architect_name': 'Sin Arquitecto',
        'area_m2': 120,
        'max_height': 8.5,
        'style': 'moderno',
        'price': 95000,
        'file_path': None,
        'description': 'Proyecto para probar asignación de arquitecto',
        'created_at': datetime.utcnow().isoformat()
    })
    # Crear arquitecto
    arch_id = f"arch_{uuid.uuid4().hex[:6]}"
    arch_email = f"{arch_id}@demo.test"
    insert_architect({
        'id': arch_id,
        'name': 'Arquitecto Test Unidad',
        'email': arch_email,
        'phone': None,
        'company': 'Test Co',
        'nif': 'TESTNIF',
        'created_at': datetime.utcnow().isoformat()
    })
    # Asignar
    update_project_architect_id(proj_id, arch_id)
    df = get_all_projects()
    row = df[df['id'] == proj_id].iloc[0]
    assert row['architect_id'] == arch_id, 'architect_id no se asignó correctamente'
