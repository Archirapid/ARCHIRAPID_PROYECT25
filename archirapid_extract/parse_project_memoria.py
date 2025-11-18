import re
import json
from pathlib import Path
from typing import Dict, Optional

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using PyMuPDF (fitz) if available, otherwise fallback to pdfplumber.

    Returns a string with the full extracted text.
    """
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(pdf_path)

    text_out = []
    try:
        import fitz  # pymupdf
        doc = fitz.open(str(p))
        for page in doc:
            text_out.append(page.get_text("text") or "")
        return "\n\n".join(text_out)
    except Exception:
        # fallback to pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(str(p)) as pdf:
                for page in pdf.pages:
                    text_out.append(page.extract_text() or "")
            return "\n\n".join(text_out)
        except Exception as e:
            # If all fallbacks fail, raise
            raise RuntimeError(f"Failed to extract PDF text: {e}")


def parse_memoria_text(text: str) -> Dict[str, Optional[str]]:
    """Simple heuristic parser for memoria text.

    Extracts: presupuesto/budget, visado (boolean or fee), memoria_de_calidades snippet, execution_time.
    The function returns a dict with keys budget, visado, calidades, execution_time.
    """
    out = {
            'budget': None,
            'visado': None,
            'calidades': None,
            'execution_time': None,
            'area_m2': None,
            'habitaciones': None,
            'banos': None,
            'plantas': None,
            'garaje': None
        }
    if not text:
        return out

    # Normalize spaces
    t = re.sub(r"\s+", " ", text)

    # Budget extraction simple heuristics (look for 'presupuesto' followed by an amount)
    budget_re = re.search(r"(presupuest[oa]|estimad[oa] de presupuesto|coste|precio).*?([€\d\.,]{2,}\s*(?:€|EUR|euros)?)",
                          t, re.I)
    if budget_re:
        out['budget'] = budget_re.group(2).strip()
    else:
        # find first monetary amount in text
        m = re.search(r"([€\d]{1}[\d\.,\s]+)(?:€|EUR|euros)?", t)
        if m:
            out['budget'] = m.group(0).strip()

    # Visa/visado
    visado_match = re.search(r"\bvisad[oa]\b|\bvisa\b|visado colegial", t, re.I)
    if visado_match:
        out['visado'] = 'sí'
        # search for nearest currency after the visado keyword
        after = t[visado_match.end():visado_match.end() + 120]
        fee_match = re.search(r"([0-9][\d\.,\s]*(?:€|EUR|euros)?)", after, re.I)
        if fee_match:
            out['visado'] = fee_match.group(1).strip()

    # Execution time (plazo de ejecución, duración, plazos)
    time_re = re.search(r"(plazo de ejecu[c|t]i[oó]n|duraci[oó]n|plazo).*?([0-9]+\s*(meses?|m[eé]ses|semanas?|d[ií]as?|a[nñ]os?))",
                        t, re.I)
    if time_re:
        out['execution_time'] = time_re.group(2).strip()

    # Memoria de calidades: find snippet
    cal_re = re.search(r"(memoria de calidades|calidades technicas|calidades).*?(?=\.|,|\n)" , t, re.I)
    if cal_re:
        out['calidades'] = cal_re.group(0).strip()

    # Spec heuristics: area, habitaciones, banos, plantas, garaje
    area_re = re.search(r"([0-9]{2,5}(?:[\.,][0-9]{1,3})?)\s*(m2|m²|metros cuadrados|m cuadrados|m2 construidos|m² construidos)", t, re.I)
    if area_re:
        out['area_m2'] = area_re.group(1).replace(',', '.').strip()

    hab_re = re.search(r"(habitacion|hab\.|dormitorio|dorms?).{0,20}?([0-9]{1,2})", t, re.I)
    if hab_re:
        out['habitaciones'] = hab_re.group(2)

    ban_re = re.search(r"(ba[ñn]o|ban[óo]s|baños|wc|aseo).{0,20}?([0-9]{1,2})", t, re.I)
    if ban_re:
        out['banos'] = ban_re.group(2)

    plantas_re = re.search(r"(plantas|pisos).{0,20}?([0-9]{1,2})", t, re.I)
    if plantas_re:
        out['plantas'] = plantas_re.group(2)

    garaje_re = re.search(r"(garaje|plazas de garaje|parking).{0,20}?([0-9]{1,2})", t, re.I)
    if garaje_re:
        out['garaje'] = garaje_re.group(2)

    return out


def extract_and_parse_memoria(pdf_path: str, project_id: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Run full pipeline: extract text then parse with heuristics and save result to JSON.

    The resulting JSON is saved next to the PDF as <basename>_memoria.json or <project_id>_memoria.json.
    The function returns the parsed metadata dict.
    """
    pdf_p = Path(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    metadata = parse_memoria_text(text)

    # build metadata file path
    if project_id:
        meta_fn = f"{project_id}_memoria.json"
    else:
        meta_fn = pdf_p.stem + "_memoria.json"
    meta_path = pdf_p.with_name(meta_fn)
    try:
        meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        # best effort to save
        raise RuntimeError(f"Could not save memoria metadata: {e}")
    return metadata


def extract_and_parse_memoria_and_map_fields(pdf_path: str, project_id: Optional[str] = None) -> Dict[str, Optional[str]]:
    """Deprecated: convenience wrapper to return typed fields for DB mapping (kept for backwards compatibility).

    Use extract_and_parse_memoria() and externally map to DB fields.
    """
    return extract_and_parse_memoria(pdf_path, project_id)
