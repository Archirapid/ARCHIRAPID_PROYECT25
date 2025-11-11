# archirapid_extract — Pipeline de Extracción Catastral (MVP)

Este directorio contiene el pipeline completo para extraer datos de notas catastrales (PDF) y generar información edificatoria.

**Pipeline MVP (4 scripts):**
1. `extract_pdf.py` — Extrae texto e imágenes del PDF
2. `ocr_and_preprocess.py` — OCR y preprocesado de imagen
3. `vectorize_plan.py` — Detecta y vectoriza el lindero del plano
4. `compute_edificability.py` — Extrae superficie y calcula edificabilidad

---

## 📦 Instalación

### 1) Crear y activar entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Nota PowerShell:** Si tienes error de restricción de ejecución, ejecuta:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 2) Instalar dependencias Python

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Instalar dependencias del sistema

**Tesseract OCR** (REQUERIDO para OCR):
- **Windows:** 
  - Opción 1: `choco install tesseract` (si tienes Chocolatey)
  - Opción 2: Descarga de https://github.com/UB-Mannheim/tesseract/wiki
  - Añade al PATH: `C:\Program Files\Tesseract-OCR`
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt install tesseract-ocr tesseract-ocr-spa`

**Poppler** (OPCIONAL, solo si PyMuPDF falla):
- **Windows:** `choco install poppler`
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt install poppler-utils`

---

## 🚀 Uso del Pipeline

### Paso 1: Preparar el PDF
Coloca tu PDF de nota catastral en la carpeta `archirapid_extract/` con el nombre `Catastro.pdf`

### Paso 2: Ejecutar los scripts en orden

```powershell
# 1. Extraer PDF (genera page_*.png + extracted_text.txt)
python extract_pdf.py

# 2. Preprocesar imagen (genera page_1_processed.png + ocr_text.txt)
python ocr_and_preprocess.py

# 3. Vectorizar plano (genera plot_polygon.geojson + visualización)
python vectorize_plan.py

# 4. Calcular edificabilidad (genera edificability.json)
python compute_edificability.py
```

### Paso 3: Revisar resultados

Todos los outputs se guardan en `catastro_output/`:

```
catastro_output/
├── page_1.png                    # Imagen extraída del PDF
├── page_1_processed.png          # Imagen binarizada
├── extracted_text.txt             # Texto del PDF
├── ocr_text.txt                   # Texto OCR de la imagen
├── plot_polygon.geojson           # Polígono del lindero (píxeles)
├── contours_visualization.png     # Visualización de contornos detectados
├── edificability.json             # Superficie y edificabilidad
├── surface_candidates.json        # Candidatos de superficie detectados
├── process_summary.json           # Resumen del preprocesado
└── vectorization_summary.json     # Resumen de vectorización
```

---

## 🎯 Salida esperada

**edificability.json:**
```json
{
  "surface_m2": 450.0,
  "max_buildable_m2": 148.5,
  "edificability_percent": 33,
  "method": "auto_extraction_heuristic",
  "cadastral_ref": "1234567AB0001C0001AB"
}
```

**plot_polygon.geojson:**
```json
{
  "type": "Feature",
  "properties": {
    "source": "auto_vectorize",
    "area_px2": 125430.5,
    "vertices": 8
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[x1, y1], [x2, y2], ...]]
  }
}
```

---

## 🔍 Verificación y troubleshooting

### ✅ Verificar instalación de Tesseract
```powershell
tesseract --version
```

### ⚠️ Si OCR falla
- Verifica que Tesseract esté en el PATH
- Instala el paquete de idioma español: `tesseract-ocr-spa`
- El script continuará sin OCR si falla (solo usará texto directo del PDF)

### ⚠️ Si no encuentra superficie
- Revisa `extracted_text.txt` y `ocr_text.txt` manualmente
- Mira `surface_candidates.json` para ver qué valores detectó
- Edita `edificability.json` manualmente si es necesario

### ⚠️ Si no detecta contornos
- Revisa `contours_visualization.png` para ver qué se detectó
- La imagen procesada (`page_1_processed.png`) debe mostrar líneas blancas sobre fondo negro
- Ajusta parámetros de binarización en `ocr_and_preprocess.py` si es necesario

---

## 📝 Próximos pasos (Sprints futuros)

- **Sprint 5:** Generador paramétrico 2D (distribución de plantas)
- **Sprint 6:** Extrusión 3D y visor (gemelo digital)
- **Sprint 7:** Integración con IA para sugerencias automáticas

---

## 🛠️ Scripts auxiliares

- `setup_windows.ps1` — Script automatizado de instalación para Windows (ejecutar como admin)

---

**¿Listo para probar?** Ejecuta los comandos de instalación y luego prueba con un PDF catastral real.