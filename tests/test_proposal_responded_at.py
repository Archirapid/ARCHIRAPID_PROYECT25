import uuid
from datetime import datetime
from src.db import insert_plot, insert_proposal, update_proposal_status, get_proposals_for_plot, ensure_tables

def test_responded_at_set():
    ensure_tables()
    plot_id = f"plot_{uuid.uuid4().hex[:6]}"
    insert_plot({
        'id': plot_id,
        'title': 'Finca responded',
        'description': 'Desc',
        'lat': 0.0,
        'lon': 0.0,
        'm2': 600,
        'height': 9.0,
        'price': 100000.0,
        'type': 'Urbano',
        'province': 'Madrid',
        'locality': 'Centro',
        'owner_name': 'Owner',
        'owner_email': 'owner@test.com',
        'image_path': None,
        'registry_note_path': None,
        'created_at': datetime.utcnow().isoformat(),
        'address': None,
        'owner_phone': None
    })
    proposal_id = f"prop_{uuid.uuid4().hex[:6]}"
    insert_proposal({
        'id': proposal_id,
        'plot_id': plot_id,
        'architect_id': 'arch_test',
        'project_id': None,
        'message': 'Propuesta test responded_at',
        'price': 45000.0,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat()
    })
    update_proposal_status(proposal_id, 'accepted')
    df = get_proposals_for_plot(plot_id)
    row = df[df['id'] == proposal_id].iloc[0]
    assert row['status'] == 'accepted'
    assert 'responded_at' in df.columns
    assert row['responded_at'] is not None
