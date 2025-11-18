import uuid
from datetime import datetime

from src.db import insert_architect, insert_project, get_all_projects, ensure_tables


def test_insert_project_with_architect():
    ensure_tables()
    arch_id = f"arch_{uuid.uuid4().hex[:6]}"
    insert_architect({
        'id': arch_id,
        'name': 'Test Arq',
        'email': f'{arch_id}@example.com',
        'phone': None,
        'company': 'Test Co',
        'nif': 'XXX',
        'created_at': datetime.utcnow().isoformat()
    })

    proj_id = f"proj_{uuid.uuid4().hex[:6]}"
    insert_project({
        'id': proj_id,
        'title': 'Proyecto con Arq',
        'architect_name': 'Test Arq',
        'architect_id': arch_id,
        'area_m2': 80,
        'max_height': 6.0,
        'style': 'moderno',
        'price': 54000,
        'file_path': None,
        'description': 'Proyecto asociado a arquitecto',
        'created_at': datetime.utcnow().isoformat()
    })

    df = get_all_projects()
    # Debe aparecer nuestro proyecto y tener architect_id correcto
    row = df[df['id'] == proj_id].iloc[0]
    assert row['architect_id'] == arch_id, 'El project no está ligado al arquitecto en la BD'
