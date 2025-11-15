from src.logger import log, get_recent_events

def test_get_recent_events_limit():
    # Generate some events
    for i in range(15):
        log('evt_test', idx=i, level='DEBUG')
    evs5 = get_recent_events(limit=5)
    assert len(evs5) <= 5
    evs10 = get_recent_events(limit=10)
    assert len(evs10) <= 10
    # Ensure ordering: last events appear (simple check by idx presence of final value)
    last_idxs = [e.get('idx') for e in evs5 if 'idx' in e]
    assert any(idx == 14 for idx in last_idxs) or any(idx == 13 for idx in last_idxs)
