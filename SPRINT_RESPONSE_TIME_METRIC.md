# Sprint: Métrica Tiempo de Respuesta en Propuestas

**Fecha:** 2025-11-17  
**Punto de Restauración Previo:** RESTAURACIONDOMINGO2

## Objetivo
Añadir visualización del tiempo transcurrido entre el envío de una propuesta (`created_at`) y su respuesta (`responded_at`) para propuestas aceptadas o rechazadas.

## Implementación Realizada

### 1. Vista de Propietario (Panel Home - Preview Finca)
**Archivo:** `app.py` líneas ~1938-1975  
**Cambios:**
- Añadido cálculo de delta temporal para propuestas aceptadas
- Añadido cálculo de delta temporal para propuestas rechazadas
- Formato inteligente: muestra horas si < 24h, días si >= 24h
- Display: `⏱️ Tiempo de respuesta: X.X horas` o `X día(s)`

### 2. Vista de Arquitecto (Portal Arquitectos - Mis Propuestas)
**Archivo:** `app.py` líneas ~2831-2850  
**Cambios:**
- Añadido cálculo de delta temporal para propuestas no-pendientes
- Mismo formato inteligente que vista propietario
- Permite al arquitecto ver cuánto tardó el propietario en responder

### 3. Exportación CSV Enriquecida
**Archivo:** `app.py` líneas ~1889-1908  
**Cambios:**
- Nueva columna `tiempo_respuesta` en CSV exportado
- Formato: "X.X horas" o "X días"
- Vacío para propuestas pendientes (sin `responded_at`)

### 4. Tests de Verificación
**Archivo:** `tests/test_response_time.py` (nuevo)  
**Cobertura:**
- Test 1: Respuesta en 2 horas → "2.0 horas" ✅
- Test 2: Respuesta en 1 día → "1 día" ✅
- Test 3: Respuesta en 5 días → "5 días" ✅
- Test 4: Respuesta en 30 minutos → "0.5 horas" ✅
- Test 5: Timestamp inválido → manejo de error ✅

## Código Crítico

### Función de Cálculo (patrón usado en 3 lugares)
```python
if prop.get('responded_at') and prop.get('created_at'):
    try:
        from datetime import datetime
        created = datetime.fromisoformat(str(prop['created_at']))
        responded = datetime.fromisoformat(str(prop['responded_at']))
        delta = responded - created
        hours = delta.total_seconds() / 3600
        if hours < 24:
            st.caption(f"⏱️ Tiempo de respuesta: {hours:.1f} horas")
        else:
            days = delta.days
            st.caption(f"⏱️ Tiempo de respuesta: {days} día{'s' if days > 1 else ''}")
    except Exception:
        pass
```

### Lógica Defensiva
- `try/except` para evitar crashes por timestamps malformados
- Validación de existencia de ambos campos antes de cálculo
- Fallback silencioso (no muestra nada si hay error)

## Impacto UX

### Antes
- Propietario veía fecha de respuesta: "Respondida: 2025-11-15"
- Sin contexto de rapidez/lentitud de respuesta
- CSV sin información de tiempos

### Después
- Propietario ve: "Respondida: 2025-11-15" + "⏱️ Tiempo de respuesta: 3.2 horas"
- Contexto inmediato de eficiencia del arquitecto
- CSV con columna `tiempo_respuesta` para análisis posterior
- Arquitecto puede ver cuánto tardó el cliente en responder

## Métricas de Negocio Habilitadas
1. **Velocidad de respuesta de arquitectos** (KPI de servicio)
2. **Análisis de conversión por tiempo** (¿respuestas rápidas = más aceptaciones?)
3. **Benchmarking entre arquitectos** (top performers en rapidez)
4. **Alertas automáticas** (futuro: notificar si >48h sin respuesta)

## Compatibilidad
- ✅ Propuestas sin `responded_at` (pendientes): no muestra métrica
- ✅ Propuestas legacy sin timestamps: manejo de excepciones
- ✅ Esquema dual (message/price vs proposal_text/estimated_budget): independiente
- ✅ No requiere migración de BD

## Testing Manual Recomendado
1. Crear propuesta demo desde arquitecto
2. Aceptar/rechazar propuesta desde propietario
3. Verificar display de tiempo en ambos paneles
4. Exportar CSV y validar columna `tiempo_respuesta`
5. Probar con propuestas antiguas (pre-métrica) para confirmar graceful degradation

## Próximos Pasos (No Implementados)
- [ ] Filtro por tiempo de respuesta en listado de propuestas
- [ ] Gráfico de distribución de tiempos de respuesta
- [ ] Badge de "Respuesta Rápida" para arquitectos (<24h promedio)
- [ ] Alerta automática por email si propuesta >72h sin responder

## Notas de Producción
- Métrica calculada en runtime (no almacenada en BD)
- Zero overhead en escritura (no modifica INSERT/UPDATE)
- Escalable: cálculo O(1) por propuesta
- Frontend-only enhancement (sin cambios en schema)

---
**Estado:** ✅ Completado y testeado  
**Restore Point:** RESTAURACIONDOMINGO2 (pre-cambios)  
**Archivos Modificados:** `app.py` (3 secciones), `tests/test_response_time.py` (nuevo)
