import ast
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
BACKUP = ROOT / "backups" / "app.py.backup_20251118_120001"


def test_backup_exists_and_is_nonempty():
    assert BACKUP.exists(), f"Backup file {BACKUP} missing"
    assert BACKUP.stat().st_size > 100, "Backup file is unexpectedly small"


def _has_st_button_in_with_form(tree: ast.AST, form_attr_name: str='form'):
    """Scan AST to find 'with st.form(...)' nodes and check if any call to 'st.button' is inside such with bodies."""
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            # for each with item, determine if context manager is st.form
            for item in node.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call) and isinstance(ctx.func, ast.Attribute):
                    if getattr(ctx.func.value, 'id', None) == 'st' and ctx.func.attr == form_attr_name:
                        # check body for any call to st.button
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                                if getattr(child.func.value, 'id', None) == 'st' and child.func.attr == 'button':
                                    return True
    return False


def test_no_st_button_inside_create_form_in_app():
    content = APP.read_text(encoding='utf-8')
    tree = ast.parse(content)
    assert not _has_st_button_in_with_form(tree), "Found st.button inside a st.form in app.py — this triggers StreamlitAPIException"


def test_last_created_project_flag_present():
    content = APP.read_text(encoding='utf-8')
    assert 'last_created_project' in content, "Expected 'last_created_project' to exist in app.py after the fix"


def test_cache_cleared_after_insert():
    content = APP.read_text(encoding='utf-8')
    assert 'get_all_projects_cached.clear' in content or 'get_all_projects_cached.clear()' in content, "Missing cache invalidation call after project insert"
