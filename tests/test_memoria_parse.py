from archirapid_extract.parse_project_memoria import parse_memoria_text


def test_parse_budget_and_time_and_visado():
    sample = (
        "Presupuesto estimado: 75.000 €\n"
        "Plazo de ejecución aproximado: 6 meses\n"
        "Visado colegial: 1.200 €\n"
        "Memoria de calidades: Acabados de alta gama con madera y cerámica."
    )
    meta = parse_memoria_text(sample)
    assert meta['budget'] is not None and '€' in meta['budget']
    assert '6' in meta['execution_time']
    assert meta['visado'] is not None and '€' in meta['visado']
    assert 'Memoria de calidades' in meta['calidades'] or 'calidades' in meta['calidades'].lower()


def test_parse_no_data_returns_none_values():
    meta = parse_memoria_text('')
    assert meta['budget'] is None
    assert meta['execution_time'] is None
    assert meta['visado'] is None


def test_parse_area_and_rooms_and_others():
    sample = (
        "Superficie construida: 180 m2\n"
        "Habitaciones: 5\n"
        "Baños: 3\n"
        "Plantas: 2\n"
        "Garaje: 1\n"
    )
    meta = parse_memoria_text(sample)
    # area should be detected
    assert meta.get('area_m2') is not None
    assert '180' in str(meta.get('area_m2'))
    assert meta.get('habitaciones') == '5'
    assert meta.get('banos') == '3'
    assert meta.get('plantas') == '2'
    assert meta.get('garaje') == '1'


def test_extract_and_save_metadata_pdf(tmp_path):
    # Create a tiny PDF with budget text using reportlab
    from archirapid_extract.parse_project_memoria import extract_and_parse_memoria
    from reportlab.pdfgen import canvas

    pdf_file = tmp_path / "sample_memoria.pdf"
    c = canvas.Canvas(str(pdf_file))
    c.drawString(100, 750, "Presupuesto: 50 €")
    c.save()

    project_id = 'testpid123'
    meta = extract_and_parse_memoria(str(pdf_file), project_id)
    assert meta.get('budget') is not None

    meta_path = pdf_file.with_name(f"{project_id}_memoria.json")
    assert meta_path.exists()
    import json
    loaded = json.loads(meta_path.read_text(encoding='utf-8'))
    assert loaded.get('budget') == meta.get('budget')