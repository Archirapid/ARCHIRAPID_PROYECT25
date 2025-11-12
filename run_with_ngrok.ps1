# run_with_ngrok.ps1
# Script para ejecutar ARCHIRAPID con acceso remoto via ngrok

Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 ARCHIRAPID - Acceso Remoto con ngrok            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Paso 1: Verificar ngrok instalado
Write-Host "📋 Paso 1: Verificando ngrok..." -ForegroundColor Yellow
$ngrokInstalled = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokInstalled) {
    Write-Host "❌ ngrok no está instalado. Instalando..." -ForegroundColor Red
    winget install Ngrok.Ngrok
    Write-Host "✅ ngrok instalado. Reinicia PowerShell y ejecuta este script de nuevo." -ForegroundColor Green
    exit
}
Write-Host "✅ ngrok instalado`n" -ForegroundColor Green

# Paso 2: Verificar token configurado
Write-Host "📋 Paso 2: Verificando token de ngrok..." -ForegroundColor Yellow
$ngrokConfigPath = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (-not (Test-Path $ngrokConfigPath)) {
    Write-Host "⚠️  No tienes token configurado.`n" -ForegroundColor Yellow
    Write-Host "Haz lo siguiente:" -ForegroundColor Cyan
    Write-Host "1. Ve a: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "2. Copia tu token" -ForegroundColor White
    Write-Host "3. Ejecuta: ngrok config add-authtoken TU_TOKEN`n" -ForegroundColor White
    Start-Process "https://dashboard.ngrok.com/get-started/your-authtoken"
    Write-Host "Cuando tengas el token configurado, ejecuta este script de nuevo.`n" -ForegroundColor Yellow
    exit
}
Write-Host "✅ Token configurado`n" -ForegroundColor Green

# Paso 3: Iniciar Streamlit
Write-Host "📋 Paso 3: Iniciando Streamlit..." -ForegroundColor Yellow
$streamlitJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\python.exe" -m streamlit run app.py --server.port 8510 --server.headless true
}

Start-Sleep -Seconds 5
Write-Host "✅ Streamlit iniciado`n" -ForegroundColor Green

# Paso 4: Iniciar ngrok
Write-Host "📋 Paso 4: Iniciando túnel ngrok..." -ForegroundColor Yellow
Write-Host "Conectando al puerto 8510...`n" -ForegroundColor Cyan

$ngrokJob = Start-Job -ScriptBlock {
    ngrok http 8510
}

Start-Sleep -Seconds 3

# Obtener URL pública
Write-Host "🔍 Obteniendo URL pública..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $publicUrl = $ngrokApi.tunnels[0].public_url
    
    Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ ARCHIRAPID ACCESIBLE DESDE CUALQUIER LUGAR       ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "🌐 URL PÚBLICA:" -ForegroundColor Cyan
    Write-Host "   $publicUrl`n" -ForegroundColor Yellow -BackgroundColor Black
    
    Write-Host "📱 Accede desde:" -ForegroundColor Cyan
    Write-Host "   ✅ Tu móvil (abre el navegador y pega la URL)" -ForegroundColor White
    Write-Host "   ✅ Cualquier PC en el mundo" -ForegroundColor White
    Write-Host "   ✅ Compartir con clientes/colegas`n" -ForegroundColor White
    
    Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "   - NO cierres esta ventana de PowerShell" -ForegroundColor White
    Write-Host "   - La URL funciona mientras este script esté corriendo" -ForegroundColor White
    Write-Host "   - Presiona Ctrl+C para detener todo`n" -ForegroundColor White
    
    Write-Host "📊 Panel de ngrok: http://localhost:4040`n" -ForegroundColor Cyan
    
    # Mantener script corriendo
    Write-Host "Presiona Ctrl+C para detener..." -ForegroundColor Yellow
    Wait-Job $ngrokJob
    
} catch {
    Write-Host "❌ No se pudo obtener la URL. Verifica que ngrok esté corriendo." -ForegroundColor Red
    Write-Host "Abre http://localhost:4040 para ver el panel de ngrok`n" -ForegroundColor Yellow
}

# Cleanup
Stop-Job $streamlitJob -ErrorAction SilentlyContinue
Stop-Job $ngrokJob -ErrorAction SilentlyContinue
Remove-Job $streamlitJob -ErrorAction SilentlyContinue
Remove-Job $ngrokJob -ErrorAction SilentlyContinue
