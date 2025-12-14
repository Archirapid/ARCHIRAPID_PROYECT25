Write-Output "Validando servicios ARCHIRAPID..."
Write-Output "========================================"

# Procesos
$procs = Get-Process | Where-Object { $_.ProcessName -match "uvicorn|python|streamlit" }
if ($procs) {
    $procs | ForEach-Object { Write-Output ("Proceso activo: " + $_.ProcessName) }
} else {
    Write-Output "No se encontraron procesos de backend/frontend corriendo"
}

# Backend
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 3
    Write-Output "✅ Backend responde en :8000"
} catch {
    Write-Output "❌ Backend no responde en :8000"
}

# Frontend
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:8501" -UseBasicParsing -TimeoutSec 3
    if ($frontend.Content -match "ARCHIRAPID") {
        Write-Output "✅ Frontend responde y carga ARCHIRAPID"
    } else {
        Write-Output "⚠️ Frontend responde pero no carga ARCHIRAPID"
    }
} catch {
    Write-Output "❌ Frontend no responde en :8501"
}

Write-Output "========================================"
Write-Output "Validacion completada"
