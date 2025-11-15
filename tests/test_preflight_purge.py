"""Test preflight log retention purge (deletes logs >30 days)."""
import os
from pathlib import Path
from datetime import datetime, timedelta
from src.preflight import run_all

def test_purge_old_logs(tmp_path, monkeypatch):
    """Old rotated logs should be purged if older than 30 days."""
    # Setup fake logs directory
    fake_logs = tmp_path / 'logs'
    fake_logs.mkdir()
    # Create an old log (31 days ago)
    old_date = datetime.utcnow() - timedelta(days=31)
    old_name = f"app.log.{old_date.strftime('%Y%m%d_%H%M%S')}"
    (fake_logs / old_name).write_text('old', encoding='utf-8')
    # Create recent log (7 days ago)
    recent_date = datetime.utcnow() - timedelta(days=7)
    recent_name = f"app.log.{recent_date.strftime('%Y%m%d_%H%M%S')}"
    (fake_logs / recent_name).write_text('recent', encoding='utf-8')
    # Monkeypatch Path('logs') to use fake
    def fake_path(p):
        if p == 'logs':
            return fake_logs
        return Path(p)
    monkeypatch.setattr('src.preflight.Path', fake_path)
    # Run preflight
    report = run_all()
    # Verify old purged, recent kept
    assert old_name in report['log_retention']['purged']
    assert not (fake_logs / old_name).exists()
    assert (fake_logs / recent_name).exists()
