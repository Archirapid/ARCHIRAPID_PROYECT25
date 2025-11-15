from src.utils_validation import html_safe

def test_html_safe_basic():
    assert html_safe('<script>') == '&lt;script&gt;'

def test_html_safe_quotes():
    assert html_safe('"x"') == '&quot;x&quot;'

def test_html_safe_none():
    assert html_safe(None) == ''
