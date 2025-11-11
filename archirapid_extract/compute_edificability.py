# compute_edificability.py
import re
from pathlib import Path
import json
import sys

IN_DIR = Path("catastro_output")
txtf = IN_DIR / "extracted_text.txt"

# Validate input
if not IN_DIR.exists():
    print(f"❌ ERROR: Directorio no encontrado: {IN_DIR.absolute()}")
    print("   Ejecuta primero 'extract_pdf.py'")
    sys.exit(1)

if not txtf.exists():
    print(f"⚠️  Archivo {txtf} no encontrado, intentando con ocr_text.txt...")
    txtf = IN_DIR / "ocr_text.txt"
    if not txtf.exists():
        print(f"❌ ERROR: No se encontró texto extraído.")
        print("   Ejecuta primero 'extract_pdf.py' y 'ocr_and_preprocess.py'")
        sys.exit(1)

print(f"📊 Analizando texto de: {txtf}")
text = txtf.read_text(encoding="utf-8")

if len(text.strip()) < 10:
    print("⚠️  Texto extraído muy corto. El PDF puede estar vacío o ser solo imagen.")

# Heurística mejorada: buscar 'superficie' con variantes comunes en catastrales españoles
# IMPORTANTE: re.DOTALL permite que \s incluya saltos de línea
patterns = [
    # Superficie gráfica PARCELA (formato catastral español con salto de línea)
    r"superficie\s+gr[aá]fica\s+parcela\s*\[?m[2²]?\]?\s*([0-9\.,]+)",
    
    # Superficie gráfica (más común en notas catastrales)
    r"superficie\s+gr[aá]fica\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    r"sup\.\s*gr[aá]fica\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    
    # Superficie genérica
    r"superficie\s+(?:de\s+)?(?:la\s+)?(?:parcela|finca|terreno|solar)\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    r"superficie\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    r"sup\.\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    
    # Área/parcela
    r"(?:área|parcela|terreno|solar)\s*[:\s]*([0-9\.,]+)\s*m[2²]?",
    
    # Solo número con m² (menos específico, puede dar falsos positivos)
    r"([0-9]{3,5}[.,]?[0-9]{0,2})\s*m[2²]"
]

candidates = []
for pat in patterns:
    # Use re.DOTALL to allow \s to match newlines
    for m in re.finditer(pat, text, flags=re.IGNORECASE | re.DOTALL):
        val_str = m.group(1)
        # FIXED: Normalize Spanish number format correctly
        # Spanish uses: punto (.) como separador de miles, coma (,) como decimal
        # Ejemplo: "26.721" es 26mil, "26,721" es 26.721
        # Estrategia: si tiene punto Y coma, quitar puntos. Si solo punto, verificar contexto
        
        val_cleaned = val_str.strip()
        
        # Caso 1: tiene punto y coma (ej: "1.234,56") -> miles + decimal español
        if '.' in val_cleaned and ',' in val_cleaned:
            val_normalized = val_cleaned.replace(".", "").replace(",", ".")
        # Caso 2: solo coma (ej: "1234,56") -> decimal español
        elif ',' in val_cleaned:
            val_normalized = val_cleaned.replace(",", ".")
        # Caso 3: solo punto - ambiguo. Heurística: si tiene 3+ dígitos antes del punto, es miles
        elif '.' in val_cleaned:
            parts = val_cleaned.split('.')
            # Si último grupo tiene exactamente 3 dígitos, probablemente es separador de miles
            if len(parts) == 2 and len(parts[1]) == 3:
                val_normalized = val_cleaned.replace(".", "")
            else:
                # Probablemente es decimal (ej: "123.45")
                val_normalized = val_cleaned
        else:
            # Sin separadores
            val_normalized = val_cleaned
            
        try:
            val = float(val_normalized)
            # Filter unrealistic values (typical urban plot: 50-50000 m²)
            if 50 < val < 50000:
                candidates.append({
                    "value": val,
                    "pattern": pat[:50],
                    "match": m.group(0)
                })
        except ValueError:
            continue

# Extract cadastral reference (varios formatos posibles)
catastral_ref = None
ref_patterns = [
    r"REFERENCIA\s+CATASTRAL[^\n]*\n\s*([0-9A-Z]{14,20})",  # Con salto de línea (formato PDF)
    r"\b([0-9]{7}[A-Z]{2}[0-9]{4}[A-Z]{1}[0-9]{4}[A-Z]{2})\b",  # Formato estándar 20 chars
    r"(?:referencia\s+catastral|ref\.?\s*catastral)[:\s]*([0-9A-Z]{14,20})",  # Con prefijo inline
]
for ref_pat in ref_patterns:
    ref_match = re.search(ref_pat, text, re.IGNORECASE | re.MULTILINE)
    if ref_match:
        catastral_ref = ref_match.group(1).strip()
        print(f"  ✓ Referencia catastral encontrada: {catastral_ref}")
        break

# Choose most likely candidate
found = None
if candidates:
    # Remove duplicates
    unique_vals = {}
    for c in candidates:
        if c["value"] not in unique_vals:
            unique_vals[c["value"]] = c
    
    candidates = list(unique_vals.values())
    
    print(f"  ✓ Encontrados {len(candidates)} candidatos de superficie:")
    for i, c in enumerate(candidates[:5], 1):
        print(f"    {i}. {c['value']:.2f} m² (patrón: '{c['match']}')")
    
    # Prefer the first match from most specific patterns (top of patterns list)
    # or the most common value if there are multiple matches
    if len(candidates) == 1:
        found = candidates[0]["value"]
        print(f"  ✓ Superficie seleccionada: {found:.2f} m²")
    else:
        # Count occurrences
        value_counts = {}
        for c in candidates:
            value_counts[c["value"]] = value_counts.get(c["value"], 0) + 1
        
        # Most common value
        most_common = max(value_counts.items(), key=lambda x: x[1])
        found = most_common[0]
        print(f"  ✓ Superficie seleccionada (más común): {found:.2f} m² (aparece {most_common[1]} veces)")

if found is None:
    print("⚠️  No se encontró superficie automáticamente.")
    print("   Revisa 'extracted_text.txt' y proporciona el valor manualmente.")
    data = {
        "surface_m2": None,
        "max_buildable_m2": None,
        "edificability_percent": 33,
        "method": "failed_auto_extraction",
        "cadastral_ref": catastral_ref
    }
else:
    max_buildable = found * 0.33
    data = {
        "surface_m2": round(found, 2),
        "max_buildable_m2": round(max_buildable, 2),
        "edificability_percent": 33,
        "method": "auto_extraction_heuristic",
        "candidates_found": len(candidates),
        "cadastral_ref": catastral_ref
    }
    print(f"✅ Superficie de parcela: {found:.2f} m²")
    print(f"✅ Máximo edificable (33%): {max_buildable:.2f} m²")

# Save results
output_file = IN_DIR / "edificability.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Cálculo guardado en: {output_file}")

# Also save all candidates for manual review
if candidates:
    candidates_file = IN_DIR / "surface_candidates.json"
    with open(candidates_file, "w", encoding="utf-8") as f:
        json.dump({"candidates": candidates, "selected": found}, f, indent=2, ensure_ascii=False)
    print(f"📋 Todos los candidatos guardados en: {candidates_file}")
