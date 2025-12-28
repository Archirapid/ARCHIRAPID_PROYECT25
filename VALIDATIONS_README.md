# Validaciones ARCHIRAPID - Windows

Este directorio contiene scripts de validación para Windows PowerShell que reemplazan los comandos Unix tradicionales.

## Uso

### Validar servicios
```powershell
# Desde PowerShell en el directorio del proyecto
.\validate_services.ps1
```

O desde cmd:
```cmd
powershell -ExecutionPolicy Bypass -File validate_services.ps1
```

## Qué valida

1. **Procesos corriendo**: Busca procesos de uvicorn (backend) y streamlit (frontend)
2. **Backend health**: Verifica que responda en `http://localhost:8000/health`
3. **Frontend health**: Verifica que responda en `http://localhost:8501` y contenga "ARCHIRAPID"

## Salida esperada

```
Validando servicios ARCHIRAPID...
========================================
Procesos relacionados:
  python (PID: 1234)
  python (PID: 5678)

Backend responde en :8000
Frontend responde y carga ARCHIRAPID
========================================
Validacion completada
```

## Notas

- Reemplaza comandos Unix como `grep`, `curl`, `ps aux` por equivalentes PowerShell
- Usa `Invoke-WebRequest` en lugar de `curl`
- Compatible con Windows 10/11
- No requiere instalación adicional