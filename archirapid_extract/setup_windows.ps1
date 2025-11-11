# ============================================
# ArchiRapid Extract - Setup Automático (Windows)
# ============================================
# Ejecuta este script en PowerShell desde la carpeta archirapid_extract/
# Si tienes error de ejecución, ejecuta primero:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Write-Host "🚀 ArchiRapid Extract - Configuración del entorno" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# 1) Verificar Python
Write-Host "1️⃣  Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python no encontrado. Instala Python 3.8+ desde python.org" -ForegroundColor Red
    exit 1
}

# 2) Crear entorno virtual
Write-Host ""
Write-Host "2️⃣  Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  venv ya existe, saltando creación" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   ✅ Entorno virtual creado" -ForegroundColor Green
}

# 3) Activar entorno virtual
Write-Host ""
Write-Host "3️⃣  Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "   ✅ Entorno activado" -ForegroundColor Green

# 4) Actualizar pip
Write-Host ""
Write-Host "4️⃣  Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "   ✅ pip actualizado" -ForegroundColor Green

# 5) Instalar dependencias Python
Write-Host ""
Write-Host "5️⃣  Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "   ✅ Dependencias instaladas" -ForegroundColor Green

# 6) Verificar Tesseract OCR
Write-Host ""
Write-Host "6️⃣  Verificando Tesseract OCR..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "   ✅ $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Tesseract NO instalado (requerido para OCR)" -ForegroundColor Red
    Write-Host "   📥 Descarga: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host "   O instala con Chocolatey: choco install tesseract" -ForegroundColor Yellow
}

# 7) Verificar Poppler (opcional)
Write-Host ""
Write-Host "7️⃣  Verificando Poppler (opcional)..." -ForegroundColor Yellow
try {
    $popplerVersion = pdftoppm -v 2>&1 | Select-Object -First 1
    Write-Host "   ✅ Poppler instalado" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Poppler no encontrado (opcional, PyMuPDF es suficiente)" -ForegroundColor Yellow
}

# Resumen final
Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✅ Instalación completada" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Coloca tu PDF catastral como 'Catastro.pdf' en esta carpeta" -ForegroundColor White
Write-Host "  2. Ejecuta el pipeline:" -ForegroundColor White
Write-Host "     python extract_pdf.py" -ForegroundColor Gray
Write-Host "     python ocr_and_preprocess.py" -ForegroundColor Gray
Write-Host "     python vectorize_plan.py" -ForegroundColor Gray
Write-Host "     python compute_edificability.py" -ForegroundColor Gray
Write-Host ""
Write-Host "📂 Resultados se guardarán en: catastro_output/" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Si Tesseract no está instalado, instálalo antes de ejecutar el pipeline" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Cyan

