import os, time
from pathlib import Path
from src.logger import log, get_recent_events

def test_log_rotation(tmp_path, monkeypatch):
    # Set very small max bytes to trigger rotation quickly
    monkeypatch.setenv('LOG_MAX_BYTES', '300')
    # Ensure log directory isolated (override FILE path temporarily)
    test_log = tmp_path / 'app.log'
    from src import logger as lg
    lg.FILE = test_log
    # Write many lines
    for i in range(200):
        log('test_event', idx=i)
    # Expect at least one rotated file
    rotated = list(tmp_path.glob('app.log.*'))
    assert rotated, 'No rotated log file created'
    # Recent events should parse some lines
    events = get_recent_events(limit=10)
    assert len(events) <= 10
    assert all(isinstance(e, dict) for e in events)
