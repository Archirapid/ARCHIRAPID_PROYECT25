import zipfile
from pathlib import Path
from scripts.normalize_glb_paths import normalize
from app import extract_glb_from_zip, UPLOADS


def test_extract_glb_from_zip(tmp_path):
    # Create a fake glb file
    glb = tmp_path / "test_model.glb"
    glb.write_bytes(b"glbheader" + b"\x00" * 100)

    # Create a zip containing the glb
    zip_path = tmp_path / "pack.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(glb, arcname="test_model.glb")

    # call extract_glb_from_zip
    extracted = extract_glb_from_zip(str(zip_path), dest_dir=str(tmp_path))
    assert extracted is not None
    assert Path(extracted).exists()
    assert Path(extracted).suffix == '.glb'
    # Re-run extraction to simulate idempotence
    extracted2 = extract_glb_from_zip(str(zip_path), dest_dir=str(tmp_path))
    assert extracted2 is not None


def test_extract_glb_from_nested_zip(tmp_path):
    # Create glb and zip inside folder
    inner_glb = tmp_path / 'inner' / 'test_model.glb'
    inner_glb.parent.mkdir(parents=True, exist_ok=True)
    inner_glb.write_bytes(b'glbheader' + b'\x00' * 100)

    inner_zip = tmp_path / 'inner.zip'
    with zipfile.ZipFile(inner_zip, 'w') as z:
        z.write(inner_glb, arcname='test_model.glb')

    outer_zip = tmp_path / 'outer.zip'
    with zipfile.ZipFile(outer_zip, 'w') as z:
        z.write(inner_zip, arcname='AR-Code-1637477629846.zip')

    res = extract_glb_from_zip(str(outer_zip), dest_dir=str(tmp_path))
    assert res is not None
    assert Path(res).exists()


def test_no_glb_in_zip(tmp_path):
    # zip without glb
    txt = tmp_path / "file.txt"
    txt.write_text('hello')
    zip_path = tmp_path / "pack2.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(txt, arcname='file.txt')

    assert extract_glb_from_zip(str(zip_path), dest_dir=str(tmp_path)) is None


def test_extract_glb_from_misnamed_inner_glb(tmp_path):
    # A zip that contains a file named *.zip but which is actually a GLB
    glb_bytes = b'glTF' + b'\x00' * 100

    outer_zip = tmp_path / 'outer_misnamed.zip'
    with zipfile.ZipFile(outer_zip, 'w') as z:
        z.writestr('AR-Code-1637477629846.zip', glb_bytes)

    res = extract_glb_from_zip(str(outer_zip), dest_dir=str(tmp_path))
    assert res is not None
    assert Path(res).exists()
    assert Path(res).suffix == '.glb'


def test_inspect_zip_for_misnamed(tmp_path):
    # Create a zip containing a member named .zip but which is a glb
    import zipfile
    from app import _inspect_zip_for_glb

    bs = b'glTF' + b'\x00' * 100
    zpath = tmp_path / 'pack.zip'
    with zipfile.ZipFile(zpath, 'w') as z:
        z.writestr('AR-Code-123.zip', bs)

    diag = _inspect_zip_for_glb(str(zpath))
    assert diag['found_misnamed_zip'] == ['AR-Code-123.zip']
