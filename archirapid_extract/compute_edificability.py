# compute_edificability.py - Enhanced validation and report generation
# -*- coding: utf-8 -*-
import re
import json
from pathlib import Path
import sys
from typing import Optional
from functools import lru_cache

try:
    from shapely.geometry import shape, Polygon
except Exception:
    # shapely debería estar en requirements; si falla seguimos sin cálculo geométrico
    shape = None

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

IN_DIR = Path("catastro_output")
OCR_FILE = IN_DIR / "ocr_text.txt"
EXTRACTED_FILE = IN_DIR / "extracted_text.txt"
GEOJSON_CANDIDATES = [IN_DIR / "plot_polygon.geojson", IN_DIR / "parcel_vector.json", IN_DIR / "plot.geojson"]
OUT_EDIFIC = IN_DIR / "edificability.json"        # back-compat
OUT_VALID_JSON = IN_DIR / "validation_report.json"
OUT_VALID_TXT = IN_DIR / "validation_report.txt"

DEFAULT_EDIFICABILITY_PERCENT = 0.33  # default 33%


def read_text_file(p: Path) -> Optional[str]:
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def find_geojson() -> Optional[Path]:
    for p in GEOJSON_CANDIDATES:
        if p.exists():
            return p
    return None


def parse_surface_from_ocr(text: str) -> Optional[float]:
    if not text:
        return None
    patterns = [
        r"superficie\s*(?:gr[aá]fica|gr[aá]fica\s*parcela|total)?\s*[:\-]?\s*([0-9\.,]+)\s*m",
        r"sup\.?\s*[:\-]?\s*([0-9\.,]+)\s*m",
        r"([0-9]{2,6}[\.,]?[0-9]{0,3})\s*m[2²]?",
    ]
    candidates = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE | re.DOTALL):
            s = m.group(1)
            s = s.strip()
            # Normalize Spanish numbers
            if '.' in s and ',' in s:
                s = s.replace('.', '').replace(',', '.')
            elif ',' in s:
                s = s.replace(',', '.')
            else:
                # keep dots as decimals unless looks like thousands
                parts = s.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    s = s.replace('.', '')
            try:
                v = float(s)
                if 1.0 < v < 1000000:
                    candidates.append(v)
            except Exception:
                continue
    if not candidates:
        return None
    # choose most common or largest
    from collections import Counter

    cnt = Counter(candidates)
    most_common = cnt.most_common(1)[0][0]
    return float(most_common)


def extract_cadastral_ref(text: str) -> Optional[str]:
    if not text:
        return None
    ref_patterns = [
        r"REFERENCIA\s+CATASTRAL[^\n]*\n\s*([0-9A-Z\-]{10,30})",
        r"referencia\s*catastral[:\s]*([0-9A-Z\-]{10,30})",
        r"(\b[0-9]{14,20}\b)",
    ]
    for pat in ref_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).strip()
    return None


def detect_soil_type(text: str) -> str:
    if not text:
        return "DESCONOCIDO"
    if re.search(r"urbano|urban(o)?", text, flags=re.IGNORECASE):
        return "URBANO"
    if re.search(r"r[uú]stico|rustico", text, flags=re.IGNORECASE):
        return "RUSTICO"
    if re.search(r"industrial", text, flags=re.IGNORECASE):
        return "INDUSTRIAL"
    return "DESCONOCIDO"


def detect_access(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r"acceso|vial|carretera|camino|acceso rodado|vía pública", text, flags=re.IGNORECASE))


def detect_linderos(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r"lindero|linderos|colindante|limite|límite|colindantes", text, flags=re.IGNORECASE))


def area_from_geojson(geojson_path: Path) -> Optional[float]:
    try:
        data = json.loads(geojson_path.read_text(encoding='utf-8'))
        # try common property names
        props = None
        if isinstance(data, dict) and 'features' in data:
            feat = data['features'][0]
            props = feat.get('properties', {})
            geom = feat.get('geometry')
        elif isinstance(data, dict) and 'geometry' in data:
            props = data.get('properties', {})
            geom = data.get('geometry')
        else:
            # try treat as geometry directly
            geom = data.get('geometry') if isinstance(data, dict) else None

        # priority: explicit area property
        if props:
            for key in ('area_m2', 'area', 'surface_m2', 'area_px'):
                if key in props:
                    try:
                        val = float(props[key])
                        # if area_px is present, treat as pixels (we won't convert)
                        if key == 'area_px':
                            return None
                        return val
                    except Exception:
                        pass

        # fallback: compute area by geometry if shapely available
        if geom and shape is not None:
            poly = shape(geom)
            # if coordinates in degrees or arbitrary units, we can't ensure meters.
            # we'll return area numeric value and mark source as 'geojson_geom'
            return float(poly.area)

    except Exception:
        return None
    return None


@lru_cache(maxsize=1)
def build_report():
    # Read text
    text = read_text_file(EXTRACTED_FILE) or read_text_file(OCR_FILE) or ''

    geojson = find_geojson()
    geo_area = area_from_geojson(geojson) if geojson else None

    surface_m2 = parse_surface_from_ocr(text)
    cadastral_ref = extract_cadastral_ref(text)
    soil_type = detect_soil_type(text)
    access = detect_access(text)
    linderos = detect_linderos(text)

    issues = []

    # Decide surface source
    surface_source = None
    if geo_area and surface_m2 is None:
        surface_m2 = geo_area
        surface_source = 'geojson_geom'
    elif surface_m2 is not None:
        surface_source = 'ocr'
    elif geo_area is not None:
        surface_source = 'geojson_geom'

    if surface_m2 is None:
        issues.append('Superficie no detectada (OCR/GeoJSON).')

    # Determine buildability
    is_buildable = False
    edificability_percent = DEFAULT_EDIFICABILITY_PERCENT
    if soil_type == 'URBANO':
        is_buildable = True
        # keep default 33% but allow future rules
    elif soil_type == 'INDUSTRIAL':
        is_buildable = True
        edificability_percent = 0.5
    else:
        # rústico or desconocido -> not buildable by default
        is_buildable = False

    if not access:
        issues.append('No se detecta acceso vial en la nota.')
    if not cadastral_ref:
        issues.append('Referencia catastral ausente.')
    if not linderos:
        issues.append('No se encuentran menciones a linderos/colindantes.')

    max_buildable = None
    if surface_m2 is not None:
        max_buildable = round(surface_m2 * edificability_percent, 2)

    report = {
        'cadastral_ref': cadastral_ref,
        'soil_type': soil_type,
        'surface_m2': round(surface_m2, 2) if surface_m2 is not None else None,
        'surface_source': surface_source,
        'edificability_percent': edificability_percent,
        'max_buildable_m2': max_buildable,
        'access_detected': bool(access),
        'linderos_mentioned': bool(linderos),
        'is_buildable': bool(is_buildable and surface_m2 is not None and access),
        'issues': issues,
        'method': 'enhanced_validation_v1',
    }

    # Maintain backward-compatible edificability.json
    edific = {
        'surface_m2': report['surface_m2'],
        'max_buildable_m2': report['max_buildable_m2'],
        'edificability_percent': report['edificability_percent'],
        'method': report['method'],
        'cadastral_ref': report['cadastral_ref']
    }

    # Write outputs
    OUT_EDIFIC.write_text(json.dumps(edific, indent=2, ensure_ascii=False), encoding='utf-8')
    OUT_VALID_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    # Human readable summary
    issues_txt = '\n- '.join(report['issues']) if report['issues'] else 'Ninguna'
    summary = f"""
VALIDACIÓN DE FINCA
-------------------
Referencia: {report['cadastral_ref']}
Tipo de suelo: {report['soil_type']}
Superficie (m²): {report['surface_m2']}
Fuente superficie: {report['surface_source']}
Edificabilidad aplicada: {int(report['edificability_percent']*100)} %
Máximo edificable (m²): {report['max_buildable_m2']}
Acceso detectado: {'Sí' if report['access_detected'] else 'No'}
Linderos mencionados: {'Sí' if report['linderos_mentioned'] else 'No'}
Construible: {'✅ Sí' if report['is_buildable'] else '❌ No'}

Observaciones:
- {issues_txt}
""".strip()

    OUT_VALID_TXT.write_text(summary, encoding='utf-8')

    print('✅ validation_report.json guardado en:', OUT_VALID_JSON)
    print('✅ validation_report.txt guardado en:', OUT_VALID_TXT)


if __name__ == '__main__':
    if not IN_DIR.exists():
        print(f"❌ ERROR: Directorio no encontrado: {IN_DIR.absolute()}")
        sys.exit(1)
    build_report()
