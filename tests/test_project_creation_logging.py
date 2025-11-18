import uuid
from datetime import datetime
from src.logger import get_recent_events
from src.db import insert_architect, insert_project, ensure_tables


def test_project_create_logs_event():
    ensure_tables()
    arch_id = f"arch_{uuid.uuid4().hex[:6]}"
    insert_architect({'id': arch_id, 'name': 'ArchLogger', 'email': f'{arch_id}@example.com', 'phone': None, 'company': 'LogCo', 'nif': 'NIF', 'created_at': datetime.utcnow().isoformat()})
    proj_id = f"proj_{uuid.uuid4().hex[:6]}"
    insert_project({'id': proj_id, 'title': 'Logger Test', 'architect_name': 'ArchLogger', 'architect_id': arch_id, 'area_m2': 120, 'max_height': 7.0, 'style': 'moderno', 'price': 120000, 'file_path': None, 'description': 'desc', 'created_at': datetime.utcnow().isoformat()})

    events = get_recent_events(limit=20)
    assert any(ev.get('event') == 'project_created' and ev.get('project_id') == proj_id for ev in events), 'Falta registro project_created en logs'
