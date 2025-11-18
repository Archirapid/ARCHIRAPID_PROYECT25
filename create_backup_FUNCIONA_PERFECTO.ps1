#!/usr/bin/env pwsh
# Crear backup FUNCIONA_PERFECTO y etiqueta git

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BACKUP FUNCIONA_PERFECTO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoDir = (Resolve-Path "$scriptDir").Path

Write-Host "📁 Repo: $repoDir" -ForegroundColor Green

Write-Host "[1/4] Ejecutando script Python para crear backup zip (FUNCIONA_PERFECTO)..." -ForegroundColor Yellow
python "$repoDir/backups/create_backup_FUNCIONA_PERFECTO.py"

if (-not (Test-Path "$repoDir/backups/FUNCIONA_PERFECTO.zip")) {
    Write-Host "❌ No se creó el zip de backup" -ForegroundColor Red
    exit 1
}

Write-Host "[2/4] Añadiendo tag git: FUNCIONA_PERFECTO" -ForegroundColor Yellow
Set-Location $repoDir
if (Test-Path ".git") {
    git add .
    $status = git status --porcelain
    if ($status) {
        git commit -m "✨ Backup FUNCIONA_PERFECTO - snapshot" -q
    }
    # Create or update annotated tag
    git tag -f -a "FUNCIONA_PERFECTO" -m "Punto de restauración FUNCIONA_PERFECTO" 2>$null
    Write-Host "✅ Tag creado: FUNCIONA_PERFECTO" -ForegroundColor Green
} else {
    Write-Host "⚠️  Repositorio Git no encontrado; solo creamos ZIP" -ForegroundColor Yellow
}

Write-Host "[3/4] Subiendo tag y backup al remoto (si existe)" -ForegroundColor Yellow
try {
    $remote = git remote -v | Select-String "origin"
    if ($remote) {
        git push origin FUNCIONA_PERFECTO 2>&1 | Out-Null
        Write-Host "✅ Tag FUNCIONA_PERFECTO enviado al remoto" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No hay remoto origin configurado, tag no subido" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Error al subir tag (no crítico): $_" -ForegroundColor Yellow
}

Write-Host "[4/4] Copia de seguridad del zip en D: (opcional)" -ForegroundColor Yellow
$destDir = "D:\ARCHIRAPID_BACKUPS"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
}
Copy-Item "$repoDir\backups\FUNCIONA_PERFECTO.zip" -Destination "$destDir\FUNCIONA_PERFECTO.zip" -Force
Write-Host "✅ Copia del zip creada en: $destDir\FUNCIONA_PERFECTO.zip" -ForegroundColor Green

Write-Host "\n✅ BACKUP FUNCIONA_PERFECTO: COMPLETADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
