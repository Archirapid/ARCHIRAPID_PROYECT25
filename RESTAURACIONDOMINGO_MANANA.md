# Punto de Restauración: RESTAURACIONDOMINGO MAÑANA

Fecha: 2025-11-16
Commit: b64d0fd (main)

Resumen de estado estable:
- Fix crítico de modales anidados en pago de suscripción de arquitectos (se evita StreamlitAPIException por dialogs anidados).
- Flujo post-pago: confirmación y recibo fuera de cualquier modal, con botón de descarga PDF.
- UX: Ocultar "➕ Nuevo Proyecto" solo en el primer render tras pago y mostrar aviso/guía para ir a "📂 Mis Proyectos".
- Exclusividad de modales en "Mis Proyectos" (no se pueden abrir al mismo tiempo "crear" y "detalle").
- Avisos de accesibilidad: radios sin etiqueta convertidos a label_visibility='collapsed'.
- Limpieza: se elimina import directo no usado de payment_simulator en `app.py`.

Cómo restaurar este punto:
- Con tag (si existe): `git checkout tags/RESTAURACIONDOMINGO_MANANA`
- Con hash: `git checkout b64d0fd`

Notas:
- Base de datos `data.db` no se versiona; usar backup externo generado con `create_backup.ps1`.
- Este punto está verificado en local con app corriendo en venv de `D:\ARCHIRAPID_PROYECT25\venv`.
