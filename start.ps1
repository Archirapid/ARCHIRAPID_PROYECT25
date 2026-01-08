# Script de arranque para ARCHIRAPID
# Activa el venv y lanza Streamlit

Write-Host "🚀 Iniciando ARCHIRAPID..." -ForegroundColor Cyan
Write-Host "📦 Activando entorno virtual..." -ForegroundColor Yellow

# Activar venv
& ".\venv\Scripts\Activate.ps1"

Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
Write-Host "🌐 Lanzando Streamlit..." -ForegroundColor Yellow

# Lanzar Streamlit
streamlit run app.py