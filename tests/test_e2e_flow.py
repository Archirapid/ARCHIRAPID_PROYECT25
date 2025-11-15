import uuid
from src.db import insert_plot, insert_project, get_all_plots, get_all_projects
from src.logger import log, get_recent_events, log_exceptions
from src.preflight import run_all

def test_preflight_environment():
    report = run_all()
    assert all(report['dirs'].values()), 'Missing required directory'
    assert report['files']['requirements.txt'], 'requirements.txt missing'
    assert report['db']['ok'], f"DB not OK: {report['db']}"
    assert all(report['write_perms'].values()), 'Write permission failure'

@log_exceptions
def _insert_dummy_records():
    pid = uuid.uuid4().hex
    plot = {
        'id': pid,
        'title': 'Test Finca',
        'description': 'Desc',
        'lat': 40.0,
        'lon': -3.0,
        'm2': 500,
        'height': 9.0,
        'price': 100000.0,
        'type': 'Urbano',
        'province': 'Madrid',
        'locality': 'Centro',
        'owner_name': 'Propietario',
        'owner_email': 'owner@example.com',
        'image_path': None,
        'registry_note_path': None,
        'created_at': '2025-11-15T00:00:00'
    }
    insert_plot(plot)
    proj = {
        'id': uuid.uuid4().hex,
        'title': 'Proyecto Demo',
        'architect_name': 'Arq',
        'area_m2': 120,
        'max_height': 9.0,
        'style': 'Moderno',
        'price': 150000.0,
        'file_path': None,
        'description': 'Proyecto',
        'created_at': '2025-11-15T00:00:00'
    }
    insert_project(proj)
    log('e2e_flow_insert', plot_id=pid, project_id=proj['id'])
    return pid, proj['id']

def test_e2e_flow_insertion_and_logging():
    plot_id, project_id = _insert_dummy_records()
    plots = get_all_plots()
    projects = get_all_projects()
    assert plot_id in plots['id'].tolist(), 'Plot not inserted'
    assert project_id in projects['id'].tolist(), 'Project not inserted'
    events = get_recent_events(limit=20)
    assert any(ev.get('event') == 'e2e_flow_insert' for ev in events), 'Log event missing'
