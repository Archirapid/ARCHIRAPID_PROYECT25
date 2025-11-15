import pytest

def test_stub_functions():
    from src.main import get_all_plots, insert_plot, save_file
    assert callable(get_all_plots)
    assert callable(insert_plot)
    assert callable(save_file)

def test_asset_manager_project_insert(tmp_path):
    from src.asset_manager import insert_project, get_all_projects
    # Insert dummy project
    pdata = {
        'id': 'TEST123',
        'title': 'Proyecto Test',
        'architect_name': 'Arq Demo',
        'area_m2': 100,
        'max_height': 9.0,
        'style': 'Moderno',
        'price': 120000.0,
        'file_path': None,
        'description': 'Demo',
        'created_at': '2025-11-15T00:00:00'
    }
    insert_project(pdata)
    df = get_all_projects()
    assert 'TEST123' in df['id'].tolist()
