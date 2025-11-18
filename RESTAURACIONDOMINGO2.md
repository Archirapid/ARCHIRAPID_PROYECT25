# RESTAURACIONDOMINGO2

Fecha: 2025-11-16 (UTC)

## Objetivo
Punto de restauración manual antes de nueva fase (métricas tiempo respuesta propuestas).

## Archivos clave respaldados (se crearán a continuación)
- `backups/app.py.RESTAURACIONDOMINGO2`
- `backups/src_db.py.RESTAURACIONDOMINGO2`
- Este documento: `RESTAURACIONDOMINGO2.md`

## Componentes principales activos
- Motor compatibilidad avanzado (`src/compatibility_engine.py`) integrado en `app.py`.
- CTA contacto arquitecto con fallback y seeding demo.
- Propuestas: envío, aceptación/rechazo, responded_at, filtros, resumen métricas, export CSV.
- Reportes compatibilidad: TXT + HTML.
- Portfolio arquitectos y suscripciones.

## Próximo paso planificado
Añadir métrica tiempo de respuesta (diferencia entre created_at y responded_at) + agregar columna calculada en UI.

## Restauración rápida
Para volver a este estado:
1. Sustituir `app.py` por `backups/app.py.RESTAURACIONDOMINGO2`.
2. Sustituir `src/db.py` por `backups/src_db.py.RESTAURACIONDOMINGO2`.
3. Reiniciar aplicación Streamlit.

## Notas
Este snapshot no incluye la base de datos SQLite. Para backup completo añade copia de `data.db` si es crítico.
Si se añaden migraciones posteriores, revertir manualmente cambios en `ensure_tables()`.
