# 🔄 Punto de Restauración – Diseñador Paramétrico Funcional

**Fecha:** 2025-11-13 18:47:57  
**Estado:** ✅ ESTABLE – Diseñador funcionando correctamente

## 📋 Descripción del Punto

Este punto de restauración captura el estado completo de la aplicación con:

- ✅ **Extracción catastral automática** (OCR + vectorización + edificabilidad)
- ✅ **Corrección automática de coherencia** (superficie + tipo de suelo)
- ✅ **Exportación DXF** funcional
- ✅ **Diseñador paramétrico 3D** completamente integrado
- ✅ **Visor 3D interactivo** (model-viewer GLB)
- ✅ **Presupuesto automático** basado en m² construidos
- ✅ **Persistencia de estado** (sin envío a inicio tras cambios de parámetros)
- ✅ **Caché de análisis** para evitar reprocesar tras reruns

## 🗂️ Archivos Respaldados

```
app.py.backup_20251113_184757
archirapid_extract/generate_design.py.backup_20251113_184757
archirapid_extract/export_dxf.py.backup_20251113_184757
```

## 🔧 Funcionalidad Verificada

### 1. Pipeline Catastral
- Carga PDF nota simple → Ejecuta extracción automática
- Genera métricas: superficie, edificabilidad, referencia catastral
- Valida edificabilidad según tipo de suelo
- Corrección automática cuando detecta píxel-area o tipo desconocido

### 2. Diseñador Paramétrico
- **Entradas:** Dormitorios (1-4), Plantas (1-3), Retranqueo (1-8m)
- **Salidas:**
  - Plano 2D PNG (distribución espacios)
  - Modelo 3D GLB (visualización interactiva)
  - Presupuesto estimado (€/m² + total)
- **Robustez:** Fallback automático a `edificability.json` si `validation_report.json` carece de `surface_m2`/`buildable_m2`

### 3. Persistencia de Estado
- Selección de finca se preserva entre reruns
- Resultado de análisis catastral guardado en `session_state.analysis_cache`
- Resultado de diseño guardado en `session_state.design_result`
- **No hay "cierre" ni regreso a inicio** al cambiar parámetros

## 🚨 Problemas Resueltos en Esta Versión

1. **❌ "Datos de superficie inválidos"**  
   → ✅ Fallback robusto lee `edificability.json` y calcula ratio si falta `buildable_m2`

2. **❌ Cierre de panel al pulsar "Generar Diseño"**  
   → ✅ Eliminados `st.rerun()` innecesarios; se usa session_state para persistir resultados

3. **❌ Cambiar dormitorios/plantas devuelve a inicio**  
   → ✅ Widgets con keys únicos; no hay forced reruns en cascada

4. **❌ Superficie en píxeles confundida con m²**  
   → ✅ Corrección automática sustituye valores irreales (>100k) por superficie registrada en BD

5. **❌ Fincas urbanas marcadas "NO EDIFICABLE"**  
   → ✅ Lógica de corrección fuerza `is_buildable=True` y `soil_type=URBANO` para plots registrados como `type='urban'`

## 📦 Dependencias Clave

- `streamlit` (UI interactiva)
- `folium` + `streamlit-folium` (mapa plots)
- `trimesh` (export GLB 3D)
- `matplotlib` + `shapely` (plano 2D + geometría)
- `ezdxf` (export DXF AutoCAD)
- `pytesseract` (OCR catastral)
- `opencv-python` (vectorización contornos)

## 🔄 Cómo Restaurar

Si necesitas volver a este estado estable:

```powershell
# Restaurar app principal
Copy-Item "app.py.backup_20251113_184757" "app.py" -Force

# Restaurar generador de diseño
Copy-Item "archirapid_extract\generate_design.py.backup_20251113_184757" "archirapid_extract\generate_design.py" -Force

# Restaurar exportador DXF
Copy-Item "archirapid_extract\export_dxf.py.backup_20251113_184757" "archirapid_extract\export_dxf.py" -Force

# Reiniciar servidor Streamlit
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
.\venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

## 📝 Notas Técnicas

### Flujo de Diseño Paramétrico

1. **Usuario pulsa "🚀 Generar Diseño"**
2. Se guarda intención en `session_state['design_requested']` con parámetros
3. Si no existe `design_result`, se ejecuta `build_project()` de `generate_design.py`
4. Se guarda resultado en `session_state['design_result']`
5. Se muestra plano, modelo 3D, presupuesto (sin necesidad de rerun)
6. Cambios posteriores de parámetros **no borran** el resultado hasta nuevo clic en botón

### Corrección Automática de Coherencia

```python
# 1. Si superficie parece ser píxeles (>100k) y tenemos valor real en BD
if surf > 100000 and 50 <= sel_surface_db <= 100000:
    edata['surface_m2'] = sel_surface_db

# 2. Si tipo de suelo es desconocido pero en BD es urbano
if soil == 'DESCONOCIDO' and plot_type == 'urban':
    vdata['soil_type'] = 'URBANO'
    vdata['is_buildable'] = True

# 3. Recalcular edificabilidad con superficie corregida
edata['max_buildable_m2'] = edata['surface_m2'] * ratio

# 4. Sincronizar validation_report.json para el diseñador
vdata['surface_m2'] = edata['surface_m2']
vdata['buildable_m2'] = edata['max_buildable_m2']
```

## ✅ Validaciones de QA

- [x] Finca urbana 10,000 m² genera diseño correctamente
- [x] Cambiar de 2 a 3 dormitorios no cierra panel
- [x] Cambiar de 1 a 2 plantas preserva preview
- [x] DXF descargable tras análisis
- [x] GLB descargable tras diseño
- [x] Presupuesto muestra cifras coherentes (900 €/m² base)
- [x] Modelo 3D rota con mouse/touch en viewer
- [x] Logs del pipeline accesibles en expander
- [x] Caché de análisis permite ver métricas sin reanalizar

---

**Creado automáticamente por:** GitHub Copilot  
**Commit recomendado:** `git commit -am "🔖 Restore point: Parametric designer fully functional"`
