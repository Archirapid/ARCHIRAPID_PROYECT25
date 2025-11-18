import io
from app import render_create_project_page


def test_memoria_field_present_in_code():
    # Quick static check that the code contains the memoria field key
    import inspect
    source = inspect.getsource(render_create_project_page)
    assert 'Memoria Técnica' in source or 'Memoria Técnica (PDF)' in source
    # Ensure full page create also contains habitaciones input and parcela inputs
    assert 'Dormitorios' in source or 'Habitaciones' in source
    assert 'Parcela mínima' in source or 'Parcela Mínima' in source
    # Check that full page offers modelo 3D upload
    assert 'Modelo 3D' in source or '.glb' in source
    # Ensure project detail allows subir planos y memoria
    from app import show_project_detail_modal
    source2 = inspect.getsource(show_project_detail_modal)
    assert 'Subir / Reemplazar Planos PDF' in source2 or 'Subir / Reemplazar Planos' in source2
    assert 'Subir / Reemplazar Memoria' in source2 or 'Subir / Reemplazar Memoria Técnica' in source2
    assert 'Modelo 3D' in source2 or 'Subir / Reemplazar Modelo 3D' in source2
