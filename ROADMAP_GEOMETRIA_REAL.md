# 🗺️ ROADMAP: Geometría Real de Finca (FASE 2)

**Fecha**: 2025-11-14  
**Estado**: PENDIENTE - No implementar hasta validación MVP  
**Prioridad**: MEDIA (Feature de mejora, no crítica)

---

## 📸 CONTEXTO

Se ha identificado que el plano catastral oficial (verde) muestra geometría irregular de fincas (esquinas, entrantes, salientes), mientras que nuestro sistema actual vectoriza solo el contorno rectangular aproximado.

**Referencia visual**: `uploads/Plano_Finca_Catastral.png`

---

## 🎯 OBJETIVO FUTURO

Permitir que el diseño paramétrico se ajuste a la geometría REAL de la finca para:
- Aprovechar esquinas/irregularidades
- Posicionamiento manual del edificio
- Sugerencias IA de placement óptimo
- Validación precisa de retranqueos

---

## 🛠️ IMPLEMENTACIÓN PROPUESTA

### Fase 2.1: Vectorización Avanzada
**Archivo**: `archirapid_extract/vectorize_plan_advanced.py`

```python
# Detección multi-capa por color:
# - Verde catastral → geometría real finca
# - Líneas rojas → retranqueos normativos
# - Áreas sombreadas → edificabilidad oficial

def detect_plot_by_color(image_path):
    """
    Segmentación HSV para aislar polígono verde catastral.
    Exportar múltiples capas en GeoJSON.
    """
    # TODO: Implementar cuando se priorice
```

### Fase 2.2: Editor Interactivo
**Archivo**: `app.py` - Nueva sección "Editor de Diseño"

```python
# Integración Leaflet.Draw o Folium.Draw
# Permitir arrastrar/rotar rectángulo del edificio
# Validación en tiempo real de normativa
```

### Fase 2.3: Motor de Sugerencias
**Archivo**: `archirapid_extract/placement_optimizer.py`

```python
# Algoritmo de optimización para sugerir N mejores posiciones
# Criterios: aprovechamiento, orientación, retranqueos
```

---

## ⚖️ ANÁLISIS COSTE-BENEFICIO

| Aspecto | Impacto | Esfuerzo | Prioridad |
|---------|---------|----------|-----------|
| Vectorización por color | Alto | Medio (6h) | Media |
| Editor interactivo | Muy Alto | Alto (2 días) | Alta* |
| Sugerencias IA | Medio | Medio (8h) | Baja |

*Alta solo si clientes lo demandan en validación

---

## 🚫 DECISIÓN ACTUAL

**NO IMPLEMENTAR** hasta:
1. Validar MVP con clientes reales
2. Recibir feedback sobre necesidad de ajuste manual
3. Completar features críticas del roadmap principal
4. Estabilizar pipeline actual completamente

---

## 📌 NOTAS TÉCNICAS

- **Riesgo de regresión**: Modificar `vectorize_plan.py` afecta toda la cadena
- **MVP suficiente**: Aproximación rectangular funciona para demostración
- **Mantenibilidad**: Implementar cuando haya recursos dedicados

---

## 🔗 ARCHIVOS RELACIONADOS

- `archirapid_extract/vectorize_plan.py` (actual)
- `archirapid_extract/generate_design.py` (actual)
- `uploads/Plano_Finca_Catastral.png` (referencia visual)

---

**Autor**: Sistema de análisis técnico  
**Revisión**: Pendiente tras roadmap completo
